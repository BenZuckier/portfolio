# Ben Zuckier AI Connect Four

## Files Inlcuded

I started working in the `connect_4.py` file but I decided to rewrite it as object oriented becuase games lend themselves well to that. So:

- `c4.py` has my implementation of the game and my algorithms to play it. Running this file has my AI play 100 games against random as player 1 and player 2 and prints how many times it loses. It rarely if ever loses.

- `driver_human_vs_heuristic1.py` has a driver for a human to play against my AI, either as player 1 or 2.

- `driver_human_vs_optimalAI.py` is mostly a prank but is by far my most clever agent. Give it a shot. I recommend playing as player 2, you can't win

## My heuristic1 AI

The heart of this agent is the heuristic1 AI. I decided that I didn't want to use a compute-heavy lookahead strategy like minimax or alphabeta pruning because that's no fun, computers are too powerful. Plus the way connect 4 was originally solved didn't involve brute forcing, I think. Anyway, I decided it would be more fun in general to make the logic of the heuristic play like an amateurish player would if they were really trying to be good. It looks ahead for a maximum of 1 move for itself and the opponent and uses some very straightforward guidelines to select its moves.

Overall, the only thing that the game board is really doing "extra" compared to the stock implementation (and the actual heuristic column selection) is keeping track per player of all their 3/4ths "threats" on the board, i.e. locations where placing that player's chip would cause a 4 in a row and win the game, or the "hole" in a four in a row. I considered doing this for 3-threats as well (ie places that would create a threat for a 3 in a row) but ultimately decided it was too complicated for my averageness AI and wanted to see how far we could get with just this.

### The results

This AI is (un?)surprisinly very good, and pretty fun to play against. It could use a tad more randomization, but overall it doesn't feel repetitive. I played it a lot and didn't win, and I had my roomate play it and he took a long time to think and still eventually lost. I also used my AI to play against an online AI (with myself as the middleman coordinator) and it beat this <https://www.mathsisfun.com/games/connect4.html> one on medium and pulled a draw on hard and put up a pretty good fight to this completely solved version <https://connect4.gamesolver.org/en> (but did lose, it was playing as p2 though which is disadvantageous).

### The logic

- First off, if we can win immediately, then win.

- If opponent will win immediately, then block.

If neither of the above are true then we pick the "best" moves considering the following criteria (in some order of relevance):

- Don't go under the opponent's winning spots

- Try to force the opp into blocking a threat that will then let us win by going under our winning spot (double trap setup)

- Try to go somewhere that makes two new playable threats, ie double trap

- Try to force opponent into letting us block their winning spot (threat) by making them go under their winning spot

- Try not to go under our winning spot unless that makes a double trap as above

- Try to increase the number of threats overall

- Try to block double trap setups that the opponent could do

- In the early game prefer center moves somewhat.

We assign each of these strategies a reward or penalty listed in this chart:

| UNDER_ENEMY | DOUBLE_TRAP | FORCE_BLOCK | THREAT_MULT | BLOCK_DOUBLE | UNDER_SELF |
|-------------|-------------|-------------|-------------|--------------|------------|
| 100         | 30          | 20          | 5 (per)     | 25           | 30         |

And in the early game we give columns these rewards respectively `EARLY_GAME =` [0,1,2,4,2,1,0]

Then we pick randomly among the best moves if there's a tie.
