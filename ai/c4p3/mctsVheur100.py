from __future__ import annotations
from functools import reduce
import time
import c4_mcts
from c4_mcts import Node, MCTS
import sys

if __name__ == "__main__":
    print("depth 20 starter now")
    print("loading tree20.pkl")
    sys.stdout.flush()
    
    ntr:Node = MCTS.load_mcts(path="tree20.pkl", make_if_ne=False)
    # m = MCTS()
    # think_t = (3,10)
    m = MCTS(start_tree=ntr)
    # m = MCTS(start_tree=ntr, think_tuple=think_t)
    m.set_no_color(True)
    print(f"Deepest: {m.tree.deepest}\n")
    sys.stdout.flush()
    # m.change_think_time(*think_t)
    # print(f"think time changed to between min={think_t[0]} and max={think_t[1]} seconds")
    sys.stdout.flush()
    ngames = 100
    # m = c4_mcts.MCTS()

    
    # %time games = [monte_vs_heur(monte_n=monte_n) for _ in range(ngames)]
    # scores = reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), games)
    # print(f"{ngames} heur games with monte_n={monte_n}:")
    # print(scores)
    
    games = []
    blocks = 10

    start = time.time()

    print(f"{ngames} games in blocks of {blocks} starting at {start}:\n")
    sys.stdout.flush()

    for i in range(blocks):
        print(f"\nblock: {i+1} of {blocks}")
        sys.stdout.flush()
        for _ in range(int(ngames/blocks)):
            game = c4_mcts.mcts_vs_heur(inst=m, playby=1)
            games.append(game)
            sys.stdout.flush()
        scores = reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), games[(i)*blocks:(i+1)*blocks])
        print(f"completed {(i+1)*blocks} of {ngames} in {time.time()-start: 0.2f}. Scores for this block: {scores}")
        sys.stdout.flush()
        if i != blocks-1: # don't save the last round...
            save_str = m.cleanup(addtl=f"t20v3_m1h{(i+1)*blocks}")
            print(f"saved tree as {save_str}")
        sys.stdout.flush()

    # games = [c4_mcts.mcts_vs_heur(inst=m, playby=1) for _ in range(ngames)]
    # games = [c4mcts_vs_rand(playby=0, inst=m) for _ in range(ngames)]
    end = time.time()
    print("done\n")
    sys.stdout.flush()
    
    # # %time games = [mcts_vs_rand() for _ in range(ngames)]
    scores = reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), games)
    print(f"Total of {ngames} heur games at tree=20v3:")
    print(games)
    print()
    print(f"scores:\n{scores}")
    print()
    sys.stdout.flush()


    print(end - start)
    secs = (end-start)/60.0
    print(f"Is {secs: 0.2f} minutes")
    sys.stdout.flush()


    # save_str = "t15v3_m1h100"
    save_str = m.cleanup(addtl="t20v3_m1h100")
    print(f"saved tree as {save_str}")
    sys.stdout.flush()

    # m.cleanup(addtl="t8v3_m1r50") # t is starting, m1 is mcts player 1, r50 is 50 rand games. pattern is startingTree_treeAddtion_treeAdditon..._