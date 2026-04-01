# chess_logic.py

class ChessLogic:

    def __init__(self):
        self.board = {}
        self.move_index = 0
        self.init_board()


    def init_board(self):

        files = "abcdefgh"

        for f in files:
            for r in range(1,9):
                self.board[f"{f}{r}"] = None

        # white
        self.board.update({
            "a1":"R","b1":"N","c1":"B","d1":"Q","e1":"K","f1":"B","g1":"N","h1":"R"
        })

        for f in files:
            self.board[f"{f}2"] = "P"

        # black
        self.board.update({
            "a8":"r","b8":"n","c8":"b","d8":"q","e8":"k","f8":"b","g8":"n","h8":"r"
        })

        for f in files:
            self.board[f"{f}7"] = "p"


    def apply_move(self, from_sq, to_sq):

        piece = self.board.get(from_sq)

        if piece is None:
            print("Invalid move: no piece at", from_sq)
            return False

        self.board[to_sq] = piece
        self.board[from_sq] = None

        self.move_index += 1

        return True


    def generate_fen(self):

        fen = ""
        files = "abcdefgh"

        for rank in range(8,0,-1):

            empty = 0

            for file in files:

                piece = self.board[f"{file}{rank}"]

                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += piece

            if empty > 0:
                fen += str(empty)

            if rank > 1:
                fen += "/"

        turn = "w" if self.move_index % 2 == 0 else "b"

        fen += " " + turn + " - - 0 1"

        return fen