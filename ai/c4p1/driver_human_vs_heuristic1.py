#%%
import c4

if __name__ == "__main__":
    g = c4.Game()
    first = 0
    while first < 1 or first > 2:
        first = int(input("Choose player 1 or 2 (type 1 or 2):"))
    g.start(heur=g.heuristic1, humanPlayerNum=first)