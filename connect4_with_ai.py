import math
import random
import sys

import numpy as np
import pygame

BLUE_COLOR = (0, 0, 255)
BLACK_COLOR = (0, 0, 0)
RED_COLOR = (255, 0, 0)
YELLOW_COLOR = (255, 255, 0)
WHITE_COLOR = (255, 255, 255)
ROWS = 6
COLUMNS = 7
PLAYER_ID = 0
AI_ID = 1
EMPTY_SLOT = 0
PLAYER_PIECE_ID = 1
AI_PIECE_ID = 2
WINDOW_LENGTH = 4
SQUARE_SIZE = 100
BOARD_WIDTH = COLUMNS * SQUARE_SIZE
BOARD_HEIGHT = (ROWS + 1) * SQUARE_SIZE
SCREEN_SIZE = (BOARD_WIDTH, BOARD_HEIGHT)
RADIUS = int(SQUARE_SIZE / 2 - 5)


def initialize_board():
    board = np.zeros((ROWS, COLUMNS))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROWS - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == 0:
            return r


def display_board(board):
    print(np.flip(board, 0))


def is_winning_move(board, piece):
    for c in range(COLUMNS - 3):
        for r in range(ROWS):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    for c in range(COLUMNS - 3):
        for r in range(ROWS - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    for c in range(COLUMNS - 3):
        for r in range(3, ROWS):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True


def evaluate_window(window, piece):
    score = 0
    opponent_piece = PLAYER_PIECE_ID
    if piece == PLAYER_PIECE_ID:
        opponent_piece = AI_PIECE_ID

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY_SLOT) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY_SLOT) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(EMPTY_SLOT) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0

    center_column = [int(i) for i in list(board[:, COLUMNS // 2])]
    center_count = center_column.count(piece)
    score += center_count * 3

    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMNS - 3):
            window = row_array[c : c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMNS):
        column_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = column_array[r : r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return (
        is_winning_move(board, PLAYER_PIECE_ID)
        or is_winning_move(board, AI_PIECE_ID)
        or len(get_valid_locations(board)) == 0
    )


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if is_winning_move(board, AI_PIECE_ID):
                return (None, 100000000000000)
            elif is_winning_move(board, PLAYER_PIECE_ID):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE_ID))
    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, AI_PIECE_ID)
            new_score = minimax(board_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, PLAYER_PIECE_ID)
            new_score = minimax(board_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def choose_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col


def draw_board(board, screen):
    for c in range(COLUMNS):
        for r in range(ROWS):
            pygame.draw.rect(
                screen,
                BLUE_COLOR,
                (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )
            pygame.draw.circle(
                screen,
                WHITE_COLOR,
                (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                    int(r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COLUMNS):
        for r in range(ROWS):
            if board[r][c] == PLAYER_PIECE_ID:
                pygame.draw.circle(
                    screen,
                    RED_COLOR,
                    (
                        int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                        BOARD_HEIGHT - int(r * SQUARE_SIZE + SQUARE_SIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == AI_PIECE_ID:
                pygame.draw.circle(
                    screen,
                    YELLOW_COLOR,
                    (
                        int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                        BOARD_HEIGHT - int(r * SQUARE_SIZE + SQUARE_SIZE / 2),
                    ),
                    RADIUS,
                )
    pygame.display.update()


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if font.size(current_line + " " + word)[0] < max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def menu_screen(screen):
    menu_font = pygame.font.SysFont("monospace", 30)
    credits_font = pygame.font.SysFont("monospace", 20)
    level_texts = ["Easy", "Medium", "Hard"]
    selected_level = 0

    while True:
        screen.fill(WHITE_COLOR)
        title_label = menu_font.render("Connect 4", 1, BLACK_COLOR)
        screen.blit(title_label, (BOARD_WIDTH // 2 - title_label.get_width() // 2, 100))

        for i, level_text in enumerate(level_texts):
            level_label = menu_font.render(level_text, 1, BLACK_COLOR)
            if i == selected_level:
                pygame.draw.rect(
                    screen,
                    BLUE_COLOR,
                    (
                        BOARD_WIDTH // 2 - level_label.get_width() // 2,
                        200 + i * 50,
                        level_label.get_width(),
                        level_label.get_height(),
                    ),
                )
            screen.blit(
                level_label,
                (BOARD_WIDTH // 2 - level_label.get_width() // 2, 200 + i * 50),
            )
        credits_text = "By: Max Dann, Trenton Whillans, Jacob Manangan, Hussain Phalasiya, and Jaydon Venderkoen"
        credits_lines = wrap_text(credits_text, credits_font, BOARD_WIDTH - 40)
        credits_height = 200 + len(level_texts) * 50 + 20
        for line in credits_lines:
            credits_label = credits_font.render(line, 1, BLACK_COLOR)
            screen.blit(
                credits_label,
                (BOARD_WIDTH // 2 - credits_label.get_width() // 2, credits_height),
            )
            credits_height += credits_label.get_height() + 5
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = (selected_level - 1) % len(level_texts)
                elif event.key == pygame.K_DOWN:
                    selected_level = (selected_level + 1) % len(level_texts)
                elif event.key == pygame.K_RETURN:
                    return selected_level


def main():
    board = initialize_board()
    display_board(board)
    game_over = False

    pygame.init()
    pygame.display.set_caption("Connect 4 AI Game For CP468")

    screen = pygame.display.set_mode(SCREEN_SIZE)
    selected_level = menu_screen(screen)
    print(f"Selected level: {selected_level}")
    draw_board(board, screen)
    pygame.display.update()

    myfont = pygame.font.SysFont("monospace", 75)

    turn = random.randint(PLAYER_ID, AI_ID)

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, WHITE_COLOR, (0, 0, BOARD_WIDTH, SQUARE_SIZE))
                posx = event.pos[0]
                if turn == PLAYER_ID:
                    pygame.draw.circle(
                        screen, RED_COLOR, (posx, int(SQUARE_SIZE / 2)), RADIUS
                    )

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, WHITE_COLOR, (0, 0, BOARD_WIDTH, SQUARE_SIZE))
                if turn == PLAYER_ID:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARE_SIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE_ID)

                        if is_winning_move(board, PLAYER_PIECE_ID):
                            label = myfont.render("Player 1 wins!!", 1, BLACK_COLOR)
                            screen.blit(label, (40, 10))
                            game_over = True

                        turn += 1
                        turn = turn % 2

                        display_board(board)
                        draw_board(board, screen)

        if turn == AI_ID and not game_over:
            if selected_level == 0:
                print("RANDOM MOVE")
                col = random.randint(0, COLUMNS - 1)
            elif selected_level == 1:
                print("RULES-BASED MOVE")
                col = random.randint(0, COLUMNS - 1)
            else:
                print("MINIMAX MOVE")
                col, _ = minimax(board, 5, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE_ID)

                if is_winning_move(board, AI_PIECE_ID):
                    label = myfont.render("Player 2 wins!!", 1, BLACK_COLOR)
                    screen.blit(label, (40, 10))
                    game_over = True

                display_board(board)
                draw_board(board, screen)

                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)


if __name__ == "__main__":
    main()
