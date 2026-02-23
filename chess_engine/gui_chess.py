import pygame
import chess
import threading

WIDTH, HEIGHT = 640, 700   # Extra space for feedback text
SQ_SIZE = WIDTH // 8

pieces = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙"
}


class ChessGUI:

    def __init__(self, game, llm, feedback_window, tts):
        pygame.init()
        self.feedback_window = feedback_window
        self.tts = tts
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess vs Engine")

        self.game = game
        self.llm = llm

        self.font = pygame.font.SysFont("dejavusans", 60)
        self.small_font = pygame.font.SysFont("dejavusans", 20)

        self.selected_square = None
        self.feedback_text = ""

    # -------------------------
    # Drawing
    # -------------------------

    def draw_board(self):
        colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
        for rank in range(8):
            for file in range(8):
                color = colors[(rank + file) % 2]
                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(file * SQ_SIZE,
                                rank * SQ_SIZE,
                                SQ_SIZE, SQ_SIZE)
                )

    def draw_pieces(self):
        board = self.game.get_board()

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                symbol = pieces[piece.symbol()]
                file = chess.square_file(square)
                rank = 7 - chess.square_rank(square)

                color = pygame.Color("white") if piece.color else pygame.Color("black")

                text = self.font.render(symbol, True, color)
                rect = text.get_rect(center=(
                    file * SQ_SIZE + SQ_SIZE // 2,
                    rank * SQ_SIZE + SQ_SIZE // 2
                ))

                self.screen.blit(text, rect)

    def draw_feedback(self):
        if self.feedback_text:
            text_surface = self.small_font.render(
                self.feedback_text,
                True,
                pygame.Color("black")
            )
            self.screen.blit(text_surface, (10, WIDTH + 10))

    # -------------------------
    # LLM Thread
    # -------------------------

    def generate_feedback_async(self, analysis):
        def worker():
            feedback = self.llm.generate_feedback(analysis)

            # Update text window
            self.feedback_window.root.after(
                0,
                self.feedback_window.update_text,
                feedback
            )

            # Speak it
            self.tts.speak_async(feedback)

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------
    # Main Loop
    # -------------------------

    def run(self):
        running = True

        while running:
            self.draw_board()
            self.draw_pieces()
            self.draw_feedback()
            pygame.display.flip()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    board = self.game.get_board()

                    if board.turn != chess.WHITE:
                        continue

                    x, y = pygame.mouse.get_pos()

                    # Ignore clicks below board area
                    if y > WIDTH:
                        continue

                    file = x // SQ_SIZE
                    rank = 7 - (y // SQ_SIZE)
                    square = chess.square(file, rank)

                    # -----------------
                    # Selecting piece
                    # -----------------
                    if self.selected_square is None:
                        piece = board.piece_at(square)
                        if piece and piece.color == chess.WHITE:
                            self.selected_square = square

                    # -----------------
                    # Attempt move
                    # -----------------
                    else:
                        move = chess.Move(self.selected_square, square)

                        if move in board.legal_moves:

                            # 1️⃣ Analyze BEFORE pushing
                            analysis = self.game.analyze_move(move)

                            # 2️⃣ Push player move
                            board.push(move)

                            # 3️⃣ LLM feedback (async)
                            self.generate_feedback_async(analysis)

                            # 4️⃣ Engine move
                            self.game.make_engine_move()

                        self.selected_square = None

        pygame.quit()
        self.game.close()