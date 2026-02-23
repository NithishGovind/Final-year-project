import chess
import chess.engine


class ChessGame:
    def __init__(self, engine_path):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def make_player_move(self, from_square, to_square):
        move = chess.Move(from_square, to_square)

        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def make_engine_move(self):
        if not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(time=0.3))
            self.board.push(result.move)
            return result.move
        return None

    def get_board(self):
        return self.board

    def is_game_over(self):
        return self.board.is_game_over()

    def close(self):
        self.engine.quit()

    def analyze_move(self, move, depth=15):

        # Evaluation before
        info_before = self.engine.analyse(
            self.board,
            chess.engine.Limit(depth=depth)
        )
        score_before = info_before["score"].relative.score(mate_score=10000)

        best_move = info_before.get("pv")[0] if "pv" in info_before else None

        # Make move
        self.board.push(move)

        info_after = self.engine.analyse(
            self.board,
            chess.engine.Limit(depth=depth)
        )
        score_after = info_after["score"].relative.score(mate_score=10000)

        self.board.pop()

        delta = (score_after - score_before) / 100.0

        return {
    "played_move": move.uci(),
    "best_move": best_move.uci() if best_move else None,
    "evaluation_change": delta,
    "fen": self.board.fen()}