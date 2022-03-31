#%%
from __future__ import annotations # requires python 3.7+
from functools import reduce 
from typing import Tuple, Type, Union, List
from c4_heur import Game as C4
import numpy as np
import random
from termcolor import colored 
import time
import os.path
import math
import sys
import pickle

book = { # i didn't end up using this much
    "":[4], # 1s
    "1":[2,4],"2":[3],"3":[3,4,5,6],"4":[4],"5":[2,3,4,5],"6":[5],"7":[4,6], # 2s
    "11":[4,6],"12":[1,2,4,5,6,7],"13":[3],"14":[4],"15":[4],"16":[6],"17":[4],
    "21":[2,5],"22":[5],"23":[2,3],"24":[2,4],"25":[4],"26":[2,4,5],"27":[2,4],
    "31":[4],"32":[6],"33":[2,4],"34":[3,4],"35":[3,5],"36":[2,3,4,5,6],"37":[3,4],
    "41":[4],"42":[2,6],"43":[6],"44":[4],"45":[2],"46":[2,6],"47":[4],
    "51":[4,5],"52":[2,3,4,5,6],"53":[3,5],"54":[4,5],"55":[4,6],"56":[2],"57":[4],
    "61":[4,6],"62":[3,4,6],"63":[4],"64":[4,6],"65":[5,6],"66":[3],"67":[3,6],
    "71":[4],"72":[2],"73":[4],"74":[4],"75":[5],"76":[1,2,3,4,6,7],"77":[2,4] # 3s???
    } 

class Node:
    __version__ = 3 # v2 had bug fix, v3 has node sibls
    BRANCHING = 7 # branching factor of 7
    def __init__(self, state:str, parent=None, winner=None, deepest=0):
        self.parent = parent
        self.n = 0 # times explored
        self.w = 0 # wins
        self.state: str = state
        self.children = []
        self.winner = winner # is game over, 0draw, 1red, 2blue
        self.deepest:int = deepest # deepest child depth (relative to us!) ie height

    def __str__(self, d=0, levels=-2) -> str:
        ret = "node has parents-------->\n" if (not d and self.parent is not None) else ""
        ret += "\t"*d+repr((self.w,self.n,self.winner,self.state,self.deepest))+"\n"
        if levels<=-2 or levels>=0: # either no level limit or under the limit
            for child in self.children: ret += child.__str__(d+1, levels=levels-1)
        return ret

    def is_over(self) -> bool:
        return False if self.winner is None else True 

    def p(self) -> Node:
        return self.parent

    def uct(self) -> Union[int, float, np.number]:
        if self.n == 0: return math.inf
        pN = 1 if self.parent is None else self.parent.n # 0 not in domain of log
        return (self.w/self.n) + ((1.4142)*math.log(pN)/self.n)**0.5 # uct with c=sqrt(2)=1.4142
    
    @classmethod
    def ver(node: Node):
        vers = 0
        try: vers = node.__version__
        except AttributeError: pass # mightve pickled an old version
        return vers

    def add_height(self):
        """recursively add height on child add"""
        # on insertion, as long as we are the deepest child keep adding one to our parent
        node:Node = self
        pa:Node =  node.p()
        sibls = [] if pa is None else [i for i in pa.children if i is not node] # get sibls
        sibls = [] if len(sibls) < 1 else [i.deepest for i in sibls] # get siblings depths
        while pa is not None and not (len(sibls) > 0 and max(sibls) >= node.deepest) : # either no parent or has sibs w >= depth
            node = pa
            node.deepest += 1 # we go one deeper
            pa = node.p() # get parent
            sibls = [] if pa is None else [i for i in pa.children if i is not node]
            sibls = [] if len(sibls) < 1 else [i.deepest for i in sibls]


    def add(self, moves: Union[tuple[int, Union[int, None]],  list[tuple[int, Union[int, None]]]]) -> list[Node]:
        """1index col moves: adds and returns child nodes for the given moves where moves is (a list of) tuple(s) of (column, win) and win is None if no winner, 0draw, 1red, 2blue\n
        doesn't add duplicates"""
        child_moves = [i.state[-1] for i in self.children]
        if type(moves) is list:
            for (col,win) in moves:
                if str(col) in child_moves: continue # already have this child
                self.children.append(Node(""+self.state+str(col), self, win))
        elif str(moves[0]) not in child_moves: # add a single child, making sure it's not already added
            self.children.append(Node(""+self.state+str(moves[0]), self, moves[1]))
        # TODO: make sure siblings we didnt add can be explored in subseq. searches
        if self.deepest == 0: # if we haven't already bubbled up depth count
            self.deepest = 1 # add 1 to our height
            self.add_height() # add to the top (or until stop)
        return self.children # TODO: think about safety

    def select(self) -> tuple[Node, int]:
        """find the favorable node to explore based on uct and return it and the depth from self node.\n
        returns self,0 if self.is_over()"""
        node = self # pointer to current node we're considering
        childs: list[Node] = [] # pointer to current children we're considering
        depth = 0
        while(len(node.children) > 0): # if it's a leaf
            childs = node.children
            ucts = [c.uct() for c in childs] # get uct scores for all top vals
            opts = zip(childs, ucts) # list[(child,uct)]
            opts = sorted(opts, key=lambda x: x[1], reverse=True) # sorted list[(child,uct)] based on uct val
            tops = [i[0] for i in opts if not i[1]<(opts[0])[1]] # all the top vals
            depth += 1
            node: Node = (random.choice(tops)) # select (one of the) top child(ren)
        return node, depth # a leaf selected based on uct scores TODO: what do we do if game is over at this node
    
    def highest(self) -> Node:
        """returns the child w the most visits"""
        if len(self.children) < 1: return None
        childs = self.children
        opts = zip(childs, [i.n for i in childs]) # list[(child,uct)]
        opts = sorted(opts, key=lambda x: x[1], reverse=True) # sorted list[(child,uct)]
        tops = [i[0] for i in opts if not i[1]<(opts[0])[1]]
        return random.choice(tops)
    
    def get(self, move, winner=None, others:Type[List[Tuple]]=None) -> Node:
        """returns the child node with the specified move if already exists, otherwise creates it and returns\n
        also adds the nodes in "others" as unexplored siblings where others is a list of tuples and each tuple is (col, winner)"""
        if others is None: others = []
        if len(self.children) < self.BRANCHING: # might as well do a (insufficient) check here
            self.add((move,winner)) # adds our move (if doesn't exist already)
            self.add(others) # adds sibls if they don't already exist (so we can explore them later?)
        for i, x in enumerate(self.children): # get the index,node for each child
        # for i,x in enumerate(childs_moves): # get the index of the node corresponding to this child
            if x.state[-1] == str(move): # if column of node is our column
                return self.children[int(i)] # return it 
        raise RuntimeError("bad node structure, cant get or add node")
        # return None # bad
    
    def backprop(self, score, loss1=True):
        node = self
        value = score
        while(node is not None):
            node.n += 1
            node.w += value

            node = node.p() # get parent
            if loss1: value = 1-value # 1win, 0loss, 0.5tie -> 1-0=1, 1-1=0, 1-.5=.5
            else: value = value * (-1) # 1win, -1loss, 0tie -> -1*-1=-1, -1*-1=1, -1*0=0
        

    @staticmethod
    def getParent(node):
        return node.parent



