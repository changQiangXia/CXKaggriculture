# Submission receipt: snh48（用户授权提交）

- file: candidate_v54_stack_s1sdoca_rgs8f_snk1_snh48.tar.gz
  (main.py 1,070,012 B, sha256 4c6572a8dd34...)
- Kaggle ref: 56456489, submitted 2026-09-22 (PENDING)
- composition: s1s + Layer D(order-book) + room_guard/dead_stock + 常数调优
  （OR2_SLOT_MARGIN 20→8、CA_MARGIN -5→-15、OR2_SLOT_H 6→8、CA_FEED_DAYS 1→0、
  OR2_SN_K 0→1、OR2_SN_H 24→48）
- 护栏（提交前实测）：
  - live 全矩阵 56×64：95.1%、中位 +1938、均分 +2958（历史新高）；
  - 257 扩池：92.1%（V 桶 84%）；
  - 6 对手 72 世界 h2h 全部 ≥77%；镜像 0.0；
  - 8 场新鲜线上败局冻结重放：净 +7756（3 翻正 2 改善）。
- 官方 loader 验证拾取 _roomguard_agent；归档与本地文件字节一致。
- 剩余提交额度：3。
