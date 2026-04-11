import chess
import chess.engine

STOCKFISH_PATH = "/Users/kushagra/Downloads/stockfish/stockfish-macos-m1-apple-silicon"

def main():
    # creates a new chess board in the normal starting position
    board = chess.Board()
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except FileNotFoundError:
        print("Stockfish not found. Check your STOCKFISH_PATH.")
        return

    side = input("Are you playing as White or Black? ").strip().lower()
    if side == "white":
        user_color = chess.WHITE
    elif side == "black":
        user_color = chess.BLACK
    else:
        print("Please type 'White' or 'Black'.")
        engine.quit()
        return

    # instructions for the user
    print("\nEnter moves in normal chess notation.")
    print("Examples: e4, Nf3, Bb5, O-O, exd5, Qxd4")
    print("Type 'quit' to stop.\n")

    # keeps running until the game has ended
    while not board.is_game_over():

        # only gives a suggestion when it is your turn to move
        if board.turn == user_color:
            # asks Stockfish for the best move in the current position
            result = engine.play(board, chess.engine.Limit(time=0.5))
            # converts Stockfish's move into normal chess notation
            suggested_move = board.san(result.move)
            print("Suggested move:", suggested_move)

        # works out whose turn it currently is, just to make the input clearer
        turn_name = "White" if board.turn == chess.WHITE else "Black"

        # asks you to type the move that was actually played on the board
        move_text = input(f"Enter {turn_name}'s move played: ").strip()

        # lets you exit the program manually
        if move_text.lower() == "quit":
            break

        try:
            # reads the move in standard algebraic notation and plays it on the virtual board
            board.push_san(move_text)
        except ValueError:
            # this happens if the move is invalid or illegal in the current position
            print("Invalid or illegal move. Try again.\n")

    # once the game is over, show the result
    if board.is_game_over():
        print("\nGame over:", board.result())

    engine.quit()

if __name__ == "__main__":
    main()