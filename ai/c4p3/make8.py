from __future__ import annotations
import time
import c4_mcts
from c4_mcts import Node
import sys

if __name__ == "__main__":
    print("making tree to max depth=8")
    sys.stdout.flush()
    start = time.time()
    nowd: Node = c4_mcts.MCTS.create_mcts_save(8, "test8.pkl")
    end = time.time()
    print(end - start)
    secs = (end-start)/60.0
    print(f"Is {secs: 0.2f} mins")
    print(f"root node's tree.deepest:{nowd.deepest}. tree.state:{nowd.state}. tree.n:{nowd.n}")
    sys.stdout.flush()