class MCTS:

    #class/static variables
    ROW_COUNT, COLUMN_COUNT = 6, 7
    TOTAL_MOVES = ROW_COUNT * COLUMN_COUNT
    DEF_THINK = (7, 18) # default (min,max) think time for timed search
    RED_CHAR, BLUE_CHAR = colored('X', 'red'), colored('O', 'blue')
    EMPTY, RED_INT, BLUE_INT = 0, 1 ,2

    def __init__(self, start_tree:Node=None, think_tuple:tuple=None) -> None:
        # def __init__(self, tree=None) -> None:
        self.turn = 0
        self.board = MCTS.create_board().copy()
        self.game_over = False
        self.winner = -1
        self.pos = [] #for https://connect4.gamesolver.org/en/?pos=
        # self.tree = tree if tree is not None else MCTS.load_mcts()
        self.tree = start_tree
        if self.tree is None: self.tree = self.loadOrMake()
        self.head = self.tree # save pointer to the head of the tree
        self.rounds = 0 # number of rounds of mcts done
        self.think = think_tuple
        self.no_color = False
        # self.tree = start_tree
        # Node("")

    def loadOrMake(self):
        """i added these bc i was getting weird circular call dependencies but they're not needed and could be written out if I wasnt lazy"""
        if not os.path.exists('tree.pkl'):
            print("no tree found, making new tree...")
            sys.stdout.flush()
            return MCTS.create_mcts_save()
        print("found tree, importing...")
        with open('tree.pkl', 'rb') as f:
            p = pickle.load(f)
            print("done getting tree!")
            try: print(f'Deepest node from root: {p.deepest}\n')
            except AttributeError: print() 
            sys.stdout.flush()
            return p
    
    def change_think_time(self, min=None, max=None):
        if min is None: min = self.DEF_THINK[0]
        if max is None: max = self.DEF_THINK[1]
        if min >= max: max = min+0.7
        self.think = (min,max)
    
    def set_no_color(self, no_color: bool):
        """set if the string representation of the board uses colors Red,Blue for X,O"""
        self.no_color = no_color
    
    def toggle_color(self):
        """toggles if the string representation of the board uses colors Red,Blue for X,O"""
        self.no_color = not self.no_color


    @classmethod
    def load_game(cls, game_state, tree=None):
        """pass an array of ints, one long int, or a string of the moves. ONE INDEXED \n
        returns a mcts instance from that position
        """
        if tree is None: tree = Node("")
        inst = cls(start_tree=tree)
        if game_state is None: raise RuntimeError("didn't load properly")
        if type(game_state) is not list and len(str(game_state))>0:
            game_state = [int(i) for i in str(game_state)]
        for m in game_state: inst.load_move(m)
        if not game_state == inst.pos: raise RuntimeError("didn't load properly")
        return inst

    #static methods
    @staticmethod
    def create_board():
        """create empty board for new game"""
        board = np.zeros((MCTS.ROW_COUNT, MCTS.COLUMN_COUNT), dtype=np.int8)
        return board
    @staticmethod
    def drop_chip(board, row, col, chip):
        """place a chip (red or BLUE) in a certain position in board and update pos save"""
        if row is None: return
        board[row][col] = chip
    @staticmethod
    def is_valid_location(board, col):
        """check if a given row in the board has a room for extra dropped chip"""
        return board[MCTS.ROW_COUNT - 1][col] == 0
    @staticmethod
    def get_next_open_row(board, col):
        """assuming column is available to drop the chip,
        the function returns the lowest empty row  """
        for r in range(MCTS.ROW_COUNT):
            if board[r][col] == 0:
                return r
    @staticmethod
    def top_in_col(board, col):
        """0ind: returns the 0indexed row of the topmost chip in this column or -1 if nothing in row"""
        for r in reversed(range(MCTS.ROW_COUNT)):
            if board[r][col]: return r
        return -1
    @staticmethod
    def board_string(board, no_color=False):
        """return string of current board with all chips put in so far"""
        ret: str = " 1 2 3 4 5 6 7 \n" + "|" + (np.array2string(np.flip(np.flip(board, 1))).replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_").replace("1", "X").replace("2", "O").replace("\n", "|\n")) + "|"
        if no_color: return ret
        return ret.replace("X", MCTS.RED_CHAR).replace("O", MCTS.BLUE_CHAR)
    @staticmethod
    def print_board(board, no_color=False):
        """print current board with all chips put in so far"""
        win_str = ""
        if MCTS.game_is_won(board, board.RED_INT): 
            win_str = "Red wins!" if no_color else f'\n{colored("Red wins!", "red")}'
        elif MCTS.game_is_won(board, board.BLUE_INT): 
            win_str = "Blue wins!" if no_color else f'\n{colored("Blue wins!", "blue")}'
        elif len(MCTS.get_valid_locations(board)) == 0: 
            win_str = "Draw!" if no_color else f'\n{colored("Draw!", "blue", "on_red")}'
        print("" + MCTS.board_string(board, no_color=no_color) + win_str)
    @staticmethod
    def game_is_won(board, chip):
        """check if current board contain a sequence of 4-in-a-row of in the board
        for the player that play with "chip"  """
        winning_Sequence = np.array([chip, chip, chip, chip])
        # Check horizontal sequences
        col_sums:Type[np.array] = np.sum(board, axis=0) # for early termination
        row_sums:Type[np.array] = np.sum(board, axis=1)
        for r in range(MCTS.ROW_COUNT):
            if row_sums[r] < chip*4: continue # if the sum isn't at least 4 times our chip then no win
            if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[r, :]))):
                return True
        # Check vertical sequences
        for c in range(MCTS.COLUMN_COUNT):
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
        """return the columns that are open 0index col"""
        valid_locations = []
        for col in range(MCTS.COLUMN_COUNT):
            if MCTS.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations
    @staticmethod
    def save_to_board(save):
        """get the valid open columns from the current save state"""
        board = MCTS.create_board()
        color = MCTS.RED_INT # red goes first, todo: make sure doesn't conflict w other way to pick first
        for col in save:
            col = int(col)-1
            MCTS.drop_chip(board, MCTS.get_next_open_row(board, col), col, color)
            color = MCTS.RED_INT if color == MCTS.BLUE_INT else MCTS.BLUE_INT
        return board
    @staticmethod
    def get_winner_next(bd, col, chip):
        """0index col: checks "ahead" if playing the col for both colors will end the game. \n
        If both colors win on placement, returns the win for chip first (ie if both win on column 4 and chip=blue, returns 2) \n
        returns color of the winner, or 0 if draw, or None if not game over\n
        TODO: very inefficient code, rewrite to cache 3s in a row like in c4_heur?"""
        other = MCTS.BLUE_INT if chip == MCTS.RED_INT else MCTS.RED_INT
        row = MCTS.get_next_open_row(bd, col)
        board = bd.copy()
        for color in [chip, other]:
            MCTS.drop_chip(board, row, col, color)
            col_sums = np.sum(board, axis=0)
            row_sums = np.sum(board, axis=1)
            win_seq = np.array([color, color, color, color])
            # Check horizontal sequences
            for r in range(MCTS.ROW_COUNT):
                if row_sums[r] < color*4: continue # if the sum isn't at least 4 times our chip then no win
                if "".join(list(map(str, win_seq))) in "".join(list(map(str, board[r, :]))):
                    return color
            # Check vertical sequences
            for c in range(MCTS.COLUMN_COUNT):
                if col_sums[c] < color*4: continue # if the sum isn't at least 4 times our chip then no win
                if "".join(list(map(str, win_seq))) in "".join(list(map(str, board[:, c]))):
                    return color
            # Check positively sloped diagonals
            for offset in range(-2, 4):
                if "".join(list(map(str, win_seq))) in "".join(list(map(str, board.diagonal(offset)))):
                    return color
            # Check negatively sloped diagonals
            for offset in range(-2, 4):
                if "".join(list(map(str, win_seq))) in "".join(list(map(str, np.flip(board, 1).diagonal(offset)))):
                    return color
        if len(MCTS.get_valid_locations(board)) < 1: # neither won and board is full
            return MCTS.EMPTY # draw
        return None # neither won, not a draw, game on!
    
    @staticmethod
    def game_is_won_load(save):
        """based on current save game state, sees if the game is currently won or draw.\n
        returns red win first (had to pick one or the other...)\n
        returns color of winner, or 0draw, or None if not game over"""
        board = MCTS.save_to_board(save)
        if MCTS.game_is_won(board, MCTS.RED_INT): return MCTS.RED_INT
        if MCTS.game_is_won(board, MCTS.BLUE_CHAR): return MCTS.BLUE_INT
        if len(MCTS.get_valid_locations(board)) < 1: return MCTS.EMPTY
        return None

    @staticmethod
    def get_valid_loc_load(save) -> list[int]:
        """get the valid open columns from the current save state"""
        return MCTS.get_valid_locations(MCTS.save_to_board(save))

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
        no_color = False
        try: no_color = self.no_color
        except AttributeError: pass
        if self.winner == self.RED_INT: 
            win_str = "Red wins!" if no_color else f'\n{colored("Red wins!", "red")}'
        elif self.winner == self.BLUE_INT: 
            win_str = "Blue wins!" if no_color else f'\n{colored("Blue wins!", "blue")}'
        elif self.winner == self.EMPTY: 
            win_str = "Draw!" if no_color else f'\n{colored("Draw!", "blue", "on_red")}'
        ret: str = MCTS.board_string(self.board, no_color=no_color) + win_str
        return ret

    def clear(self):
        self.turn = 0
        self.board = MCTS.create_board().copy()
        self.game_over = False
        self.winner = -1
        self.pos = []
        self.tree = self.head

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
        """INSTANCE METHOD to return the 0indexed columns that are open 0index col"""
        return self.get_valid_locations(self.board)

    def save_game(self):
        return str("").join([str(i) for i in self.pos])

    def last_move(self) -> int:
        """1index col: returns the last move made"""
        return None if len(self.pos)==0 else self.pos[-1]

    def remove(self, row, col):#row is redundant but whatever
        self.board[row,col] = 0

    def randomMove(self) -> int:
        """returns the column of a valid random move or -1 if none exist"""
        valids = self.getValidLocations()
        return -1 if len(valids) == 0 else random.choice(valids)

    def winOrBlock(self):
        """returns the column for a win if possible, otherwise block a win, otherwise None"""
        # ignore:  ret_wins=False \n if ret_wins is True then returns a tuple of the column from above and a list of ()
        valids = self.getValidLocations()
        if len(valids) == 0: return None
        turn = self.BLUE_INT if self.turn%2 else self.RED_INT
        wins = [self.get_winner_next(self.board, i, turn) for i in valids]
        # wins = [self.get_winner(self.board, i, turn) for i in valids]
        opts = [i for i in zip(valids, wins)]
        gameovers = [ii for ii in opts if ii[1] is not None and ii[1]!=0]
        if len(gameovers) > 0:
            wewin = [ii for ii in gameovers if ii[1]==turn]
            if len(wewin) > 0:
                return random.choice(wewin)[0]
            welose = [ii for ii in gameovers if ii[1]!=turn]
            if len(welose) > 0:
                return random.choice(welose)[0]
        return None

    def winsOrRand(self) -> int:
        """wins if possible, otherwise blocks opponent from winning if possible, otherwise random"""
        valids = self.getValidLocations()
        if len(valids) == 0: return -1
        wins = self.winOrBlock()
        if wins is not None: return wins
        return random.choice(valids)

    def randomOrBook(self) -> int:
        """returns the column of a move either by opening book if exists for position or a valid random move or -1 if none exist"""
        save = self.save_game()
        if save in book.keys():
            return random.choice(book[save])-1 # 0 index
        return self.winsOrRand()
        # valids = self.getValidLocations()
        # return -1 if len(valids) == 0 else random.choice(valids)

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
        """makes random moves until the game is over and returns the color of the winner\n
        NOTE: `randomOrBook` uses the winOrBlock random method where it wins if able, else blocks if able, else plays random"""
        while(not self.game_over):
            color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
            # col = self.winsOrRand() # win or block if able otherwise rand #TODO: would use but SLOW
            col = self.randomOrBook() # opening book if exists else random 
            # col = self.randomMove()
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


    def mcts1(self, tree=None):
        """does one round of mcts"""
        if tree is None: tree = self.tree # TODO: idk lol
        self.rounds += 1 # increment mcts counter
        node = tree
        node, depth = node.select() # selection phase
        turn = self.BLUE_INT if len(node.state)%2 else self.RED_INT # gets whose turn it is
        if not node.is_over(): # non terminal node, expansion phase
            board = self.save_to_board(node.state) # we get the board (note: board, not game) of this save state
            moves = [i+1 for i in self.get_valid_locations(board)] # get all the valid moves 1index
            wins = [self.get_winner_next(board, col-1, turn) for col in moves] # get the winners (if win) after playing each moves
            # wins = [self.get_winner(board, col-1, turn) for col in moves] # get the winners (if win) after playing each moves
            childs = node.add([i for i in zip(moves, wins)]) # add the children nodes to our node
            term_nodes = [n for n in childs if n.winner is not None] # all the nodes where the game is over after playing
            
            node = random.choice(childs) if len(term_nodes) <= 0 else random.choice(term_nodes) # select game ending node if avail, otherwise random child
        winner = node.winner if node.winner is not None else self.load_game(game_state=node.state, tree=self.tree).random_finish() # rollout
        score = 0
        if winner == self.EMPTY: score = 0.5
        elif winner == turn: score = 1
        node.backprop(score) # 1 if we won, .5 if tie, 0 if opp won 
        #TODO: change to -1,0,1? Nah.
        return tree, depth # idk. 
    
    def timed_search(self, min=None, max=None, tree=None, boost=0, retry=0):
        """does mcts for an amount of time between min and max seconds or between self.think[0] and self.think[1] if set"""
        if self.think is not None: # self.think takes precedence if it's set
            min, max = self.think
        else: # if either of the params arent set then get the default from the class
            if min is None: min = self.DEF_THINK[0]
            if max is None: max = self.DEF_THINK[1]
        if retry: # we're retrying timed search, add some time
            min += 2*retry
            max += 2*retry
        else: max = max - boost # if boost is set (and we're not retrying) then reduce time by that amnt
        long =  0.5*min if min>max else random.randint(math.floor(min),math.ceil(max))
        if tree is None: tree = self.tree # TODO: idk lol
        tree, _ = self.mcts1(tree)
        start = time.time()
        current = start
        while((current - start) <= long): 
            tree, _ = self.mcts1(tree)
            current = time.time()
        return tree

    def search(self, to_depth=5, tree=None, print_prog=False):
        """does mcts until one node passes a certain depth, default 5.\n
        a bit too much magic here for my liking. how to set depth params etc? How do we know when to stop"""
        if tree is None: 
            tree = self.tree # TODO: idk lol
        last_d = 0
        try: last_d = tree.deepest
        except AttributeError: pass
        start_d = last_d
        if print_prog:
            print(f"starting depth: {start_d}. tree.state:{tree.state}. tree.deepest:{tree.deepest}. starting.n:{tree.n}")
            sys.stdout.flush()
        tree, depth = self.mcts1(tree) # do while mcts
        remaining = self.TOTAL_MOVES - start_d - depth # num o remaining moves is total minus starting depth minus current depth
        if print_prog and depth > last_d:
            print(f"first mcts depth: {depth}. tree.state:{tree.state}. tree.deepest:{tree.deepest}. remaining:{remaining}. starting.n:{tree.n}")
            sys.stdout.flush()
        if depth > last_d: last_d = depth
        while (depth < to_depth) and (remaining > 0): # target depth or full board
            tree, depth = self.mcts1(tree) # do a round of mcts returning the depth of the selection
            remaining = self.TOTAL_MOVES - start_d - depth
            if print_prog and depth > last_d:
                print(f"hit new depth: {depth}. tree.state:{tree.state}. tree.deepest:{tree.deepest}. remaining:{remaining}. starting.n:{tree.n}")
                sys.stdout.flush()
            if depth > last_d: last_d = depth
        if remaining == 0:
            if print_prog: 
                print(f"depth:{depth}. tree.state:{tree.state}. tree.deepest:{tree.deepest}. remaining:{remaining}. bonus rounds")
                sys.stdout.flush()
            for _ in range(100): # do bonus rounds of mcts at max depth
                tree, depth = self.mcts1(tree)
                if print_prog and depth > last_d:
                    print(f"hit new depth: {depth}. tree.state:{tree.state}. tree.deepest:{tree.deepest}. starting.n:{tree.n}")
                    sys.stdout.flush()
                if depth > last_d: last_d = depth
        return tree
    
    def gameover(self):
        """does backprop on the ending node after an 'actual' game is played (ie considers it a rollout). set mctsp1 to False if mcts is player 2"""
        # make sure we have the last node on loss
        if not self.game_over: return
        played_last = MCTS.BLUE_INT if len(self.save_game()[:-1])%2 else MCTS.RED_INT # the player that played the ending move
        last = self.last_move()
        if int(self.tree.state[-1]) != last: # we haven't added the ending move to the tree yet (opp won or drew)
            wins_none = None if self.winner == -1 else self.winner # map the -1 to None for self.winner
            sibls = self.get_siblings(played_last) # get the sibling nodes for the ending node
            self.tree = self.tree.get(last, wins_none, others=sibls) # add and get the winning node (and add siblings) if not already added
        return self.mcts1() # Node.select() will return the same node because gameover, in mcts we have a terminal node so we're just doing backprop from gamending node


    def cleanup(self, addtl=None) -> str:
        """if work was done on the tree, saves a time stamped copy\n
        returns the name of the file or '' if no changes made to tree"""
        addtl = "" if addtl is None else f"{addtl}_"
        # if addtl is None: addtl = "" 
        if self.rounds <= 0: return ""# didn't work on the tree 
        vers = 0
        try: vers = self.tree.__version__
        except AttributeError: pass # mightve pickled an old version
        path = f"v{vers}_{addtl}r{self.rounds}_tree_{round(time.time())}.pkl"
        with open(""+path, "wb") as f:
            pickle.dump(self.head, f)
        return path

    @staticmethod
    def create_mcts_save(to_depth=8, path=None, print_prog=True):
        """turns a Node object into a .pkl file (prob should be in the Node class but whatevs)"""
        if path is None: path = "tree.pkl"
        m = MCTS(start_tree=Node(""))
        m.search(to_depth, print_prog=print_prog)
        if path != "tree.pkl":
            vers = 0
            try: vers = m.tree.__version__
            except AttributeError: pass # mightve pickled an old version
            path = f"v{vers}_" + path
        with open(""+path, "wb") as f:
            pickle.dump(m.tree, f)
        return m.head
    @staticmethod
    def load_mcts(path=None, make_if_ne=True)->Node:
        """loads an mcts tree .pkl file into a Node object (prob should be in the Node class but whatevs)"""
        if path is None: path = "tree.pkl"
        if not os.path.exists(path):
            if make_if_ne: return MCTS.create_mcts_save(path=path)
            raise RuntimeError("no such file")
        with open(path, "rb") as f: return pickle.load(f)



    def get_siblings(self, color):
        """gets the "sibling" tuples for the last played move, ie the (col, winner) for each move not played by player="color" last move"""
        last = self.last_move() # 1index last col played
        if last is None: raise RuntimeError("no last move durr")
        bd = self.board.copy()
        bd[self.top_in_col(bd, last-1)][last-1] = 0 # remove the last move in the board copy
        return [((xcol+1), self.get_winner_next(bd, xcol, color)) for xcol in self.getValidLocations() if xcol != (last-1)] # list of tuple of last's siblings (1indexed col, winner)

    def our_move(self) -> int:
        """(0index) keeps track of the tree and does mcts if necessary to expand. plays a winning move if avail, otherwise block opponent win if avail, otherwise best move based on mcts\n
        returns 0indexed column of mcts agent's move"""
        last = self.last_move() # get the last move of the game to move the tree there
        color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
        if last is not None: # except on the first move
            wins_none = None if self.winner == -1 else self.winner # map the -1 to None for self.winner, otherwise the color of the winner or 0draw
            opp = self.RED_INT if color==self.BLUE_INT else self.BLUE_INT # opponent color
            siblings = self.get_siblings(opp)
            self.tree = self.tree.get(last, wins_none, others=siblings) # move the tree to where the opponent went (and add siblings, add won't add twice) #TODO: make sure other nodes can be explored on other searches

        # TODO: we shouldnt need this "twice", during mcts and play...
        wins = self.winOrBlock() # see if we have a winning move
        if wins is not None: # we can either win or block a win
            winner = self.get_winner_next(self.board, wins, color) # get who "won" this move or block
            siblings = self.get_siblings(color) # get the sibling nodes
            self.tree = self.tree.get(wins+1, winner, others=siblings) # move the tree to this
            return wins # return the col to play
        
        boost = 0 # take less time if we have calculated to a big depth already
        try: 
            boost = self.tree.deepest-1
            if boost < 0: boost = 0
        except AttributeError: pass # mightve pickled an old version
        self.timed_search(boost=boost) # does mcts from our node TODO: change boost Node.n based?
        node = self.tree.highest() # get the most visited child
        tries = 0
        while node is None and tries < 5: # timed search w retry
            self.timed_search(retry=tries+1)
            node = self.tree.highest()
            # node = node if high is None else high
            tries += 1
        while node is None and tries > 0: # backup depth search
            self.search(to_depth=2)
            node = self.tree.highest()
            tries -= 1
        if node is None: raise RuntimeError("bad node waa")
        self.tree = node # move the tree to our move
        return int(node.state[-1])-1 # zero index col to play

    def isPlayable(self, r, c):
        availRow = self.getNextOpenRow(c) # see if threat is playable
        if availRow == r: return True #block imminent threat
        return False

    def load_move(self, move):
        """1index col: loads a certain move that was calculated already (either for us or other player). If game ends, turn is not incremented, ie when game ends, turn==winner or turn==draw"""
        if self.game_over: return self.winner
        color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
        col = move
        if col > 7 or col < 1: raise RuntimeError(f"bad load, range. move(1indx):{col}, turn:{self.turn}, color:{color}")
        if not self.isValidLocation(col-1): raise RuntimeError(f"bad load invalid. move(1indx):{col}, turn:{self.turn}, color:{color}, state(1indx):{self.save_game()}")
        col -= 1
        row = self.getNextOpenRow(col)
        self.dropChip(row, col, color)
        if self.gameIsWon(color):
            self.game_over = True
            self.winner = color
            return color
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
            return self.EMPTY
        if not self.game_over: self.turn += 1


    def go(self, move, monte_n=100):
        """1index col: move is the move that the opponent made. We load that up and then do a move calculated with our_move. Ie this is a full "turn" of both players. \n
        If game ends, self.turn is not incremented, ie when game ends, turn==winner or turn==draw"""
        if self.game_over: return self.winner
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
        column = self.our_move() # mcts magic happens here
        row = self.getNextOpenRow(column)
        self.dropChip(row, column, color)
        if self.gameIsWon(color):
            self.game_over = True
            self.winner = color
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
        if not self.game_over: self.turn += 1
        return column


    def start_interactive(self, humanPlayerNum=1):
        """start a game using heur1 and human goes first by default \n """
        stdout = sys.stdout
        color_names = {1:"RED",2:"BLUE"}
        self.clear()
        print(self)
        print()
        sys.stdout.flush()
        humanPlayerNum -= 1 #(1,2) -> 0 if human go first, else 1
        while not self.game_over:
            if self.turn % 2 == humanPlayerNum:
                color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
                col = int(input(f'{color_names[color]} please choose a column(1-7): '))
                while col > 7 or col < 1:
                    col = int(input('Invalid column, pick a valid one:'))
                while not self.isValidLocation(col-1):
                    col = int(input('Column is full. pick another one...'))
                col -= 1 # fix zero index
                     
                row = self.getNextOpenRow(col)
                self.dropChip(row, col, color)
                if self.gameIsWon(color):
                    self.game_over = True
                    self.winner = color
                     
            else:
                color = self.RED_INT if self.turn%2==0 else self.BLUE_INT
                column = self.our_move() # MCTS magic happens here 
                row = self.getNextOpenRow(column)
                self.dropChip(row, column, color)
                if self.gameIsWon(color):
                    self.game_over = True
                    self.winner = color
            if (not self.game_over) and len(self.getValidLocations()) == 0:
                self.game_over = True
                self.winner = self.EMPTY
            sys.stdout = stdout
            print(self)
            print()
            sys.stdout.flush()
            if not self.game_over: self.turn += 1
        self.gameover() # count this game as a rollout
        return self.pos

