#new

#%% time
from functools import reduce
from typing import Type, Union
from c4_heur import Game as C4
import numpy as np
import random
from termcolor import colored 
import math

# TODO: these classes should really be player classes and there should be a game class that these both use 

class Carlos:
    """I named my monte carlo implementation carlos"""

    #class/static variables
    ROW_COUNT, COLUMN_COUNT = 6, 7
    RED_CHAR, BLUE_CHAR = colored('X', 'red'), colored('O', 'blue')
    EMPTY, RED_INT, BLUE_INT = 0, 1 ,2

    def __init__(self) -> None:
        self.turn = 0
        self.board = Carlos.create_board().copy()
        self.game_over = False
        self.winner = -1
        self.pos = [] #for https://connect4.gamesolver.org/en/?pos=


    @classmethod
    def load_game(cls, game_state):
        """pass an array of ints, one long int, or a string of the moves. ONE INDEXED \n
        returns a Carlos instance from that position
        """
        inst = cls()
        if game_state == None: raise RuntimeError("didn't load properly")
        if type(game_state) is not list and len(str(game_state))>0:
            game_state = [int(i) for i in str(game_state)]
        for m in game_state: inst.load_move(m)
        if not game_state == inst.pos: raise RuntimeError("didn't load properly")
        return inst

    #static methods
    @staticmethod
    def create_board():
        """create empty board for new game"""
        board = np.zeros((Carlos.ROW_COUNT, Carlos.COLUMN_COUNT), dtype=np.int8)
        return board
    @staticmethod
    def drop_chip(board, row, col, chip):
        """place a chip (red or BLUE) in a certain position in board and update pos save"""
        if row == None: return
        board[row][col] = chip
    @staticmethod
    def is_valid_location(board, col):
        """check if a given row in the board has a room for extra dropped chip"""
        return board[Carlos.ROW_COUNT - 1][col] == 0
    @staticmethod
    def get_next_open_row(board, col):
        """assuming column is available to drop the chip,
        the function returns the lowest empty row  """
        for r in range(Carlos.ROW_COUNT):
            if board[r][col] == 0:
                return r
    @staticmethod
    def board_string(board):
        """return string of current board with all chips put in so far"""
        return " 1 2 3 4 5 6 7 \n" + "|" + (np.array2string(np.flip(np.flip(board, 1))).replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_").replace("1", Carlos.RED_CHAR).replace("2", Carlos.BLUE_CHAR).replace("\n", "|\n")) + "|"
    @staticmethod
    def print_board(board):
        """print current board with all chips put in so far"""
        win_str = ""
        if Carlos.game_is_won(board, board.RED_INT): win_str = f'\n{colored("Red wins!", "red")}'
        elif Carlos.game_is_won(board, board.BLUE_INT): win_str = f'\n{colored("Blue wins!", "blue")}'
        elif len(Carlos.get_valid_locations(board))==0: win_str = f'\n{colored("Draw!", "blue", "on_red")}'
        print(""+Carlos.board_string(board)+win_str)
    @staticmethod
    def game_is_won(board, chip):
        """check if current board contain a sequence of 4-in-a-row of in the board
        for the player that play with "chip"  """
        #TODO: add early termination if a row doesn't at least equal 4 times chip? 
        winning_Sequence = np.array([chip, chip, chip, chip])
        # Check horizontal sequences
        col_sums:Type[np.array] = np.sum(board, axis=0)
        row_sums:Type[np.array] = np.sum(board, axis=1)
        for r in range(Carlos.ROW_COUNT):
            if row_sums[r] < chip*4: continue # if the sum isn't at least 4 times our chip then no win
            if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[r, :]))):
                return True
        # Check vertical sequences
        for c in range(Carlos.COLUMN_COUNT):
            if col_sums[c] < chip*4: continue # if the sum isn't at least 4 times our chip then no win
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
    @staticmethod
    def get_valid_locations(board):
        """return the columns that are open"""
        valid_locations = []
        for col in range(Carlos.COLUMN_COUNT):
            if Carlos.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations

    @staticmethod
    def absincr(x, by=1):
        """ returns: the increase of the magnitude of x by "by" \n
        ie moves x away from 0 by "by" \n
        examples: absincr(1,2)=3, absincr(-1,2)=-3, absincr(-7,10)=-17, """
        return int(x + math.copysign(by,x))
        # return lambda x: int(x + math.copysign(1,x)) 


    #class methods
    def __str__(self) -> str:
        win_str = ""
        if self.winner == self.RED_INT: win_str = f'\n{colored("Red wins!", "red")}'
        elif self.winner == self.BLUE_INT: win_str = f'\n{colored("Blue wins!", "blue")}'
        elif self.winner == self.EMPTY: win_str = f'\n{colored("Draw!", "blue", "on_red")}'
        return Carlos.board_string(self.board) + win_str

    def clear(self):
        self.turn = 0
        self.board = Carlos.create_board().copy()
        self.game_over = False
        self.winner = -1
        self.pos = []

    def dropChip(self, row, col, chip):
        """INSTANCE METHOD to place a chip (red or BLUE) in a certain position in board"""
        self.pos.append(col+1) # update game state save 
        self.drop_chip(self.board, row, col, chip)
    def isValidLocation(self, col):
        """INSTANCE METHOD to check if a given row in the board has a room for extra dropped chip"""
        return self.is_valid_location(self.board, col)
    def getNextOpenRow(self, col):
        """INSTANCE METHOD: assuming column is available to drop the chip,
        the function returns the lowest empty row  """
        return self.get_next_open_row(self.board, col)
    def gameIsWon(self, chip):
        """INSTANCE METHOD to check if current board contain a sequence of 4-in-a-row of in the board
        for the player that play with "chip"  """
        return self.game_is_won(self.board, chip)
    def getValidLocations(self):
        """INSTANCE METHOD to return the columns that are open"""
        return self.get_valid_locations(self.board)

    def save_game(self):
        return str("").join([str(i) for i in self.pos])

    def last_move(self) -> int:
        return None if not len(self.pos) else self.pos[-1]

    def remove(self, row, col):#row is redundant but whatever
        self.board[row,col] = 0

    def randomMove(self) -> int:
        """returns the column of a valid random move or -1 if none exist"""
        valids = self.getValidLocations()
        return -1 if len(valids) == 0 else random.choice(valids)

    def book0or1(self): #not valid for other board sizes
        """ gives moves from the playbook for turns 0 or 1, otherwise returns -1
        returns: column to move or -1 """
        # playbook for 0th and 1st turns
        if self.turn <= 1:
            if not (self.board[0][1] + self.board[0][-2]): return 3 
            if self.board[0][1]: return 2 #1st turn and opp played 0,1 (ie col #2)
            else: return 4 #1st turn and opp played 0,5 (ie col 6)
        return -1

    def random_with_book01(self) -> int:
        """bad heuristic of only the playbook of moves 0 and 1, otherwise random"""
        if self.turn <= 1: return self.book0or1()
        return self.randomMove()

    def random_finish(self) -> int:
        """makes random moves until the game is over and returns the color of the winner"""
        # TODO: do we care about how many moves the game took? 
        while(not self.game_over):
            color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
            col = self.randomMove()
            if col > 6 or col < 0: raise RuntimeError("weird draw situation?")
            row = self.getNextOpenRow(col)
            self.dropChip(row, col, color)
            if self.gameIsWon(color):
                self.game_over = True
                self.winner = color
            elif len(self.getValidLocations()) == 0: #(not self.game_over) and
                self.game_over = True
                self.winner = self.EMPTY
            else: self.turn += 1 # player just went (and not end of game), need to incr turn
        return self.winner

    @staticmethod
    def monte_trials(game, color: Type[int], n=100): # could switch the game from being a game to a save game string
        """params: a theoretical (Carlos) game with the first move of monte carlo simulation filled and the user number that is doing the simulation and the number of trials to run with default of 100 \n
        returns a tuple of (wins, losses)"""
        if game.game_over: # checking to see if this move is already a win
            if game.winner == game.EMPTY: return (0,0) # draw
            return (n,0) if game.winner==color else (0,n) # we won all games if winner is our color otherwise we lost all
        save = game.save_game()
        wins, losses = 0, 0
        draws = 0 # TODO: for testing only
        for _ in range(n):
            load = Carlos.load_game(save)
            winner = load.random_finish() # play game randomly starting with other color's turn
            if color==game.EMPTY: draws += 1
                # continue #draw. mayb pass instead? 
            elif color==winner: wins += 1
            else: losses += 1
        assert(n == (wins+losses+draws)) # TODO: for testing
        return (wins, losses)

    def monte(self, n=100) -> int:
        """do monte carlo from current state to find the best col to play"""
        save:Type[str] = self.save_game()
        color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
        moves = {} # TODO: figure out best scoring metric (wins, wins/losses, wins/turns etc )
        for c in self.getValidLocations(): #each open col
            g: Type[Carlos] = self.load_game(save+str(c+1)) #load is 1 indexed, this is a move also 
            wins, losses = Carlos.monte_trials(g, color, n=n) # starts w other player bc we 'went' by adding c to the save
            moves[c] = (wins/(losses+.0000001)) # avoid div zero
        if not len(moves): raise RuntimeError("bad monte sim, no moves oooop")
        moves = sorted(moves.items(), key=lambda kv: kv[1], reverse=True)
        tops = [i[0] for i in moves if not i[1]<(moves[0])[1]] # all the top vals
        return random.choice(tops)

    def our_move(self, monte_n=100) -> int:
        """wrapper around heur1 for runner class"""
        return self.monte(n=monte_n)

    def isPlayable(self, r, c):
        availRow = self.getNextOpenRow(c) # see if threat is playable
        # if availRow == None: continue
        if availRow == r: return True #block imminent threat
        return False

    def load_move(self, move):
        if self.game_over: return self.winner#throw?
        color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
        col = move
        if col > 7 or col < 1: raise RuntimeError("bad load")
        if not self.isValidLocation(col-1): raise RuntimeError("bad load")
        col -= 1 # TODO: do we want 0 or 1 indexing
        row = self.getNextOpenRow(col)
        self.dropChip(row, col, color)
        if self.gameIsWon(color):
            self.game_over = True
            self.winner = color
            return color # TODO: related to coloring above, what do we print when we win vs computer
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
            return self.EMPTY # draw? TODO: what ret
        self.turn += 1


    def go(self, move, monte_n=100):
        # TODO: should we return the move the pc made or the position state or the win flag or a tuple of some combination?
    # if self.turn % 2 == 0: # TODO: figure out coloring - we know this is always the human moving but who went first??
        if self.game_over: return self.winner#throw?
        color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
        col = move
        if col > 7 or col < 1: return None
        if not self.isValidLocation(col-1): return None
        col -= 1
        row = self.getNextOpenRow(col)
        self.dropChip(row, col, color)
        if self.gameIsWon(color):
            self.game_over = True
            self.winner = color
            return None
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
            return None
        self.turn += 1 # player just went, need to incr turn
        color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
        column = self.monte(n=monte_n)
        row = self.getNextOpenRow(column)
        self.dropChip(row, column, color)
        if self.gameIsWon(color):
            self.game_over = True
            self.winner = color
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
        self.turn += 1
        return column


    def start_interactive(self, heur=None, humanPlayerNum=1):
        """start a game using heur1 and human goes first by default \n """
        # if heur == None: heur = self.heuristic1
        color_names = {0:"RED",1:"BLUE"}
        self.clear()
        print(self)
        humanPlayerNum -= 1 #(1,2) -> 0 if human go first, else 1
        while not self.game_over:
            if self.turn % 2 == humanPlayerNum:
                color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
                col = int(input(f"{color_names[color]} please choose a column(1-7): "))
                while col > 7 or col < 1:
                    col = int(input("Invalid column, pick a valid one: "))
                while not self.isValidLocation(col-1):
                    col = int(input("Column is full. pick another one..."))
                col -= 1 # fix zero index
                     
                row = self.getNextOpenRow(col)
                self.dropChip(row, col, color)
                if self.gameIsWon(color):
                    self.game_over = True
                    self.winner = color
                     
            else:
                color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
                column = self.monte()
                row = self.getNextOpenRow(column)
                self.dropChip(row, column, color)
                if self.gameIsWon(color):
                    self.game_over = True
                    self.winner = color
            if (not self.game_over) and len(self.getValidLocations()) == 0:
                self.game_over = True
                self.winner = self.EMPTY
            print(self)
            self.turn += 1
        return self.pos

