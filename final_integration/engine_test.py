from engine import ChessEngine, ChessBoardUI
import pygame


ENGINE_PATH = "/usr/games/stockfish"   # change if needed


def main():

    engine = ChessEngine(ENGINE_PATH)
    ui = ChessBoardUI(engine)

    print("\nControls:")
    print("Type move like: e2e4")
    print("'e' → engine move")
    print("'r' → reset")
    print("'q' → quit")

    running = True

    while running:

        # -----------------------
        # UI UPDATE
        # -----------------------
        if not ui.handle_events():
            break

        ui.update()

        # -----------------------
        # NON-BLOCKING INPUT
        # -----------------------
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:

                # -----------------------
                # ENGINE MOVE
                # -----------------------
                if event.key == pygame.K_e:

                    move = engine.get_best_move()

                    from_sq, to_sq = engine.move_to_squares(move)

                    print("Engine:", from_sq, "->", to_sq)

                    if engine.is_capture(move):
                        print("Capture move")

                    engine.apply_engine_move(move)

                # -----------------------
                # RESET
                # -----------------------
                elif event.key == pygame.K_r:

                    engine = ChessEngine(ENGINE_PATH)
                    ui.engine = engine
                    print("Game reset")

                # -----------------------
                # QUIT
                # -----------------------
                elif event.key == pygame.K_q:
                    running = False

        # -----------------------
        # TERMINAL INPUT (HUMAN MOVE)
        # -----------------------
        try:
            move = input("Your move: ")

            if move == "":
                continue

            if move == "q":
                break

            if len(move) != 4:
                print("Invalid format")
                continue

            from_sq = move[:2]
            to_sq = move[2:]

            if engine.apply_move_uci(from_sq, to_sq):
                print("Move applied")
            else:
                print("Illegal move")

        except:
            pass

    engine.close()
    pygame.quit()


if __name__ == "__main__":
    main()