###############
# end classes #
###############

def mcts_vs_heur(mcts_first=True, playby=0, rec=False, inst:MCTS=None):
    """plays a full game of monte vs heuristic\n
    self monte_first to False if want heuristic to go first\n
    returns (monte_win, heur_win) \n
    -> (1,0) if monte win, (0,0) if tie, (0,1) if heur win"""
    # TODO: would be nice to have a game class and agents but whatever, two copies of the game it is
    m:MCTS = inst if inst is not None else MCTS()
    m.clear()
    h = C4() # heuristic game
    curr = m if mcts_first else h # current player starts as first player
    other = m if curr is h else h
    while not (m.game_over or h.game_over):
        last = curr.our_move() # MCTS or heuristic calculations here
        curr.load_move(last+1) # load is 1 indexed
        other.load_move(last+1)
        if playby > 1:
            print()
            print(m)
            print(m.save_game())
            sys.stdout.flush()
        curr, other = other, curr # swap whose turn it is 
    if m.winner!=h.winner:
        print()
        print(m)
        print(h)
        sys.stdout.flush()
        raise RuntimeError("game disagreement??")
    m.gameover() # count this game as a rollout bc why not
    mcts_player = 1 if mcts_first else 2
    heur_player = 2 if mcts_first else 1
    mcts_win = 1 if m.winner==mcts_player else 0
    heur_win = 1 if m.winner==heur_player else 0
    if playby > 0:
        print("\n")
        print(m)
        print(m.save_game()) # the string state
        # print(h)
        sys.stdout.flush()
    return (mcts_win, heur_win) if not rec else (mcts_win, heur_win, m.save_game())

