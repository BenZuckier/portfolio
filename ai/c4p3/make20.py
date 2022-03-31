from __future__ import annotations
import time
import c4_mcts
from c4_mcts import Node
import sys

if __name__ == "__main__":
    print("making tree to max depth=20")
    sys.stdout.flush()
    start = time.time()
    nowd: Node = c4_mcts.MCTS.create_mcts_save(20, "tree20v2.pkl")
    end = time.time()
    print(f"time: {(end - start)}")
    sys.stdout.flush()
    secs = (end-start)/60.0
    print(f"Is {secs: 0.2f} mins")
    sys.stdout.flush()
    print(f"root node's tree.deepest:{nowd.deepest}. tree.state:{nowd.state}. tree.n:{nowd.n}")
    sys.stdout.flush()
