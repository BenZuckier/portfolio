#%%
import numpy as np
import random
from termcolor import colored 
import math
from functools import partial, reduce
from itertools import repeat
import optimals
import time

class Game:
    #class/static variables
    ROW_COUNT, COLUMN_COUNT = 6, 7
    RED_CHAR, BLUE_CHAR = colored('X', 'red'), colored('O', 'blue')
    EMPTY, RED_INT, BLUE_INT = 0, 1 ,2

    def __init__(self) -> None:
        self.turn = 0
        self.board = Game.create_board().copy()
        self.game_over = False
        self.p1 = self.createPlayer(self.RED_INT)
        self.p2 = self.createPlayer(self.BLUE_INT)
        self.pos = [] #for https://connect4.gamesolver.org/en/?pos=

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
        # print(np.flip(board, 0))
        return " 1 2 3 4 5 6 7 \n" + "|" + (np.array2string(np.flip(np.flip(board, 1))).replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_").replace("1", Game.RED_CHAR).replace("2", Game.BLUE_CHAR).replace("\n", "|\n")) + "|"
    @staticmethod
    def print_board(board):
        """print current board with all chips put in so far"""
        print(""+Game.board_string(board))
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
        return Game.board_string(self.board)

    def clear(self):
        self.turn = 0
        self.board = Game.create_board().copy()
        self.game_over = False
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

    def remove(self, row, col):#row is redundant but whatever
        self.board[row,col] = 0

    def randomMove(self) -> int:
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

    def heuristic0(self):
        """bad heuristic of only the playbook of moves 0 and 1, otherwise random"""
        if self.turn <= 1: return self.book0or1()
        return self.randomMove()

    def perfectAI(self):
        """just assume that everyone plays optimally from here on out :) lol"""
        firstMove = -1
        for i in range(self.COLUMN_COUNT): # find first move spot
            if self.board[0][i] != 0:
                firstMove = i
                break
        self.board = np.array(optimals.optimal(firstMove)) #get the optimal game from the state
        return 0

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

    def start(self, heur=None, humanPlayerNum=1):
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
                    print(colored("Red wins!", 'red'))
                # winning_next_move = False
                     
            else:
                # valid_locations = self.getValidLocations()
                # column = random.choice(valid_locations)   # you can replace with input if you like... -- line updated with Gilad's code-- thanks!
                column = heur()
                row = self.getNextOpenRow(column)
                self.dropChip(row, column, self.BLUE_INT)
                self.pos.append(column+1)
                self.p2.trackThreats(row,column)
                if self.gameIsWon(self.BLUE_INT):
                    self.game_over = True
                    print(colored("Blue wins!", 'blue'))
            print(self)
            if (not self.game_over) and len(self.getValidLocations()) == 0:
                self.game_over = True
                print(colored("Draw!", 'blue','on_red'))
            self.turn += 1
        return self.pos
        

    #UGH ik ugly code and DRY violation but whatever 
    def start_ai_ai(self, ai1=None, ai2=None, slow=False, prints=True):
        """start a game ai vs ai using heuristics ai1 and ai2 respectively
        defaults to use heuristic1 for both """
        if ai1 == None: ai1=self.heuristic1
        if ai2 == None: ai2=self.heuristic1
        self.clear()
        if prints: print(self)
        winner = 0
        while not self.game_over:
            if slow:
                time.sleep(0.2)
            if self.turn % 2 == 0:
                column = ai1()
                row = self.getNextOpenRow(column)
                self.dropChip(row, column, self.RED_INT)
                self.pos.append(column+1)
                self.p1.trackThreats(row,column)
                if self.gameIsWon(self.RED_INT):
                    self.game_over = True
                    if prints: print(colored("Red wins!", 'red'))
                    winner = self.RED_INT
            else:
                # valid_locations = self.getValidLocations()
                # column = random.choice(valid_locations)   # you can replace with input if you like... -- line updated with Gilad's code-- thanks!
                column = ai2()
                row = self.getNextOpenRow(column)
                self.dropChip(row, column, self.BLUE_INT)
                self.pos.append(column+1)
                self.p2.trackThreats(row,column)
                if self.gameIsWon(self.BLUE_INT):
                    self.game_over = True
                    if prints: print(colored("Blue wins!", 'blue'))
                    winner = self.BLUE_INT
            if prints: print(self)
            if (not self.game_over) and len(self.getValidLocations()) == 0:
                self.game_over = True
                if prints: print(colored("Draw!", 'blue','on_red'))
            self.turn += 1
        return (winner, self.pos)

if __name__ == "__main__":
    g = Game()
    N_RUNS = 100
    games100 = [g.start_ai_ai(ai2=g.randomMove,prints=False) for _ in range(N_RUNS)]
    randomwins = [i[1] for i in games100 if i[0]==2]
    print(f"my AI lost {len(randomwins)} times out of {N_RUNS} games as p1")
    if len(randomwins) > 0: 
        for j in randomwins:
            for i in j:
                print(i, sep='', end='')
            print()
    games100two = [g.start_ai_ai(ai1=g.randomMove,prints=False) for _ in range(N_RUNS)]
    randomwinstwo = [i[1] for i in games100two if i[0]==1]
    print(f"my AI lost {len(randomwinstwo)} times out of {N_RUNS} games as p2")
    if len(randomwinstwo) > 0: 
        for j in randomwinstwo:
            for i in j:
                print(i, sep='', end='')
            print()
    # g.start(g.perfectAI)
# %%
