# 机器安全规则（2026-09-24 迁移后，防 OOM/爆盘）

## 当前配置（实测）

| 项 | 值 |
|---|---|
| CPU | 12 核 |
| 内存 | `free` 显示宿主 503 GB，**但容器 cgroup 限额 ≈ 62 GB**（`/sys/fs/cgroup/memory.max` = 66.57e9）。**以 62 GB 为准**，峰值目标 < 20 GB |
| 系统盘 `/` | 30 GB，**仅剩 ~10 GB** |
| 数据盘 `/root/autodl-tmp` | 150 GB，剩 ~48 GB |
| 旧事故 | 一次性 `pq.read_table(...).to_pylist()` 读 1.26 GB parquet（10,030 条 replay JSON 全量物化）→ 旧机器 OOM |

## 硬规则

1. **禁止整表物化**：读 parquet 一律 `iter_batches`（或按 row group）
   分批处理，每批处理完立刻释放；单进程峰值内存目标 < 4 GB。
2. **多进程上限**：kagsim/评估类任务 workers ≤ 12；与后台守护进程共存时
   ≤ 10。
3. **临时文件放数据盘**：`/root/autodl-tmp/tmp_*`，不要写 `/tmp`（在只有
   10 GB 的系统盘上）；单个中间产物 >1 GB 先算空间。
4. **长任务必须后台化 + 断点续跑**：`setsid nohup ... &`，进度写日志，
   已完成产物存在则跳过（panel_search.py 已是此模式）。
5. **大 parquet 清单**（都在数据盘）：
   replays_2026-09f.parquet 1.26 GB（10,030 行）、09e 2.54 GB、09d 1.44 GB、
   07 35 MB。迁移丢了 08/08b/09/09b/09c 五个（非关键）。
6. **守护进程**（迁移后需重启，已重启）：
   - `georgy_watch_download.py`（base python，15 分钟轮询 09g）
   - `climber_watch.py`（kaggle-eval python，13 分钟轮询碰撞）
   日志：`/tmp/georgy_watch.log`、`/tmp/climber_watch.log`。
7. 资源巡检：`free -g`、`df -h /root/autodl-tmp`、`ps aux --sort=-%mem | head`。
