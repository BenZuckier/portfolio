#%%
import numpy as np
import random
from termcolor import colored 
import math
from functools import reduce
from itertools import repeat


class Game:

    #class/static variables
    ROW_COUNT, COLUMN_COUNT = 6, 7
    RED_CHAR, BLUE_CHAR = colored('X', 'red'), colored('O', 'blue')
    EMPTY, RED_INT, BLUE_INT = 0, 1 ,2

    def __init__(self) -> None:
        self.turn = 0
        self.board = Game.create_board().copy()
        self.game_over = False
        self.winner = -1
        self.p1 = self.createPlayer(self.RED_INT)
        self.p2 = self.createPlayer(self.BLUE_INT)
        self.pos = [] #for https://connect4.gamesolver.org/en/?pos=


    @classmethod
    def load_game(cls, game_state):
        """pass an array of ints, one long int, or a string of the moves. ONE INDEXED \n
        returns a Game instance from that position
        """
        inst = cls()
        if game_state == None: raise RuntimeError("didn't load properly")
        if type(game_state) is not list and len(str(game_state))>0:
            game_state = [int(i) for i in str(game_state)]
        for m in game_state: inst.load_move(m)
        if not game_state == inst.pos: raise RuntimeError("didn't load properly")
        return inst


    def fours(self, r, c):
        """returns list of list of all the lines of four that include our piece (16theoretical max"""
        horizs = [[*zip(repeat(r),range(c-3,c+1))], [*zip(repeat(r),range(c-2,c+2))], [*zip(repeat(r),range(c-1,c+3))], [*zip(repeat(r),range(c,c+4))]]
        verts = [[*zip(range(r-3,r+1),repeat(c))], [*zip(range(r-2,r+2),repeat(c))], [*zip(range(r-1,r+3),repeat(c))], [*zip(range(r,r+4),repeat(c))]]
        diags = [[*zip(range(r-3,r+1),range(c-3,c+1))], [*zip(range(r-2,r+2),range(c-2,c+2))], [*zip(range(r-1,r+3),range(c-1,c+3))], [*zip(range(r,r+4),range(c,c+4))]]
        adiags = [[*zip(range(r-3,r+1),range(c+3,c-1,-1))], [*zip(range(r-2,r+2),range(c+2,c-2,-1))], [*zip(range(r-1,r+3),range(c+1,c-3,-1))], [*zip(range(r,r+4),range(c,c-4,-1))]]
        no_oob = lambda x: x[0][0] >= 0 and x[1][0] >= 0 and x[2][0] >= 0 and x[3][0] >= 0\
            and x[0][1] >= 0 and x[1][1] >= 0 and x[2][1] >= 0 and x[3][1] >= 0  \
            and x[0][0] < Game.ROW_COUNT and x[1][0] < Game.ROW_COUNT and x[2][0] < Game.ROW_COUNT and x[3][0] < Game.ROW_COUNT\
            and x[0][1] < Game.COLUMN_COUNT and x[1][1] < Game.COLUMN_COUNT and x[2][1] < Game.COLUMN_COUNT and x[3][1] < Game.COLUMN_COUNT
        horizs = [i for i in filter(no_oob, horizs)]
        verts = [i for i in filter(no_oob, verts)]
        diags = [i for i in filter(no_oob, diags)]
        adiags = [i for i in filter(no_oob, adiags)]
        # print("diags", diags)
        # print("adiags", adiags)
        return (horizs+verts+diags+adiags)
    
    def createPlayer(self, color):
        """makes a player that has access to the outer game class"""
        return Game.Player(self, color)

    class Player:
        def __init__(self, game, color) -> None: #makes a player that has access to the outer game class
            self.game:Game = game #the outer game class
            self.color = color
            self.threats = set() # spots we're threatening with 3 out of 4 in a row, sets of tuples
        def isMine(self, row, col):
            """return one if a square is mine, 0 if empty, -1 if enemy"""
            spot = self.game.board[row,col]
            if spot == self.color: return 1
            if spot == 0: return 0
            return -1 #enemy has spot
        def otherPlayer(self):
            """returns the other player"""
            return self.game.p2 if self.color == Game.RED_INT else self.game.p1
        def newThreats(self,r,c):
            """returns list of (row,col) of new threats we create"""
            if r == None: return 
            new_threats = []
            checks = self.game.fours(r, c)
            for i in checks: # i is an array of four tuples of row,col
                mines = [point for point in map(lambda x: self.isMine(*x), i)] #get the -1,0,1 scoring of the line of 4
                if reduce(lambda x,y:x+y,mines,0) >= 3: #threat!
                    for j in zip(mines,i):
                        if j[0] == 0: # if this is the "missing" part of the 4 
                            new_threats.append(j[1]) #add the row,col to threats
            return new_threats
        def trackThreats(self, r, c): # keep track of threats
            """update the spots that would end the game if we played it, 3/4 'hole'"""
            if r == None: return
            self.otherPlayer().threats.discard((r,c)) #remove the threat from other player if it existed
            news = self.newThreats(r,c)
            if news == None: news = []
            for i in news:
                self.threats.add(i) #add the row,col to threats

    

    #static methods
    @staticmethod
    def create_board():
        """create empty board for new game"""
        board = np.zeros((Game.ROW_COUNT, Game.COLUMN_COUNT), dtype=np.int8)
        return board
    @staticmethod
    def drop_chip(board, row, col, chip):
        """place a chip (red or BLUE) in a certain position in board"""
        if row == None: return
        board[row][col] = chip
    @staticmethod
    def is_valid_location(board, col):
        """check if a given row in the board has a room for extra dropped chip"""
        return board[Game.ROW_COUNT - 1][col] == 0
    @staticmethod
    def get_next_open_row(board, col):
        """assuming column is available to drop the chip,
        the function returns the lowest empty row  """
        for r in range(Game.ROW_COUNT):
            if board[r][col] == 0:
                return r
    @staticmethod
    def board_string(board):
        """return string of current board with all chips put in so far"""
        return " 1 2 3 4 5 6 7 \n" + "|" + (np.array2string(np.flip(np.flip(board, 1))).replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_").replace("1", Game.RED_CHAR).replace("2", Game.BLUE_CHAR).replace("\n", "|\n")) + "|"
    @staticmethod
    def print_board(board):
        """print current board with all chips put in so far"""
        win_str = ""
        if Game.game_is_won(board, board.RED_INT): win_str = f'\n{colored("Red wins!", "red")}'
        elif Game.game_is_won(board, board.BLUE_INT): win_str = f'\n{colored("Blue wins!", "blue")}'
        elif len(Game.get_valid_locations(board))==0: win_str = f'\n{colored("Draw!", "blue", "on_red")}'
        print(""+Game.board_string(board)+win_str)
    @staticmethod
    def game_is_won(board, chip):
        """check if current board contain a sequence of 4-in-a-row of in the board
        for the player that play with "chip"  """
        winning_Sequence = np.array([chip, chip, chip, chip])
        # Check horizontal sequences
        for r in range(Game.ROW_COUNT):
            if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[r, :]))):
                return True
        # Check vertical sequences
        for c in range(Game.COLUMN_COUNT):
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
        for col in range(Game.COLUMN_COUNT):
            if Game.is_valid_location(board, col):
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
        return Game.board_string(self.board) + win_str

    def clear(self):
        self.turn = 0
        self.board = Game.create_board().copy()
        self.game_over = False
        self.winner = -1
        self.p1 = self.createPlayer(self.RED_INT)
        self.p2 = self.createPlayer(self.BLUE_INT)
        self.pos = []

    def dropChip(self, row, col, chip):
        """INSTANCE METHOD to place a chip (red or BLUE) in a certain position in board"""
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

    def heuristic0(self) -> int:
        """bad heuristic of only the playbook of moves 0 and 1, otherwise random"""
        if self.turn <= 1: return self.book0or1()
        return self.randomMove()

    def heuristic1(self):
        """this heuristic implements logic that a skilled amateur human would exhibit\n
        i chose not to implement lookahead algorithms like minimax or alphabeta because i thought this would be more interesting
        to quantify how humans play well and because it felt like cheating.\n
        it uses the following logic: 
        if we can win immediately, then win. 
        if opponent will win immediately, then block. \n\n
        Now we pick the "best" moves considering the following: 
        dont go under the opp's winning spots, 
        try to force the opp into block a threat that lets us win by going under our winning spot (double trap setup), 
        try to go somewhere that makes 2 playable threats ie double trap,
        try to force opp to let us block their winning spot by making them go under their winning spot, 
        try not to go under our winning spot unless that makes a double trap, 
        try to increase the number of threats overall,
        try to block double trap setups that the opponent could do,
        in the early game prefer center moves a bit. \n
        Then we pick randomly from the best moves if theres a tie! (check out the weights in the code.)"""
        #some "hyperparams"
        UNDER_ENEMY, DOUBLE_TRAP, FORCE_BLOCK, THREAT_MULT, BLOCK_DOUBLE, UNDER_SELF, BLOCK_THREAT = 100, 30, 20, 8, 25, 30, 5
        EARLY_WEIGHT = [0,1,2,4,2,1,0] # prefer middle 
        EARLY_GAME = 9
        player:Game.Player = self.p1 if not (self.turn % 2) else self.p2
        if self.turn <= 1: return self.book0or1()
        #more openings book if we are player 1
        if self.turn == 2: # we are player 1 and it's our second move 
            if self.board[0,1] or self.board[0,2]: return 5 
            if self.board[0,4] or self.board[0,5]: return 1
        #TODO: add more books, maybe up until move 3 or something 
        moves = [(self.getNextOpenRow(i),i) for i in self.getValidLocations()] # all row,col pairs
        for (row,col) in moves: #if we can win then win
            self.dropChip(row,col,player.color) #check if winning spot
            if self.gameIsWon(player.color): 
                self.remove(row,col) # put back the board
                return col
            self.remove(row,col) # put back the board
        opp:Game.Player = player.otherPlayer() #check if other player is about to win and block
        opp_threats:set = opp.threats
        for spot in opp_threats: #spots row,col where the opponent is threatening us
            if self.isPlayable(*spot): return spot[1] # if threat playable, block imminent threat
        #now let's rank possible moves
        ranks = [0] * len(moves)
        for i in range(len(moves)):
            row, col = moves[i]
            # allThreats = self.allThreats()
            if (row+1,col) in opp_threats: 
                ranks[i] -= UNDER_ENEMY # DONT GO UNDER ENEMY ENDGAME SPOT!
            #TODO: dont let opponent go somewhere to block us
            # we really want to force a threat under our threats (double trap), 
            # and forcing a threat under their threat is nice (make them help us block)
            self.dropChip(row,col,player.color)#need to put the chip and remove for threat coutns
            news = player.newThreats(row,col) # list of (r,c) of new threats this move would create
            self.remove(row,col)#dont forget to remove after threat count lol
            if news == None: news = []
            doubletrap = False
            our_threats = player.threats # our current threats
            playable_news = list(filter(lambda x: self.isPlayable(*x), news))
            if (row+1,col) in our_threats and (row+2, col) in our_threats:
                ranks[i] += DOUBLE_TRAP
                doubletrap = True
            if len(playable_news) > 1: 
                ranks[i] += DOUBLE_TRAP
                doubletrap = True
            for threat_r, threat_c in news:
                if (threat_r+1, threat_c) in our_threats: # if our move makes a new threat that forces opp to go under our threat, double trap!
                    ranks[i] += DOUBLE_TRAP
                    doubletrap = True
                if (threat_r+1, threat_c) in opp_threats: # our moves forces opponent to let us block, nice
                    ranks[i] += FORCE_BLOCK
            if not doubletrap: #unless it's a double trap, don't go under our threat
                if (row+1, col) in our_threats:
                    ranks[i] -= UNDER_SELF
            ranks[i] += len(news)*THREAT_MULT # we want to make more threats
            # TODO: weight threats higher if they're lower down
            # TODO: add about threatening opponents threaten spot to neutralize it
            # TODO: add pref for blocking vs offensive if went first or not (even/odd control?)
            self.dropChip(row,col,opp.color)#need to put opponents chip and remove for threat coutns
            opp_news = opp.newThreats(row,col) #opponent's new threats for our moves if they were to go there instead
            self.remove(row,col)
            ranks[i] += len(opp_news)*BLOCK_THREAT
            opp_playable_news = list(filter(lambda x: self.isPlayable(*x), opp_news))
            # print(opp_news, opp_playable_news)
            if len(opp_playable_news) > 1: ranks[i] += BLOCK_DOUBLE
            if self.turn < EARLY_GAME:# early game, good to go towards center
                # TODO: maybe not so high up on center col?
                ranks[i] += EARLY_WEIGHT[col]
                if row > 3: ranks[i] + ((-2)*row)+2 #penalty for being too high up
        m = max(ranks)
        max_indexes = [i for i, j in enumerate(ranks) if j == m] #indexes of the max ranks
        pick_ind = random.choice(max_indexes)
        return (moves[pick_ind])[1] # col of our move to make
        
    def allThreats(self):
        return self.p1.threats.union(self.p2.threats)
    def isPlayable(self, r, c):
        availRow = self.getNextOpenRow(c) # see if threat is playable
        # if availRow == None: continue
        if availRow == r: return True #block imminent threat
        return False

    def load_move(self, move):
        if self.game_over: return self.winner#throw?
        player = self.p1 if self.turn%2==0 else self.p2
        col = move
        if col > 7 or col < 1: raise RuntimeError("bad load")
        if not self.isValidLocation(col-1): raise RuntimeError("bad load")
        col -= 1 # TODO: do we want 0 or 1 indexing
        row = self.getNextOpenRow(col)
        self.dropChip(row, col, player.color)
        self.pos.append(col+1)
        player.trackThreats(row,col)
        if self.gameIsWon(player.color):
            self.game_over = True
            self.winner = player.color
            return player.color # TODO: related to coloring above, what do we print when we win vs computer
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
            return self.EMPTY # draw? TODO: what ret
        self.turn += 1

    def our_move(self, monte_n=0) -> int:
        """wrapper around heur1 for runner class"""
        return self.heuristic1()

    def go(self, move):
        # TODO: should we return the move the pc made or the position state or the win flag or a tuple of some combination?
    # if self.turn % 2 == 0: # TODO: figure out coloring - we know this is always the human moving but who went first??
        if self.game_over: return self.winner#throw?
        player = self.p1 if self.turn%2==0 else self.p2
        col = move
        if col > 7 or col < 1: return -1
        if not self.isValidLocation(col-1): return -1
        col -= 1
        row = self.getNextOpenRow(col)
        self.dropChip(row, col, player.color)
        self.pos.append(col+1)
        player.trackThreats(row,col)
        if self.gameIsWon(player.color):
            self.game_over = True
            self.winner = player.color
            return None
            # return player.color # TODO: related to coloring above, what do we print when we win vs computer
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
            return None
            # return self.EMPTY # draw? TODO: what ret
        # computer always goes after user unless game is over
    # else:
        self.turn += 1 # player just went, need to incr turn
        player = self.p1 if self.turn%2==0 else self.p2
        column = self.heuristic1()
        row = self.getNextOpenRow(column)
        self.dropChip(row, column, player.color)
        self.pos.append(column+1)
        self.p2.trackThreats(row,column)
        if self.gameIsWon(player.color):
            self.game_over = True
            self.winner = player.color
            # return player.color # TODO: again, what do we return? 
        if (not self.game_over) and len(self.getValidLocations()) == 0:
            self.game_over = True
            self.winner = self.EMPTY
            # return self.EMPTY # draw? TODO: what ret
        self.turn += 1
        return column

    def start_interactive(self, heur=None, humanPlayerNum=1):
        """start a game using heur1 and human goes first by default \n
        """
        if heur == None: heur = self.heuristic1
        self.clear()
        print(self)
        humanPlayerNum -= 1 #(1,2) -> 0 if human go first, else 1
        while not self.game_over:
            if self.turn % 2 == humanPlayerNum:
                col = int(input("RED please choose a column(1-7): "))
                while col > 7 or col < 1:
                    col = int(input("Invalid column, pick a valid one: "))
                while not self.isValidLocation(col-1):
                    col = int(input("Column is full. pick another one..."))
                col -= 1
                     
                row = self.getNextOpenRow(col)
                self.dropChip(row, col, self.RED_INT)
                self.pos.append(col+1)
                self.p1.trackThreats(row,col)
                if self.gameIsWon(self.RED_INT):
                    self.game_over = True
                    # print(colored("Red wins!", 'red'))
                # winning_next_move = False
                     
            else:
                # valid_locations = self.getValidLocations()
                # column = random.choice(valid_locations)
                column = heur()
                row = self.getNextOpenRow(column)
                self.dropChip(row, column, self.BLUE_INT)
                self.pos.append(column+1)
                self.p2.trackThreats(row,column)
                if self.gameIsWon(self.BLUE_INT):
                    self.game_over = True
                    # print(colored("Blue wins!", 'blue'))
            print(self)
            if (not self.game_over) and len(self.getValidLocations()) == 0:
                self.game_over = True
                # print(colored("Draw!", 'blue','on_red'))
            self.turn += 1
        return self.pos
        

if __name__ == "__main__":
    g = Game()
    g.start_interactive()
# %%