def monte_vs_heur(monte_first=True, playby=False, rec=False, monte_n=100):
    """plays a full game of monte vs heuristic\n
    self monte_first to False if want heuristic to go first\n
    returns (monte_win, heur_win) \n
    -> (1,0) if monte win, (0,0) if tie, (0,1) if heur win"""
    # TODO: would be nice to have a game class and agents but whatever, two copies of the game it is
    m = Carlos() # monte carlo game
    h = C4() # heuristic game
    curr = m if monte_first else h # current player starts as first player
    other = m if curr is h else h
    while not (m.game_over or h.game_over):
        last = curr.our_move(monte_n=monte_n)
        curr.load_move(last+1) # load is 1 indexed
        other.load_move(last+1)
        if playby:
            print()
            print(m)
            print(h)
        curr, other = other, curr # swap whose turn it is 
    if m.winner!=h.winner:
        print()
        print(m)
        print(h)
        raise RuntimeError("game disagreement??")
    monte_player = 1 if monte_first else 2
    heur_player = 2 if monte_first else 1
    monte_win = 1 if m.winner==monte_player else 0
    heur_win = 1 if m.winner==heur_player else 0
    if playby:
        print("\n")
        print(m)
        print(h)
    return (monte_win, heur_win) if not rec else (monte_win, heur_win, m.save_game())