def mcts_vs_rand(mcts_first=True, playby=0, inst:MCTS=None):
    """plays a full game of mcts vs random player\n
    set mcts_first to False if want random to go first\n
    returns (mcts, random_win) \n
    -> (1,0) if mcts win, (0,0) if tie, (0,1) if heur win \n
    can pass an instance of mcts to use (to save on tree loading time)"""
    # TODO: would be nice to have a game class and agents but whatever, two copies of the game it is
    m:MCTS = inst if inst is not None else MCTS()
    m.clear()
    if mcts_first: 
        m.load_move((m.our_move()+1))
        if playby > 1:
            print()
            print(m)
            print(m.save_game())
            sys.stdout.flush()
    while not m.game_over:
        m.go((m.randomMove()+1)) # mcts calculations happen in here
        if playby > 1:
            print()
            print(m)
            print(m.save_game())
            sys.stdout.flush()
    m.gameover() # count this game as a rollout
    mcts_player = 1 if mcts_first else 2
    rand_player = 2 if mcts_first else 1
    mcts_win = 1 if m.winner==mcts_player else 0
    rand_win = 1 if m.winner==rand_player else 0
    if playby == 1:
        print("\n")
        print(m)
        print(m.save_game()) # the string state
        sys.stdout.flush()
    return (mcts_win, rand_win)



if __name__ == "__main__":
    # ntr:Node = MCTS.load_mcts(path="tree8.pkl", make_if_ne=False)
    # m = MCTS(ntr) # load mcts from specific tree
    m = MCTS()
    print(f"Deepest: {m.tree.deepest}\n")
    # m.change_think_time(1, 5)
    m.start_interactive()
    print(m)
    m.cleanup() # save the tree that was modified by the online mcts


# %%
