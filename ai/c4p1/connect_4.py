#%%
import numpy as np
import random
from termcolor import colored  # can be taken out if you don't like it...

# # # # # # # # # # # # # # global values  # # # # # # # # # # # # # #
ROW_COUNT = 6
COLUMN_COUNT = 7

RED_CHAR = colored('X', 'red')  # RED_CHAR = 'X'
BLUE_CHAR = colored('O', 'blue')  # BLUE_CHAR = 'O'

EMPTY = 0
RED_INT = 1
BLUE_INT = 2


# # # # # # # # # # # # # # functions definitions # # # # # # # # # # # # # #

def create_board():
    """create empty board for new game"""
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=np.int8)
    return board


def drop_chip(board, row, col, chip):
    """place a chip (red or BLUE) in a certain position in board"""
    if row == None: return
    board[row][col] = chip


def is_valid_location(board, col):
    """check if a given row in the board has a room for extra dropped chip"""
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    """assuming column is available to drop the chip,
    the function returns the lowest empty row  """
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    """print current board with all chips put in so far"""
    # print(np.flip(board, 0))
    print(" 1 2 3 4 5 6 7 \n" "|" + np.array2string(np.flip(np.flip(board, 1)))
          .replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_")
          .replace("1", RED_CHAR).replace("2", BLUE_CHAR).replace("\n", "|\n") + "|")


def game_is_won(board, chip):
    """check if current board contain a sequence of 4-in-a-row of in the board
     for the player that play with "chip"  """

    winning_Sequence = np.array([chip, chip, chip, chip])
    # Check horizontal sequences
    for r in range(ROW_COUNT):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[r, :]))):
            return True
    # Check vertical sequences
    for c in range(COLUMN_COUNT):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[:, c]))):
            return True
    # Check positively sloped diagonals
    for offset in range(-2, 4):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board.diagonal(offset)))):
            return True
    # Check negatively sloped diagonals
    for offset in range(-2, 4):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, np.flip(board, 1).diagonal(offset)))):
            return True


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


# # # added functions # # #
import math
from functools import partial
import optimals

def absincr(x, by=1):
    """
    returns: the increase of the magnitude of x by "by" \n
    ie moves x away from 0 by "by" \n
    examples: absincr(1,2)=3, absincr(-1,2)=-3, absincr(-7,10)=-17, 
    """
    return int(x + math.copysign(by,x))
    # return lambda x: int(x + math.copysign(1,x)) 

def randomMove(board) -> int:
    valids = get_valid_locations(board)
    return -1 if len(valids) == 0 else random.choice(valids)

def book0or1(board, turns): #not valid for other board sizes
    """
    gives moves from the playbook for turns 0 or 1, otherwise returns -1
    returns: column to move or -1
    """
    # playbook for 0th and 1st turns
    if turns <= 1:
        if not (board[0][1] + board[0][-2]): return 3 
        if board[0][1]: return 2 #1st turn and opp played 0,1 (ie col #2)
        else: return 4 #1st turn and opp played 0,5 (ie col 6)
    return -1

def heuristic0(board, turns):
    """bad heuristic of only the playbook of moves 0 and 1, otherwise random"""
    if turns <= 1: return book0or1(board,turns)
    return randomMove(board)

def perfectAI(board: np.ndarray):
    firstMove = -1
    for i in range(COLUMN_COUNT): # find first move spot
        if board[0][i] != 0:
            firstMove = i
            break
    board[:,:] = np.array(optimals.optimal(firstMove))
    return 0

# def heuristic1(board, turns):


# # # # # # # # # # # # # # main execution of the game # # # # # # # # # # # # # #
turn = 0

board = create_board()
print_board(board)
game_over = False

while not game_over:

    if turn % 2 == 0:
        col = int(input("RED please choose a column(1-7): "))
        while col > 7 or col < 1:
            col = int(input("Invalid column, pick a valid one: "))
        while not is_valid_location(board, col - 1):
            col = int(input("Column is full. pick another one..."))
        col -= 1

        row = get_next_open_row(board, col)
        drop_chip(board, row, col, RED_INT)
        if game_is_won(board, RED_INT):
            game_over = True
            print(colored("Red wins!", 'red'))
        winning_next_move = False

    if turn % 2 == 1 and not game_over:
        valid_locations = get_valid_locations(board)
        #TODO: all happens here
        column = partial(heuristic0, turns=turn)(board)
        # column = perfectAI(board)
        row = get_next_open_row(board, column)
        drop_chip(board, row, column, BLUE_INT)
        if game_is_won(board, BLUE_INT):
            game_over = True
            print(colored("Blue wins!", 'blue'))
    print_board(board)
    if (not game_over) and len(get_valid_locations(board)) == 0: #added check if won on the last piece!
        game_over = True
        print(colored("Draw!", 'blue'))
    turn += 1
# %%
