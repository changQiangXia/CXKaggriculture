# 2nd - Trading clutch, and no B200s harmed!

Train the 2nd place solution with **30 RTX 5090 hours**. 1.5K of plain python/pytorch available here: [Github/vmerckle/kaggriculture](https://github.com/vmerckle/kaggriculture), and download [the weights!](https://www.kaggle.com/models/vmerckle/kaggriculture-2nd-place)

My solution is a **wheat trading algorithm** on top of a 37M parameter network trained on supervised (BC). Wheat trading alone was **+$700** and took my win rate against MMPQ's top solution from **9% to 39%**. (A/B between my two final submissions)

Thanks to Kaggle for this game & format, and to all the top teams who made this intense until the final day!

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23854220%2F6053c4a66c9f7c76433134cb7840a83c%2Fwheat_trading_hours.png?generation=1793119846660618&alt=media)
(fig1: trading is a risky strat!)

# Solution

## The 37M parameter network

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23854220%2Fbb0440e325841d66bd4b830cda72b398%2Fmodel_schema.png?generation=1793118756554473&alt=media)

- A standard enc-dec transformer: a 19M-parameter encoder is used 719 times per game: for each hour, it reads 217 tokens (a summary token, the 200 tiles of both farms and 16 worker slots).
- Within each hour, a 17M-parameter decoder writes the hour's 26 actions one by one: 10 market orders first, then one per worker (16), each as (operation, item, quantity).
- A learned team embedding tells it which of the 23 cloned teams to imitate.

## The 30 hours training recipe

The weights that are submitted are from the 4 day rush to catch up to MMPQ, I didn't retrain from scratch then, so they went through many complex steps.
Here I describe the simplified recipe that reaches the same performance way faster.

1. Behavior cloning (BC), 25h:
   - 110K steps of 1.8k game hours each, AdamW, lr 1e-3 -> 1e-4 in 300 steps and cosine decay, weight decay 0.1, dropout 0.1.
   - The team input is hidden in 10% of game hours
2. Fine-tune on the top team for 600steps 1min, lr=5e-5:
3. PPO, 2h10min:
   - Starts from fine-tune step 600 and plays against older finetune checkpoints
   - 15 iterations of 688 games at temperature 0.5, each followed by 22 optimizer steps of 44 × 512 game hours.
   - lr 2e-5, 20 warmup steps, GAE λ = 1, target KL 0.05; 25% of each iteration's games replay games lost in earlier iterations (each lost game at most twice).

# Wheat trading

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23854220%2Fe603b287f0e8e1b09204ddea5138957e%2Fwheat_trading_toy.png?generation=1793118873081152&alt=media)

Wheat trading is something I actively prevented in all my RL attempts.

Wheat trading is a very attractive/annoying local minimum full of cycles for self-play.
You might waste many GPU hours just trying to sell wheat right before your opponent for a $10 gain instead of just producing more tomatoes.
So it's a very exploitable strat, except if you're the only one doing it, see fig1 at the top. :)

I took the gamble to never submit a wheat trading algorithm until my last minute submission, taking the risk to have it fail live!

# Supervised learning from leaderboard data (BC)

We used 22k games from the top 23 teams.
The most recently added games were played 15 hours before the deadline. Data parallelism on 8 GPUs gets the BC recipe down to 4 wall-clock hours.

# Two rules +$600

A bit more explanation of what a "rule" is.
After a forward pass, the two rules(+wheat trading algo) are applied and modify the actual actions sent, circumventing the normal process. 

- sell any end-of-day overflow (+$350 to +$800 depending on the network)
- endgame: force workers to walk to the shed and sell what they have in hand before the end (+$30 to +$180)

# Debugging

One big improvement was  making a few 'mini-game' settings with easy optimal strategies that helped debug and ground any ideas.
RL in general is so easy to get wrong, many mistakes do not matter until you're pushing for the limit of skill at the game.

# Why not top 1

1. I forgot to launch the last BC run, that is why the newest data is 15 hours old.
   - The last evening of the competition, we were hosting a research talk at the Tufa Labs office and I went slightly over Ballmer's peak.
2. I sent my first BC-powered network on the weekend before the deadline, on my way to Oktoberfest.
   - It reached the top 20 and I got motivated to join the fun. However, MMPQ had quite a lead and I had an Oktoberfest to enjoy...
   - It was so fun to catch up and pleasantly surprised to reach top2!
3. I couldn't find a compute-efficient local league setup!
   - That was my goal for the first weeks or so of the competition, and then I had to step away until the final week.
   - You can think of first 6-9days without new town shops to be some kind of meta or local basin of strategies.
   - Changing the meta requires a very good league

# Kaggriculture is hard for RL

This game has many traps for RL, one being that it might look like simple self-play RL is possible.

- Win rate and money margins only give a signal against mostly similar plans
	- 100% winrate against one solution predicts nothing about actual league ELO
- Money margin doesn't matter except against similar plans (it is an important signal when doing BC, however)
    - Too easy to sacrifice both of your production to fully disturb an opponent, cannot disturb them all.
- After a certain Elo (reached in a few days of competition), **total money doesn't matter**: opponents are already cutting total production to produce earlier, so any good plan has to account for what **ALL** the opponents might do. You usually cannot react, either: by the time you see a better plan, it is too late to switch.
- Each day and each hour contains small timing games (who sells wheat first). Self-play spends most of its policy updates on these, and they cycle (A > B > C > A), so nothing accumulates. The only way out is to execute better or start with a better plan.

# Conclusions & leaderboard league

In the early weeks, LLMs dominated the leaderboard, and then everyone imitated the top, and a few pushed the frontier with PPO.

A full self-play solution requires quite complex leagues to be compute-efficient.
The leaderboard was a very cheap and aligned league with many active competitors putting in compute and effort.
Many PPO attempts would end up having a weakness against one plan, and one loss meant you would wait 10 hours to reach the top of the leaderboard.

While 2nd place might only cost 30 GPU hours($10!), I obviously spent way more hours experimenting, debugging and, most importantly, learning.
I am not an expert in RL and I learned a lot.

Thanks again to Kaggle and everyone that put in efforts!