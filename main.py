import chess
import chess.engine
import chess.pgn
import matplotlib.pyplot as plt

# Inizializza Stockfish (aggiorna il percorso con il tuo eseguibile)
engine_path = "C:/Users/donat/Desktop/Università/Chess/stockfish/stockfish-windows-x86-64.exe"
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

def load_game_from_pgn(pgn_path):
    with open(pgn_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    return game

pgn_path = "C:/Users/donat/Desktop/Università/Chess/Cronologia partite/136227961496-Abdoolah_iraq_vs_donatomartinellii-2025-03-13.pgn"

# Imposta il colore con cui giochi: chess.WHITE o chess.BLACK.
# Questo parametro è usato esclusivamente per la visualizzazione (presentazione) delle valutazioni.
my_color = chess.WHITE

def get_evaluation_str(pov_score, my_color):
    """
    Converte l'oggetto PovScore per visualizzarlo dal punto di vista del colore indicato.
    Operazione puramente di formattazione.
    """
    score_converted = pov_score.white() if my_color == chess.WHITE else pov_score.black()
    cp = score_converted.score(mate_score=10000)
    if cp is None:
        return "Mate"
    sign = "+" if cp >= 0 else ""
    return f"{sign}{cp}"

def average_evaluation(board, my_color, times, limit):
    """
    Valuta la posizione della scacchiera 'times' volte usando il parametro 'limit'
    e restituisce la media del punteggio (in centipedine) dal punto di vista di my_color.
    """
    evaluations = []
    for _ in range(times):
        b = board.copy()  # copia per non alterare la posizione principale
        result = engine.analyse(b, limit)
        score_converted = result["score"].white() if my_color == chess.WHITE else result["score"].black()
        cp_value = score_converted.score(mate_score=10000)
        if cp_value is None:
            cp_value = 10000
        evaluations.append(cp_value)
    return sum(evaluations) / times

def format_eval_value(cp_value):
    """
    Converte il punteggio in centipedine in una stringa formattata,
    aggiungendo il segno "+" se il valore è positivo.
    """
    sign = "+" if cp_value >= 0 else ""
    return f"{sign}{int(cp_value)}"

def analyze_game_table_and_plot(game, my_color, times, limit):
    """
    Per ogni coppia di mosse (bianco e nero) calcola la valutazione media (usando i parametri scelti)
    e stampa la riga della tabella. I dati ottenuti vengono salvati in una lista, poi usata per generare il grafico.
    """
    board = game.board()
    moves = list(game.mainline_moves())
    move_number = 1
    ply_numbers = []     # per il grafico: numero delle mezzo-mosse (ply)
    evaluations = []     # per il grafico: valutazioni (in centipedine)
    ply = 1           
    
    for i in range(0, len(moves), 2):
        # Mossa del bianco
        white_move = moves[i]
        white_notation = board.san(white_move)  # ottieni la notazione prima di eseguire la mossa
        board.push(white_move)
        avg_eval_white = average_evaluation(board, my_color, times, limit)
        eval_white = format_eval_value(avg_eval_white)
        evaluations.append(avg_eval_white)
        ply_numbers.append(ply)
        ply += 1
        
        # Se esiste anche la mossa del nero
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
        
        print(f"{move_number}. | {white_notation} | {eval_white} | {black_notation} | {eval_black} |")
        move_number += 1

    # Creazione del grafico utilizzando i dati calcolati
    plt.figure(figsize=(10, 5))
    plt.plot(ply_numbers, evaluations, marker='o', linestyle='-', color='blue')
    plt.xlabel("Numero di mezzo-mosse (ply)")
    plt.ylabel("Valutazione (centipedine)")
    plt.title("Andamento della valutazione durante la partita")
    plt.yscale('symlog', linthresh=50)
    plt.grid(True, which="both", ls="--")
    plt.show()

def analyze_move_errors(game, my_color, times, limit):
    """
    Per ogni mossa della partita (quando tocca a my_color),
    valuta la posizione 'times' volte:
      - Ottiene la mossa migliore (con multipv=1) e la sua valutazione.
      - Simula l'esecuzione della mossa giocata e ottiene la valutazione risultante.
      - Calcola la differenza (errore) tra le due valutazioni.
    Se la mossa giocata non coincide con la migliore e l'errore medio è significativo,
    stampa il numero della mossa, la mossa giocata, quella migliore e la differenza media.
    """
    board = game.board()
    player_move_index = 1  # Contatore per le mosse di my_color

    for move in game.mainline_moves():
        if board.turn == my_color:
            errors = []
            played_move_san = board.san(move)
            best_move_san_trial = None  # Verrà usata per l'output (primo campione)
            
            for i in range(times):
                b = board.copy()  # Copia della posizione attuale
                # Ottieni la mossa migliore usando i parametri scelti (multipv=1)
                result_best = engine.analyse(b, limit, multipv=1)
                best_line = result_best[0]
                best_move = best_line["pv"][0]
                best_eval = best_line["score"].white() if my_color == chess.WHITE else best_line["score"].black()
                best_eval_value = best_eval.score(mate_score=10000)
                if i == 0:
                    best_move_san_trial = b.san(best_move)
                # Simula l'esecuzione della mossa giocata
                b.push(move)
                result_played = engine.analyse(b, limit)
                played_eval = result_played["score"].white() if my_color == chess.WHITE else result_played["score"].black()
                played_eval_value = played_eval.score(mate_score=10000)
                # Calcola l'errore per questa iterazione
                error = best_eval_value - played_eval_value
                errors.append(error)
            
            avg_error = sum(errors) / len(errors)
            if played_move_san != best_move_san_trial and avg_error >= 50:
                print(f"{player_move_index}. {played_move_san} -> {best_move_san_trial}  avg. diff: {int(avg_error)}")
            
            board.push(move)  # Aggiorna la posizione principale
            player_move_index += 1
        else:
            board.push(move)

def choose_analysis_mode():
    """
    Permette di scegliere la modalità di analisi:
      1. Veloce: 2 sec, 2 valutazioni
      2. Approfondita: 5 sec, 3 valutazioni
      3. Approfonditissima: depth=20, 3 valutazioni
    Ritorna una tupla (times, limit) da usare nelle funzioni.
    """
    print("Scegli il tipo di analisi:")
    print("1. Veloce (2 sec, 2 valutazioni)")
    print("2. Approfondita (5 sec, 3 valutazioni)")
    print("3. Approfonditissima (depth=20, 3 valutazioni)")
    scelta = input("Inserisci 1, 2 o 3: ")
    if scelta == "1":
        return 2, chess.engine.Limit(time=2)
    elif scelta == "2":
        return 3, chess.engine.Limit(time=5)
    elif scelta == "3":
        return 3, chess.engine.Limit(depth=20)
    else:
        print("Scelta non valida. Uso il tipo 'Approfondita' (5 sec, 3 valutazioni).")
        return 3, chess.engine.Limit(time=5)

# Carica la partita
game = load_game_from_pgn(pgn_path)

# Scegli il tipo di analisi
times, limit = choose_analysis_mode()

print("Tabella delle valutazioni e grafico:")
analyze_game_table_and_plot(game, my_color, times, limit)

# Per evitare conflitti (in quanto le funzioni eseguono push sul board),
# ricarichiamo la partita per l'analisi degli errori.
game = load_game_from_pgn(pgn_path)
print("\nAnalisi degli errori mossa per mossa:")
analyze_move_errors(game, my_color, times, limit)

engine.quit()
