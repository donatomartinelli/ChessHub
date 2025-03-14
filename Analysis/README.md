# Chess Game Analysis Tool

This Python script provides a detailed post-game analysis for chess matches stored in PGN files using the Stockfish engine. It performs the following tasks:

- **Load a PGN Game:**  
  Reads a chess game from a PGN file.

- **Engine Initialization:**  
  Initializes a UCI-compatible chess engine from a specified path.

- **Player Color Input:**  
  Prompts the user to indicate whether they played as white or black. This setting is used to adjust the evaluation displays.

- **Analysis Modes:**  
  Offers several analysis modes with different parameters:
  - **Fast:** 2 seconds per move analysis, 2 evaluations per move.
  - **In-depth:** 5 seconds per move analysis, 3 evaluations per move.
  - **Very In-depth:** Uses a fixed search depth (20 plies) for 3 evaluations.
  - **Very Fast:** 0.5 seconds per move analysis, 2 evaluations per move.

- **Evaluation Table and Graph Generation:**  
  For each pair of moves (white and black), the script:
  - Calculates the average evaluation (in centipawns) after each move.
  - Prints a table with the move number, white move notation, evaluation, black move notation, and evaluation.
  - Generates a graph showing the evaluation trend over the course of the game.

- **Move Error Analysis:**  
  For every move played by the user:
  - Compares the evaluation of the played move with the engine’s best move evaluation.
  - Computes an average error over multiple analyses.
  - Prints moves where the error exceeds a set threshold and calculates the overall accuracy (percentage of moves with an error below the threshold).

- **Engine Shutdown:**  
  Once analysis is complete, the engine is properly closed.

---

## Prerequisites

- **Python 3.x**
- **Libraries:**
  - `python-chess`
  - `matplotlib`
- **Chess Engine:**  
  A UCI-compatible chess engine (e.g., Stockfish). Update the `engine_path` variable accordingly.

---

## Usage

1. **Update Paths:**  
   Modify the `engine_path` and `pgn_path` variables in the script with your own paths.

2. **Run the Script:**  
   Execute the script in a terminal or command prompt.
   
3. **Input Your Data:**  
   - When prompted, specify if you played as white or black by entering `w` or `b`.
   - Choose the desired analysis mode (Fast, In-depth, Very In-depth, or Very Fast).

4. **View Results:**  
   The script will print an evaluation table showing each move with its evaluation, display a graph of the evaluation trend throughout the game, and provide detailed move error analysis including overall accuracy.

---

## Code Overview

- **Loading the Game:**  
  The function `load_game_from_pgn(pgn_path)` opens the specified PGN file and returns the first game.

- **Engine Analysis Functions:**  
  Functions such as `average_evaluation()`, `format_eval_value()`, and `get_evaluation_str()` perform the engine analysis and format the resulting evaluations.

- **Game Analysis and Visualization:**  
  The `analyze_game_table_and_plot(game, my_color, times, limit)` function processes the game move-by-move, prints a table with move notations and evaluations, and generates a graph depicting the evaluation trend over time.

- **Move Error Analysis:**  
  The `analyze_move_errors(game, my_color, times, limit, threshold=50)` function compares the evaluation of each move played by the user against the engine’s best move evaluation, computes the average error, prints moves where the error is significant, and calculates the overall accuracy (percentage of moves with an error below the specified threshold).

- **Analysis Mode Selection:**  
  The `choose_analysis_mode()` function allows the user to select from various analysis modes, returning the number of evaluations and the analysis limit (either time-based or depth-based) to be used in the analysis.

---

## Customization

To generalize file paths, you can modify the script to accept command-line arguments or read from a configuration file. This prevents hardcoding your personal paths in the source code.

---

This tool is designed to help chess enthusiasts review and improve their games by comparing their moves against engine recommendations. Enjoy analyzing your games!

