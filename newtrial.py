import pygame
import numpy as np
import sys
import math
from threading import Timer
import random
import button

pygame.init()
pygame.display.set_caption('Connect4')

def draw_box(screen, font, text_box1, text_box2, text1, text2):
     # Render and display the row and column text
    row_text = font.render("Rows: " , True, (255, 255, 255))
    col_text = font.render("Columns: " , True, (255, 255, 255))
    screen.blit(row_text, (text_box1.x, text_box1.y - 20))
    screen.blit(col_text, (text_box2.x, text_box2.y - 20))
    # Render the text boxes
    pygame.draw.rect(screen, pygame.Color('white'), text_box1)
    pygame.draw.rect(screen, pygame.Color('black'), text_box1, 2)

    pygame.draw.rect(screen, pygame.Color('white'), text_box2)
    pygame.draw.rect(screen, pygame.Color('black'), text_box2, 2)

    # Render the text
    text_surface1 = font.render(text1, True, pygame.Color('black'))
    screen.blit(text_surface1, (text_box1.x + 5, text_box1.y + 5))

    text_surface2 = font.render(text2, True, pygame.Color('black'))
    screen.blit(text_surface2, (text_box2.x + 5, text_box2.y + 5))



def draw_screen():
    screen = pygame.display.set_mode((800, 450))
    boardImg = pygame.image.load('mp4.png')
    screen.blit(boardImg, (0, 0))
    # Load button images
    entr_img = pygame.image.load('entr_btn.png').convert_alpha()

    # Create button instances
    entr_button = button.Button(100, 240, entr_img, 0.45)

    text1 = ''
    text2 = ''

    # Set up the font
    font = pygame.font.Font(None, 32)

    # Set up the text boxes
    text_box1 = pygame.Rect(400, 220, 200, 32)
    text_box2 = pygame.Rect(400, 280, 200, 32)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                # Handle key presses
                if text_box1.collidepoint(pygame.mouse.get_pos()):
                    if event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        text1 += event.unicode
                elif text_box2.collidepoint(pygame.mouse.get_pos()):
                    if event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        text2 += event.unicode
            

        draw_box(screen, font, text_box1, text_box2, text1, text2)

        if entr_button.draw(screen):
            print('Enter')
            print("Value 1:", text1)
            print("Value 2:", text2)
            ROWS = int(text1)
            COLS = int(text2)
            
            # turns
            PLAYER_TURN = 0
            AI_TURN = 1

            # pieces represented as numbers
            PLAYER_PIECE = 1
            AI_PIECE = 2

            # colors for GUI
            BLUE = (0, 0, 255)
            BLACK = (0, 0, 0)
            RED = (255, 0, 0)
            YELLOW = (255, 255, 0)

            # using numpy, create an empty matrix of 6 rows and 7 columns
            def create_board():
                board = np.zeros((ROWS, COLS))
                return board


            # add a piece to a given location, i.e., set a position in the matrix as 1 or 2
            def drop_piece(board, row, col, piece):
                board[row][col] = piece


            # checking that the top row of the selected column is still not filled
            # i.e., that there is still space in the current column
            # note that indexing starts at 0
            def is_valid_location(board, col):
                return board[0][col] == 0


            # checking where the piece will fall in the current column
            # i.e., finding the first zero row in the given column
            def get_next_open_row(board, col):
                for r in range(ROWS-1, -1, -1):
                    if board[r][col] == 0:
                        return r


            # calculating if the current state of the board for player or AI is a win
            def winning_move(board, piece):

                for c in range(COLS-1):
                    for r in range(ROWS-1):
                        if board[r][c] == piece and board[r+1][c] == piece and board[r][c+1] == piece and board[r+1][c+1] == piece :
                            return True


            # visually representing the board using pygame
            # for each position in the matrix the board is either filled with an empty black circle, or a palyer/AI red/yellow circle
            def draw_board(board):
                for c in range(COLS):
                    for r in range(ROWS):
                        pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE ))
                        if board[r][c] == 0:
                            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE/2), int(r* SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), circle_radius)
                        elif board[r][c] == 1:
                            pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE/2), int(r* SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), circle_radius)
                        else :
                            pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE/2), int(r* SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), circle_radius)

                pygame.display.update()


            # evaluate a 'window' of 4 locations in a row based on what pieces it contains
            # the values used can be experimented with
            def evaluate_window(window, piece):
                # by default the oponent is the player
                opponent_piece = PLAYER_PIECE

                # if we are checking from the player's perspective, then the oponent is AI
                if piece == PLAYER_PIECE:
                    opponent_piece = AI_PIECE

                # initial score of a window is 0
                score = 0

                # based on how many friendly pieces there are in the window, we increase the score
                if window.count(piece) == 4:
                    score += 100
                elif window.count(piece) == 3 and window.count(0) == 1:
                    score += 15
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 5

                # or decrese it if the oponent has 3 in a row
                if window.count(opponent_piece) == 3 and window.count(0) == 1:
                    score -= 50 

                return score    


            # scoring the overall attractiveness of a board after a piece has been droppped
            def score_position(board, piece):

                score = 0

                # score center column --> we are prioritizing the central column because it provides more potential winning windows
                center_array = [int(i) for i in list(board[:,COLS//2])]
                center_count = center_array.count(piece)
                score += center_count * 6
                for i in range (ROWS-1):
                    for j in range (COLS-1):
                        window=[]
                        for a in range(2):
                            for b in range(2):
                                window.append(board[i+a][j+b])
                        score += evaluate_window(window,piece)
                return score

            # checking if the given turn or in other words node in the minimax tree is terminal
            # a terminal node is player winning, AI winning or board being filled up
            def is_terminal_node(board):
                return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

        
            # maximizing_palyer is a boolean value that tells whether we are maximizing or minimizing
            # in this implementation, AI is maximizing.
            def minimax(board, depth, alpha, beta, maximizing_player):

                # all valid locations on the board
                valid_locations = get_valid_locations(board)

                # boolean that tells if the current board is terminal
                is_terminal = is_terminal_node(board)

                # if the board is terminal or depth == 0
                # we score the win very high and a draw as 0
                if depth == 0 or is_terminal:
                    if is_terminal: # winning move 
                        if winning_move(board, AI_PIECE):
                            return (None, 10000000)
                        elif winning_move(board, PLAYER_PIECE):
                            return (None, -10000000)
                        else:
                            return (None, 0)
                    # if depth is zero, we simply score the current board
                    else: # depth is zero
                        return (None, score_position(board, AI_PIECE))

                # if we are maximizing
                if maximizing_player:

                    # initial value is what we do not want - negative infinity
                    value = -math.inf

                    # this will be the optimal column. Initially it is random
                    column = random.choice(valid_locations)

                    # for every valid column, we simulate dropping a piece with the help of a board copy
                    # and run the minimax on it with decresed depth and switched player
                    for col in valid_locations:
                        row = get_next_open_row(board, col)
                        b_copy = board.copy()
                        drop_piece(b_copy, row, col, AI_PIECE)
                        # recursive call
                        new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
                        # if the score for this column is better than what we already have
                        if new_score > value:
                            value = new_score
                            column = col
                        # alpha is the best option we have overall
                        alpha = max(value, alpha) 
                        # if alpha (our current move) is greater (better) than beta (opponent's best move), then 
                        # the oponent will never take it and we can prune this branch
                        if alpha >= beta:
                            break

                    return column, value
                
                # same as above, but for the minimizing player
                else: # for thte minimizing player
                    value = math.inf
                    column = random.choice(valid_locations)
                    for col in valid_locations:
                        row = get_next_open_row(board, col)
                        b_copy = board.copy()
                        drop_piece(b_copy, row, col, PLAYER_PIECE)
                        new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
                        if new_score < value:
                            value = new_score
                            column = col
                        beta = min(value, beta) 
                        if alpha >= beta:
                            break
                    return column, value


            # get all columns where a piece can be
            def get_valid_locations(board):
                valid_locations = []
                
                for column in range(COLS):
                    if is_valid_location(board, column):
                        valid_locations.append(column)

                return valid_locations


            # end the game which will close the window eventually
            def end_game():
                global game_over
                game_over = True
                print(game_over)



            # initializing the board
            board = create_board()

            # initially nobody has won yet
            game_over = False

            # initially the game is not over - this is used for GUI quirks
            not_over = True

            #Initially no draw occured
            draw=False

            # initial turn is random
            turn = random.randint(PLAYER_TURN, AI_TURN)

            # initializing pygame
            pygame.init()

            # size of one game location
            SQUARESIZE = 90

            # dimensions for pygame GUI
            width = COLS * SQUARESIZE
            height = (ROWS + 1) * SQUARESIZE
            circle_radius = int(SQUARESIZE/2 - 5)
            size = (width, height)
            screen = pygame.display.set_mode(size)

            # font for win message
            my_font = pygame.font.SysFont("monospace", 55)

            # draw GUI
            draw_board(board)
            pygame.display.update()


            # game loop
            # loop that runs while the game_over variable is false,
            while not game_over:

                for r in range(board.shape[1]):
                    if is_valid_location(board, r):
                        draw=False
                        break
                    draw=True
                if draw:
                    print("Draw")
                    label = my_font.render("DRAWWW!", 1, RED)
                    screen.blit(label, (40, 10))
                    not_over = False
                    t = Timer(3.0, end_game)
                    t.start()

                # for every player event
                for event in pygame.event.get():

                    # if player clses the window
                    if event.type == pygame.QUIT:
                        sys.exit()

                    # if player moves the mouse, their piece moves at the top of the screen
                    if event.type == pygame.MOUSEMOTION and not_over:
                        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                        xpos = pygame.mouse.get_pos()[0]
                        if turn == PLAYER_TURN:
                            pygame.draw.circle(screen, RED, (xpos, int(SQUARESIZE/2)), circle_radius )

                    # if player clicks the button, we drop their piece down
                    if event.type == pygame.MOUSEBUTTONDOWN and not_over:
                        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))

                        # ask for player 1 inupt
                        if turn == PLAYER_TURN:

                            # we assume players will use correct input
                            xpos = event.pos[0] 
                            col = int(math.floor(xpos/SQUARESIZE)) 

                            if is_valid_location(board, col):
                                row = get_next_open_row(board, col)
                                drop_piece(board, row, col, PLAYER_PIECE)
                                if winning_move(board, PLAYER_PIECE):
                                    print("PLAYER 1 WINS!")
                                    label = my_font.render("PLAYER 1 WINS!", 1, RED)
                                    screen.blit(label, (40, 10))
                                    not_over = False
                                    t = Timer(4.0, end_game)
                                    t.start()
                            draw_board(board) 

                            # increment turn by 1
                            turn += 1

                            # this will alternate between 0 and 1 withe very turn
                            turn = turn % 2 

                    pygame.display.update()

                                
                # if its the AI's turn
                if turn == AI_TURN and not game_over and not_over:

                    # the column to drop in is found using minimax
                    col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

                    if is_valid_location(board, col):
                        pygame.time.wait(500)
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, AI_PIECE)
                        if winning_move(board, AI_PIECE):
                            print("PLAYER 2 WINS!")
                            label = my_font.render("PLAYER 2 WINS!", 1, YELLOW)
                            screen.blit(label, (40, 10))
                            not_over = False
                            t = Timer(4.0, end_game)
                            t.start()
                    draw_board(board)    

                    # increment turn by 1
                    turn += 1
                    # this will alternate between 0 and 1 withe very turn
                    turn = turn % 2

        pygame.display.update()

    pygame.quit()

draw_screen()