def monte_vs_rand(monte_first=True, playby=False, monte_n=100):
    """plays a full game of monte vs random player\n
    set monte_first to False if want random to go first\n
    returns (monte_win, random_win) \n
    -> (1,0) if monte win, (0,0) if tie, (0,1) if heur win"""
    # TODO: would be nice to have a game class and agents but whatever, two copies of the game it is
    m = Carlos() # monte carlo game
    if monte_first: m.load_move((m.our_move(monte_n=monte_n)+1))
    while not m.game_over:
        m.go((m.randomMove()+1),monte_n=monte_n)
        if playby:
            print()
            print(m)
    monte_player = 1 if monte_first else 2
    rand_player = 2 if monte_first else 1
    monte_win = 1 if m.winner==monte_player else 0
    rand_win = 1 if m.winner==rand_player else 0
    if playby:
        print("\n")
        print(m)
    return (monte_win, rand_win)



if __name__ == "__main__":

    # monte_n = 18
    # ngames = 100

    # %time games = [monte_vs_rand(monte_n=monte_n) for _ in range(ngames)]
    # scores = reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), games)
    # print(f"{ngames} random games with monte_n={monte_n}:")
    # print(scores)
    # print()
    # print()

    
    # monte_n = 100
    # ngames = 10
    # %time games = [monte_vs_heur(monte_n=monte_n) for _ in range(ngames)]
    # scores = reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), games)
    # print(f"{ngames} heur games with monte_n={monte_n}:")
    # print(scores)

    c = Carlos()
    c.start_interactive()

    # carlo = Carlos.load_game(4444)
    # print(carlo)
    # %prun c = carlo.monte()
    # print(carlo)


    # print("finding losses for monte vs heur, n=1000")
    # losses = []
    # while len(losses) < 5:
    #     %time _, ml, mrec = monte_vs_heur(rec=True,monte_n=1000)
    #     if ml:
    #         print(mrec)
    #         losses.append(mrec)
    # print("\n\nlosses:")
    # for loss in losses:
    #     print(loss)

    # pass

# TODO: async while waiting for human, keep calc moves round robin
