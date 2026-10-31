# Submission receipt: AM（用户授权提交，2026-09-23）

- file: /tmp/candidate_am.tar.gz（main.py = farm2945_dev/v57_advmirror.py）
  - tar sha256 556feaeaa9031fa642e5c8ebedf6ae7e7bc3a1ab433ddc6c425f32c49b512eae
  - main.py 1,070,876 B，sha256 a2d15ffd4a66cb1e253c1fc2ff2064b20a1df6cb7d6e301f06ed8c9fdb488eee
- composition: v57fix（snh48 + V57 资金顺序不变量）+ 镜像门控 advance_sales
  （leoprovorov MarketShock ice/fire 抢跑：similarity≥0.9 时把未来 2 步 premium
  SELL 提前，LOOKAHEAD=2，7 商品）。
- 护栏（提交前实测）：
  - 镜像 h2h 96 世界：AM vs v57 92W/30L 75.4% +11；**AM vs snh48 131W/31L
    80.9% +57**；
  - 257 池：AM 92.5% vs v57 91.8% / snh48 92.1%（V 桶 86% vs 84%）；
  - 真实板 194×2：AM vs v57 +16；**AM vs snh48 +68（54.6% 胜、tie 25.5%）**；
  - live 28-agent 场：85.8%（同场对比 AM vs v57 仍在后台跑）。
- 参数扫描（全收敛）：阈值 0.7-0.95 平台、判据不敏感、LOOKAHEAD=2 最优、
  7 商品最优、对称抢跑优于座位感知。
- 官方 loader 验证拾取 _roomguard_agent；tar 与本地文件字节一致。
- 剩余提交额度：2。
