import os
import random
import copy
import time

# --- Configuration & Colors ---
ROWS = 6
COLS = 7
PLAYER_PIECE = 'X'  # Red
AI_PIECE = 'O'      # Yellow
EMPTY = ' '

COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_RESET = '\033[0m'

def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n  0   1   2   3   4   5   6")
    print("+---+---+---+---+---+---+---+")
    for row in board:
        line = "|"
        for cell in row:
            if cell == PLAYER_PIECE:
                line += f" {COLOR_RED}{cell}{COLOR_RESET} |"
            elif cell == AI_PIECE:
                line += f" {COLOR_YELLOW}{cell}{COLOR_RESET} |"
            else:
                line += f" {cell} |"
        print(line)
        print("+---+---+---+---+---+---+---+")

def get_valid_columns(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def drop_piece(board, col, piece):
    for r in reversed(range(ROWS)):
        if board[r][col] == EMPTY:
            board[r][col] = piece
            return r, col
    return None

def check_win(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == piece for i in range(4)): return True
    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r+i][c] == piece for i in range(4)): return True
    # Diagonals
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)): return True
        for c in range(3, COLS):
            if all(board[r+i][c-i] == piece for i in range(4)): return True
    return False

# --- AI Engines ---

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4: score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1: score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2: score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1: score -= 80 # Heavy penalty for letting player win
    return score

def score_position(board, piece):
    score = 0
    # Prefer center column
    center_array = [board[r][COLS//2] for r in range(ROWS)]
    score += center_array.count(piece) * 3
    # Horizontal
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS-3):
            score += evaluate_window(row_array[c:c+4], piece)
    # Vertical
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS-3):
            score += evaluate_window(col_array[r:r+4], piece)
    # Diagonals
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
        for c in range(COLS-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_cols = get_valid_columns(board)
    is_terminal = check_win(board, PLAYER_PIECE) or check_win(board, AI_PIECE) or not valid_cols
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if check_win(board, AI_PIECE): return (None, 10000000)
            if check_win(board, PLAYER_PIECE): return (None, -10000000)
            return (None, 0)
        return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -float('inf')
        column = random.choice(valid_cols)
        for col in valid_cols:
            b_copy = copy.deepcopy(board)
            drop_piece(b_copy, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta: break
        return column, value
    else:
        value = float('inf')
        column = random.choice(valid_cols)
        for col in valid_cols:
            b_copy = copy.deepcopy(board)
            drop_piece(b_copy, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta: break
        return column, value

def get_ai_move(board, difficulty):
    valid_cols = get_valid_columns(board)
    if difficulty == "1": # Easy
        return random.choice(valid_cols)
    
    if difficulty == "2": # Medium
        for col in valid_cols: # Can AI win?
            b = copy.deepcopy(board)
            drop_piece(b, col, AI_PIECE)
            if check_win(b, AI_PIECE): return col
        for col in valid_cols: # Must AI block?
            b = copy.deepcopy(board)
            drop_piece(b, col, PLAYER_PIECE)
            if check_win(b, PLAYER_PIECE): return col
        return random.choice(valid_cols)
    
    # Hard
    col, _ = minimax(board, 5, -float('inf'), float('inf'), True)
    return col

# --- Game Loop ---

def main():
    board = create_board()
    print("=== WELCOME TO FIRST TO 4 ===")
    level = ""
    while level not in ["1", "2", "3"]:
        level = input("Choose Difficulty: 1 (Easy), 2 (Medium), 3 (Hard): ")
    
    turn = random.randint(0, 1) # Randomize who starts
    
    while True:
        print_board(board)
        valid_cols = get_valid_columns(board)
        
        if not valid_cols:
            print("It's a Draw!")
            break

        if turn == 0: # Human
            choice = -1
            while choice not in valid_cols:
                try:
                    choice = int(input(f"Your turn ({COLOR_RED}X{COLOR_RESET}) - Pick 0-6: "))
                except ValueError:
                    continue
            drop_piece(board, choice, PLAYER_PIECE)
            if check_win(board, PLAYER_PIECE):
                print_board(board)
                print(f"Congratulations! {COLOR_RED}You win!{COLOR_RESET}")
                break
        else: # AI
            print("AI is thinking...")
            time.sleep(0.5)
            choice = get_ai_move(board, level)
            drop_piece(board, choice, AI_PIECE)
            if check_win(board, AI_PIECE):
                print_board(board)
                print(f"Game Over! {COLOR_YELLOW}AI wins!{COLOR_RESET}")
                break
        
        turn = (turn + 1) % 2

if __name__ == "__main__":
    main()