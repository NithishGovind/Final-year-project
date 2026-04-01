import chess
import chess.engine


class ChessEngine:

    def __init__(self, engine_path, think_time=0.5):

        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

        self.think_time = think_time

    # -----------------------
    # APPLY MOVE (FROM VISION OR ROBOT)
    # -----------------------
    def apply_move_uci(self, from_sq, to_sq):

        move = chess.Move.from_uci(from_sq + to_sq)

        if move in self.board.legal_moves:
            self.board.push(move)
            print("Move applied:", move)
            return True

        print("Illegal move:", from_sq, "->", to_sq)
        return False

    # -----------------------
    # GET ENGINE MOVE
    # -----------------------
    def get_best_move(self):

        result = self.engine.play(
            self.board,
            chess.engine.Limit(time=self.think_time)
        )

        move = result.move
        print("Engine move:", move)

        return move

    # -----------------------
    # APPLY ENGINE MOVE
    # -----------------------
    def apply_engine_move(self, move):

        self.board.push(move)

    # -----------------------
    # GET MOVE AS SQUARES
    # -----------------------
    def move_to_squares(self, move):

        uci = move.uci()
        return uci[:2], uci[2:]

    # -----------------------
    # CAPTURE CHECK
    # -----------------------
    def is_capture(self, move):

        return self.board.is_capture(move)

    # -----------------------
    # GAME STATUS
    # -----------------------
    def is_game_over(self):

        return self.board.is_game_over()

    def get_result(self):

        return self.board.result()

    # -----------------------
    # DEBUG / DISPLAY
    # -----------------------
    def print_board(self):
        print(self.board)

    def get_fen(self):
        return self.board.fen()

    # -----------------------
    # CLEANUP
    # -----------------------
    def close(self):
        self.engine.quit()


import pygame


class ChessBoardUI:

    def __init__(self, engine, size=600):

        self.engine = engine
        self.size = size
        self.cell = size // 8

        pygame.init()
        self.screen = pygame.display.set_mode((size, size))
        pygame.display.set_caption("Chess Board")

        # colors
        self.light = (240, 217, 181)
        self.dark = (181, 136, 99)

        # piece font
        self.font = pygame.font.SysFont("Arial", self.cell // 2)

    # -----------------------
    # DRAW BOARD
    # -----------------------
    def draw_board(self):

        for r in range(8):
            for c in range(8):

                color = self.light if (r + c) % 2 == 0 else self.dark

                pygame.draw.rect(
                    self.screen,
                    color,
                    (c * self.cell, r * self.cell, self.cell, self.cell)
                )

    # -----------------------
    # DRAW PIECES
    # -----------------------
    def draw_pieces(self):

        board = self.engine.board

        for square in board.piece_map():

            piece = board.piece_at(square)
            symbol = piece.symbol()

            col = square % 8
            row = 7 - (square // 8)

            text = self.font.render(symbol, True, (0, 0, 0))

            self.screen.blit(
                text,
                (col * self.cell + self.cell // 3,
                 row * self.cell + self.cell // 4)
            )

    # -----------------------
    # UPDATE DISPLAY
    # -----------------------
    def update(self):

        self.draw_board()
        self.draw_pieces()
        pygame.display.flip()

    # -----------------------
    # HANDLE EVENTS
    # -----------------------
    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True