from __future__ import annotations
import time
import c4_mcts
from c4_mcts import Node

if __name__ == "__main__":
    print("making tree to max depth=15")
    start = time.time()
    c4_mcts.MCTS.create_mcts_save(15, "tree15.pkl")
    end = time.time()
    print(end - start)
    secs = (end-start)/60.0
    print(f"Is {secs: 0.2f} mins")