from __future__ import annotations
from functools import reduce
import time
import c4_mcts
from c4_mcts import Node, MCTS
import sys

if __name__ == "__main__":
    # ntr:Node = MCTS.load_mcts(path="v3_tree15.pkl", make_if_ne=False)
    m = MCTS()
    # m = MCTS(ntr)
    m.set_no_color(True)
    print("loaded tree")
    print(f"Deepest: {m.tree.deepest}\n")
    sys.stdout.flush()

    ngames = 50
    games = []
    
    start = time.time()
    print(f"start time: {start}\n")
    sys.stdout.flush()
    games = [c4_mcts.mcts_vs_rand(inst=m, playby=1) for _ in range(ngames)]
    end = time.time()
    
    scores = reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), games)
    print(f"{ngames} rand games at tree=t50_m1h200:")
    print(scores)
    print()
    sys.stdout.flush()

    print(f"time: {(end - start)}")
    secs = (end-start)/60.0
    print(f"Is {secs: 0.2f} mins")
    sys.stdout.flush()

    pname = m.cleanup(addtl="t50_m1h200_m1r50") 
    print(f"saved to {pname}")
    sys.stdout.flush()

    # m.cleanup(addtl="t8v3_m1r50") # t is starting, m1 is mcts player 1, r50 is 50 rand games. pattern is startingTree_treeAddtion_treeAdditon..._