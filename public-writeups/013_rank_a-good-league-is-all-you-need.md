# A Good League is All You Need

I trained an ~947k parameter actor for about 10 hours on an RTX 5090. Behavioural Cloning on leaderboard data from Sept. 27/28 and then a PPO self play league.

Highlights:
- About 2 hours before submission I recognized it was buying 3/4 land plots every game, so I gave it an entropy bonus. It seemed to improve its movement and trading Δ. but did not fix its collapsed strategy in time.
- I should have pretrained my critic on either the leaderboard data I cloned or my BC'd actor, and then it probably wouldn't have suffered from said strategy collapse.
- An ~800k parameter [lejepa](https://arxiv.org/html/2511.08544v3) backbone improved learning speed a lot, and made it easier to share parameters between the actor and critic without worrying about gradient conflict.
- A good league is incredibly important. You want only the toughest opponents, but that is a dynamic class, so I did screening of old versions with high posterior σ.
- Win/Draw/Loss CE critic seems to perform better than any soft reward based on bank-margin, or dense rewards on asset liquidity (which I figured might work as a proxy for final bank).

[code and more information](https://github.com/CarsonBurke/kaggriculture)