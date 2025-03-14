import chess
import chess.engine
import chess.pgn
import matplotlib.pyplot as plt

# Initialize Stockfish engine (update the path with your engine executable)
engine_path = "path/to/engine/..."
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

def load_game_from_pgn(pgn_path):
    """
    Load a chess game from a PGN file.
    
    :param pgn_path: The file path to the PGN file.
    :return: A chess.pgn.Game object representing the loaded game.
    """
    with open(pgn_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    return game

# Set the PGN file path
pgn_path = "path/to/pgn/..."

# Ask the user which color they played (white or black) for proper evaluation display.
color_input = input("Did you play as white or black? ('w' or 'b'): ") or "w"
if color_input.lower() == 'w':
    my_color = chess.WHITE
elif color_input.lower() == 'b':
    my_color = chess.BLACK
else:
    print("Invalid input, using white as default.")
    my_color = chess.WHITE

def get_evaluation_str(pov_score, my_color):
    """
    Converts a PovScore object to a formatted string from the perspective of the given color.
    
    This function only formats the engine evaluation and does not affect the underlying calculations.
    
    :param pov_score: The evaluation score from the engine.
    :param my_color: The player's color (chess.WHITE or chess.BLACK).
    :return: A string representing the evaluation (e.g., "+24" or "Mate").
    """
    # Convert score to the player's point of view
    score_converted = pov_score.white() if my_color == chess.WHITE else pov_score.black()
    cp = score_converted.score(mate_score=10000)
    if cp is None:
        return "Mate"
    # Add a plus sign if the score is positive
    sign = "+" if cp >= 0 else ""
    return f"{sign}{cp}"

def average_evaluation(board, my_color, times, limit):
    """
    Evaluate the current board position 'times' times using the given analysis limit,
    and return the average evaluation (in centipawns) from the perspective of my_color.
    
    :param board: The chess.Board object representing the current position.
    :param my_color: The player's color (chess.WHITE or chess.BLACK).
    :param times: The number of times to run the analysis.
    :param limit: The analysis limit (e.g., time or depth).
    :return: The average evaluation score.
    """
    evaluations = []
    for _ in range(times):
        # Use a copy of the board to preserve the original position
        b = board.copy()
        result = engine.analyse(b, limit)
        # Get the score from the player's perspective
        score_converted = result["score"].white() if my_color == chess.WHITE else result["score"].black()
        cp_value = score_converted.score(mate_score=10000)
        if cp_value is None:
            cp_value = 10000  # Handling mate scenarios by using a large fixed value
        evaluations.append(cp_value)
    # Return the average of the collected evaluations
    return sum(evaluations) / times

def format_eval_value(cp_value):
    """
    Format a centipawn evaluation value into a string, adding a plus sign for positive values.
    
    :param cp_value: The evaluation score in centipawns.
    :return: A formatted string representation of the score.
    """
    sign = "+" if cp_value >= 0 else ""
    return f"{sign}{int(cp_value)}"

def analyze_game_table_and_plot(game, my_color, times, limit):
    """
    Analyze the game move-by-move, print a table of evaluations and plot the evaluation graph.
    
    For every pair of moves (white and black), the function:
      - Calculates the average evaluation using the chosen parameters.
      - Prints a table line with the move number, white move notation, evaluation, black move notation, and evaluation.
      - Collects the evaluations and ply numbers to generate a graph showing the evaluation trend throughout the game.
    
    :param game: The chess.pgn.Game object.
    :param my_color: The player's color.
    :param times: The number of evaluations to average per move.
    :param limit: The analysis limit (e.g., time or depth).
    """
    board = game.board()
    moves = list(game.mainline_moves())
    move_number = 1
    ply_numbers = []     # List to store the half-move (ply) numbers for plotting
    evaluations = []     # List to store evaluation scores (in centipawns)
    ply = 1           
    
    # Process moves in pairs: one white move and one black move
    for i in range(0, len(moves), 2):
        # White's move
        white_move = moves[i]
        # Get the move notation before making the move on the board
        white_notation = board.san(white_move)
        board.push(white_move)
        # Evaluate the position after white's move
        avg_eval_white = average_evaluation(board, my_color, times, limit)
        eval_white = format_eval_value(avg_eval_white)
        evaluations.append(avg_eval_white)
        ply_numbers.append(ply)
        ply += 1
        
        # If black has made a move in this turn, evaluate it as well
        if i + 1 < len(moves):
            black_move = moves[i+1]
            black_notation = board.san(black_move)
            board.push(black_move)
            avg_eval_black = average_evaluation(board, my_color, times, limit)
            eval_black = format_eval_value(avg_eval_black)
            evaluations.append(avg_eval_black)
            ply_numbers.append(ply)
            ply += 1
        else:
            black_notation = ""
            eval_black = ""
        
        # Print the move number, white's move and evaluation, black's move and evaluation
        print(f"{move_number}. | {white_notation} | {eval_white} | {black_notation} | {eval_black} |")
        move_number += 1

    # Generate a graph of the evaluation over the course of the game
    plt.figure(figsize=(10, 5))
    plt.plot(ply_numbers, evaluations, marker='o', linestyle='-', color='blue')
    plt.xlabel("Half-move (ply) number")
    plt.ylabel("Evaluation (centipawns)")
    plt.title("Evaluation Trend Throughout the Game")
    # Use a symmetric logarithmic scale for better visibility of small and large changes
    plt.yscale('symlog', linthresh=50)
    plt.grid(True, which="both", ls="--")
    plt.show()

def analyze_move_errors(game, my_color, times, limit, threshold=50):
    """
    Analyze move errors for the moves made by the player (my_color).
    
    For each move played by the player:
      - Perform 'times' analyses to obtain:
          * The best move suggested by the engine (using multipv=1) and its evaluation.
          * The evaluation after executing the actual played move.
      - Compute the average absolute difference (error) between the evaluation of the best move and the played move.
      - If the average error is below a given threshold, consider the move "accurate".
      - If the played move does not match the best move and the error is significant,
        print the move number, the played move, the best move, and the average error.
      - At the end, compute and print the overall accuracy (percentage of accurate moves).
    
    :param game: The chess.pgn.Game object.
    :param my_color: The player's color.
    :param times: The number of evaluations to average for each move.
    :param limit: The analysis limit (e.g., time or depth).
    :param threshold: The threshold (in centipawns) under which a move is considered accurate.
    """
    board = game.board()
    player_move_index = 1  # Counter for the player's moves
    total_moves = 0
    accurate_moves = 0

    for move in game.mainline_moves():
        # Only analyze moves when it's the player's turn
        if board.turn == my_color:
            total_moves += 1
            errors = []
            # Get the SAN notation for the played move
            played_move_san = board.san(move)
            best_move_san_trial = None  # Will store the best move notation from the first evaluation
            
            # Perform multiple analyses for reliability
            for i in range(times):
                b = board.copy()  # Copy the current board state
                # Get the best move according to the engine (using multipv=1)
                result_best = engine.analyse(b, limit, multipv=1)
                best_line = result_best[0]
                best_move = best_line["pv"][0]
                best_eval = best_line["score"].white() if my_color == chess.WHITE else best_line["score"].black()
                best_eval_value = best_eval.score(mate_score=10000)
                if i == 0:
                    # Save the best move notation from the first evaluation
                    best_move_san_trial = b.san(best_move)
                # Simulate playing the actual move and analyze the resulting position
                b.push(move)
                result_played = engine.analyse(b, limit)
                played_eval = result_played["score"].white() if my_color == chess.WHITE else result_played["score"].black()
                played_eval_value = played_eval.score(mate_score=10000)
                # Compute the absolute error between the best move evaluation and the played move evaluation
                errors.append(abs(best_eval_value - played_eval_value))
            
            # Compute the average error for this move
            avg_error = sum(errors) / len(errors)
            # Consider the move accurate if the average error is below the threshold
            if avg_error < threshold:
                accurate_moves += 1
            # If the played move differs from the best move and the error is significant, print the details
            if played_move_san != best_move_san_trial and avg_error >= threshold:
                print(f"{player_move_index}. {played_move_san} -> {best_move_san_trial}  avg. diff: {int(avg_error)}")
            
            board.push(move)  # Update the main board position by playing the move
            player_move_index += 1
        else:
            board.push(move)
    
    # Calculate and print the overall accuracy (percentage of moves with average error below the threshold)
    if total_moves > 0:
        accuracy_percentage = (accurate_moves / total_moves) * 100
    else:
        accuracy_percentage = 0.0
    print(f"Overall Accuracy: {accuracy_percentage:.2f}%")

def choose_analysis_mode():
    """
    Allow the user to choose the analysis mode:
      1. Fast: 2 seconds, 2 evaluations
      2. In-depth: 5 seconds, 3 evaluations
      3. Very In-depth: depth=20, 3 evaluations
      4. Very Fast: 0.5 seconds, 2 evaluations
    Returns a tuple (times, limit) to be used in the analysis functions.
    
    :return: A tuple (number_of_evaluations, analysis_limit)
    """
    print("Choose the analysis mode:")
    print("1. Fast (2 sec, 2 evaluations)")
    print("2. In-depth (5 sec, 3 evaluations)")
    print("3. Very In-depth (depth=20, 3 evaluations)")
    print("4. Very Fast (0.5 sec, 2 evaluations)")
    mode = input("Enter 1, 2, 3 or 4: ")
    if mode == "1":
        return 2, chess.engine.Limit(time=2)
    elif mode == "2":
        return 3, chess.engine.Limit(time=5)
    elif mode == "3":
        return 3, chess.engine.Limit(depth=20)
    elif mode == "4":
        return 2, chess.engine.Limit(time=0.5)
    else:
        print("Invalid selection. Using 'Very Fast' (0.5 sec, 2 evaluations) by default.")
        return 2, chess.engine.Limit(time=0.5)

# --- Main Execution Flow ---

# Load the game from the PGN file
game = load_game_from_pgn(pgn_path)

# Let the user choose the analysis mode, which returns the number of evaluations and analysis limit
times, limit = choose_analysis_mode()

# Analyze the game: print the evaluation table and plot the evaluation trend graph
print("Evaluation table and graph:")
analyze_game_table_and_plot(game, my_color, times, limit)

# To avoid conflicts (since functions push moves on the board),
# reload the game before analyzing move errors.
game = load_game_from_pgn(pgn_path)
print("\nMove errors analysis:")
analyze_move_errors(game, my_color, times, limit, threshold=50)

# Close the engine once analysis is complete
engine.quit()
