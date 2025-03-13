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
    Questa operazione è solo di formattazione: il calcolo dell'engine non viene modificato.
    """
    # Se giochi da bianco, converte la valutazione in prospettiva bianca, altrimenti in prospettiva nera.
    score_converted = pov_score.white() if my_color == chess.WHITE else pov_score.black()
    cp = score_converted.score(mate_score=10000)  # Ottiene il punteggio in centipedine
    if cp is None:
        return "Mate"
    # Aggiunge il segno "+" se il valore è positivo
    sign = "+" if cp >= 0 else ""
    return f"{sign}{cp}"

def average_evaluation(board, my_color, times=3, limit=chess.engine.Limit(depth=20)):
    """
    Valuta la posizione della scacchiera 'times' volte e restituisce la media
    del punteggio (in centipedine) dal punto di vista del colore my_color.
    """
    evaluations = []
    for _ in range(times):
        b = board.copy()  # Usa una copia per non alterare la posizione principale
        result = engine.analyse(b, limit)
        score_converted = result["score"].white() if my_color == chess.WHITE else result["score"].black()
        cp_value = score_converted.score(mate_score=10000)
        if cp_value is None:
            cp_value = 10000  # Gestione del mate
        evaluations.append(cp_value)
    return sum(evaluations) / times

def format_eval_value(cp_value):
    """
    Converte il punteggio in centipedine in una stringa formattata,
    aggiungendo il segno "+" se il valore è positivo.
    """
    sign = "+" if cp_value >= 0 else ""
    return f"{sign}{int(cp_value)}"

def analyze_game_table(game, my_color):
    board = game.board()
    moves = list(game.mainline_moves())
    move_number = 1

    for i in range(0, len(moves), 2):
        # Gestione della mossa bianca
        white_move = moves[i]
        white_notation = board.san(white_move)  # Salva la notazione prima di eseguire la mossa
        board.push(white_move)
        # Ottieni la valutazione media eseguendo l'analisi 3 volte
        avg_eval_white_value = average_evaluation(board, my_color, times=3, limit=chess.engine.Limit(depth=20))
        eval_white = format_eval_value(avg_eval_white_value)
        
        # Gestione della mossa nera (se presente)
        if i + 1 < len(moves):
            black_move = moves[i+1]
            black_notation = board.san(black_move)
            board.push(black_move)
            avg_eval_black_value = average_evaluation(board, my_color, times=3, limit=chess.engine.Limit(depth=20))
            eval_black = format_eval_value(avg_eval_black_value)
        else:
            black_notation = ""
            eval_black = ""
        
        print(f"{move_number}. | {white_notation} | {eval_white} | {black_notation} | {eval_black} |")
        move_number += 1

def plot_move_evaluations_graph(game, my_color):
    board = game.board()
    ply_numbers = []
    evaluations = []
    ply = 1
    for move in game.mainline_moves():
        board.push(move)
        result = engine.analyse(board, chess.engine.Limit(depth=20))
        score_converted = result["score"].white() if my_color == chess.WHITE else result["score"].black()
        cp_value = score_converted.score(mate_score=10000)
        if cp_value is None:
            cp_value = 10000
        evaluations.append(cp_value)
        ply_numbers.append(ply)
        ply += 1

    plt.figure(figsize=(10, 5))
    plt.plot(ply_numbers, evaluations, marker='o', linestyle='-', color='blue')
    plt.xlabel("Numero di mezzo-mosse (ply)")
    plt.ylabel("Valutazione (centipedine)")
    plt.title("Andamento della valutazione durante la partita")
    # Usa la scala symlog per migliorare la visibilità delle variazioni
    plt.yscale('symlog', linthresh=50)
    plt.grid(True, which="both", ls="--")
    plt.show()

def analyze_move_errors(game, my_color):
    """
    Per ogni mossa della partita, se il turno corrente corrisponde al tuo colore (my_color),
    valuta la posizione tre volte. Per ciascuna valutazione:
      - Richiede la mossa migliore (con multipv=1) e la sua valutazione.
      - Simula l'esecuzione della mossa giocata e ottiene la valutazione risultante.
      - Calcola la differenza (errore) tra la valutazione della mossa migliore e quella giocata.
    Alla fine, se la mossa giocata non coincide con la migliore e la media degli errori è positiva,
    stampa il numero della mossa, la mossa giocata, la mossa migliore (presa dalla prima valutazione)
    e la media della differenza.
    """
    board = game.board()
    player_move_index = 1  # Contatore per le tue mosse

    for move in game.mainline_moves():
        if board.turn == my_color:
            errors = []
            # Salva la notazione della mossa giocata (prima di eseguire alcun push)
            played_move_san = board.san(move)
            best_move_san_trial = None  # Da utilizzare per l'output (primo campione)
            
            # Esegui tre valutazioni indipendenti sulla stessa posizione
            for i in range(3):
                b = board.copy()  # Copia della posizione attuale
                # Analizza la posizione corrente per ottenere la mossa migliore
                result_best = engine.analyse(b, chess.engine.Limit(depth=20), multipv=1)
                best_line = result_best[0]  # multipv=1 restituisce una lista con un solo elemento
                best_move = best_line["pv"][0]
                best_eval = best_line["score"].white() if my_color == chess.WHITE else best_line["score"].black()
                best_eval_value = best_eval.score(mate_score=10000)
                # Salva la mossa migliore della prima valutazione per l'output
                if i == 0:
                    best_move_san_trial = b.san(best_move)
                
                # Simula l'esecuzione della mossa giocata
                b.push(move)
                result_played = engine.analyse(b, chess.engine.Limit(depth=20))
                played_eval = result_played["score"].white() if my_color == chess.WHITE else result_played["score"].black()
                played_eval_value = played_eval.score(mate_score=10000)
                
                # Calcola l'errore per questa iterazione
                error = best_eval_value - played_eval_value
                errors.append(error)
            
            # Calcola la media degli errori
            avg_error = sum(errors) / len(errors)
            
            # Se la mossa giocata non coincide con la mossa migliore e la media è positiva, stampa l'output
            if played_move_san != best_move_san_trial and avg_error >= 50:
                print(f"{player_move_index}. {played_move_san} -> {best_move_san_trial}  avg. diff: {int(avg_error)}")
            
            board.push(move)  # Aggiorna la posizione sul board principale
            player_move_index += 1
        else:
            board.push(move)

# Carica la partita
game = load_game_from_pgn(pgn_path)

print("Tabella delle valutazioni:")
analyze_game_table(game, my_color)

print("\nGrafico delle valutazioni mossa per mossa:")
plot_move_evaluations_graph(game, my_color)

print("\nAnalisi degli errori mossa per mossa:")
analyze_move_errors(game, my_color)

engine.quit()
