# candidate_h120ch99 之后所有提交 vs 好包（ch99 / archplus）的源码拆解

方法：把 90 个 tar 全部解包，剥掉 5 条超长数据行（占文件 90% 体积的压缩磁带表），对代码骨架做逐行 diff；再对每个包解析 `_SETTINGS`、41 条路线（逐条 md5）、路由器源码哈希。逐包明细见 `SOURCE_DIFF_TABLE_AFTER_CH99.csv`。

## 一、数据层只有三套磁带（41 条路线全同 / 全不同）

| 世代 | 包数 | 时间跨度 | 代表与线上分 |
|---|---:|---|---|
| A（v54/s1sd 磁带） | 44 | 09-19 → 09-27 | v54_stack_s1sd 2676、v54_stack_s1s 2590.9、snh48_系、am_y*/s1sd_y*/merge5/7/8、s1s_y2* |
| B（ch99/archplus 磁带） | 33 | 09-24 → 09-27 | archplus 2641.2、ch99 2558.5、snh8、final 2554.1、e2d*、sloth80 2338.9、or2*、pg576mir2 2544.0、idleharv 2415.9、stack500 2261.3、h120ch99_y2*、archplus_y2* |
| C（v50 老磁带） | 13 | 09-20 → 09-21 | v50_soft_v9 2475.4、v50_npf4 2514.3（旧实验） |

关键点：**ch99 与 archplus 用的是同一套磁带**；历史最好 v54_stack_s1sd(2676) 用的是另一套（A）。**A 与 B 之间 41/41 条路线全部不同**——这是最大的一处源码差异，但它不是某一次提交改出来的，而是两条并行血统。

## 二、路由器只有 4 个版本（21 → 33 行）

| 版本 | 首次出现 | 相对上一版的实际行为差异 |
|---|---|---|
| v0（ch99 原版） | ≤09-24 | step2 记录对手现金→rkey；day6 按商店签名选 `_R108_SHOP_ROUTES`（非 YARN）/`_R110_OLD_SHOPS`（YARN），`_V92_TABLE` 覆盖（YARN→9），`_V93_ROUTE_BY_RIVAL` 对手现金例外（→128）；day27→route 2 |
| v1（merge8） | 09-27 02:19 | +3 行：`if 'YARN_STORE' in shops: state['route']=126`（YARN 世界不再用 9/128） |
| v2（y2 代） | 09-27 02:53 | v1 再加一个例外：`... and set(shops) != {'BRUNCH_SPOT','YARN_STORE'}` |
| v3（规则包） | 09-27 04:38 | 在 v2 上加 day-12（step 288）换磁带：mid112（15 格表）/ surg（只改命中局）/ mid_seq |

⇒ 整个 y / y2 代与**自己血统的前身**的差别，逐对实测：

| 前身 → y2 包 | 代码差异 |
|---|---|
| candidate_h120ch99 → cand_h120ch99_y2 | **+7 / −0** |
| candidate_archplus → cand_archplus_y2 | **+7 / −0** |
| candidate_v54_stack_s1sd → cand_s1sd_y2 | **+7 / −0** |
| v54_…snk1_snh48 → cand_snh48_y2 | **+7 / −0** |
| cand_am_y → cand_am_y2 | **+6 / −4**（v1→v2 的签名例外） |
| cand_s1s_y2_base → v54_stack_s1s | **+0 / −7**（base 就是"去掉这条规则"的版本） |

即：**y2 代 = 前身 + 一段 7 行代码（YARN 世界换 126）**，没有其它行为改动。

## 三、ch99 vs archplus：只差 6 个常量和一处开屏

| 项 | ch99 | archplus |
|---|---:|---:|
| `_OR2_CAP` | 16 | 30 |
| `_OR2_SN_H` | 120 | 24 |
| `_OR2_SLOT_MARGIN` | 10.0 | 20.0（两处） |
| `_CH_SHED` | 99 | 90 |
| `_CXD_BUDGET` | 3200 | 800 |
| `_O_STEP1_PREFIX_B` | 存在（对手现金 2850-2950 的开屏变体） | 删除，统一用 `_O_STEP1_PREFIX` |

ch99(2558.5) 与 archplus(2641.2) 的线上差距 ≈ 这 6 个常数 + 1 处开屏简化。

## 四、ch99 之后每个包，本质都是几行代码

| 包（时间） | 代码差异 | 线上分 |
|---|---|---:|
| sloth12 / sloth20 / sloth80（09-25 21:26~22:23） | `_OR2_SLOT_H` 6/8 → 80（**2 行**） | sloth80 2338.9 |
| pge（09-26 02:56） | 相位门 slot horizon：早期 80 / 后期 8，step 480 切换（13 行） | — |
| or2off / or2sn0 / or2sn24 / or2sn4（09-26 04:59~05:25） | `agent = _OR2_PARENT`（1 行，关掉 OR2 层）；`_OR2_SN_H` 变体（2 行） | — |
| pg576mir / pg576mir2 / pareto（09-26 12:13~13:19） | 新增镜像检测 `_or2_sn_h(obs)`（26 行）：双方田块计数相同且现金差 ≤2000 → 用 120 长窗 | pg576mir2 2544.0 |
| idleharv_mir / stack_th336 / stack500 / combo_th336band500（09-26 18:09~21:50） | 新增 L3 idle 转换层（144~162 行） | 2415.9 / — / 2261.3 / — |
| merge5 / merge5fix / merge7（09-27 01:03~01:41） | 多臂合并（25~31 行） | — |
| merge6（09-27 01:19） | 五臂真并集：archplus 常数 + s1sd 常数（20/17 行） | — |
| **merge8（09-27 02:19）** | **+YARN→126**（9 行） | — |
| **y 代：am_y / s1sd_y / snh48_y（02:53~03:10）** | 同款 YARN→126，分别套在 A / B 两套磁带上 | — |
| **y2 代：am_y2 / s1sd_y2 / snh48_y2 / h120ch99_y2 / archplus_y2（03:10~04:18）** | v2：YARN→126，但排除 `{BRUNCH_SPOT, YARN_STORE}` | am_y2 2441.5、snh48_y2 1977.5 |
| mid / mid_seq（04:38~05:16） | day-12 两段版（59~66 行） | — |
| **mid112（05:54 / 10:18 / 10:53 / 11:26）** | day-12 起换 route 112 + 15 格例外表（23 行） | am_y2_mid112 2088.1、h99t 2102.5 |
| surg（16:41 / 16:58） | 同表但只对命中签名的局生效（23 行） | — |
| archplus_y2_mid112 / s1s_y2_mid112（18:05） | v2 + 112（无例外表） | 未提交 |

## 五、结论

1. 从 ch99 到今天候选，**代码级"创新"总量极小**：能称得上行为变化的只有四件——OR2 常数调整、镜像检测层、YARN→126、day-12→112；其余全是同一骨架的常数微调。
2. **单个常数就能决定本地好坏**：sloth 系唯一改动是 `_OR2_SLOT_H` 6/8→80；archplus 相对 ch99 也只有 6 个常数。这既说明"常数即收益"，也说明**本地对常数极度敏感 ⇒ 过拟合风险高**。
3. **YARN→126 是所有 y/y2/规则候选与好包之间唯一共同的行为差异**。若要给线上退化找"全体共享"的嫌疑点，它是第一个该 A/B 的对象（ch99/archplus 原版 vs y2 版）。
4. 逐包明细：`SOURCE_DIFF_TABLE_AFTER_CH99.csv`（90 包 × 日期 / 分数 / 磁带世代 / 路由器版本 / diff 行数）。
