# destbreso 全部 37 篇言论综述（2026-09-23 爬取，除 8 篇旧读外新读 29 篇）

## 一、目标函数：Wins, not money
- 评分只按胜负走，不按分差：首个 14 局后，大胜和小胜的 rating 变化比 0.9:1.0
  （46,333 次 rating 更新实测）。**目标是 P(win)，不是 E(margin)**。
- margin 的价值只是"低噪声估计器"：单局 margin 标准差 ≈ 27,300，顶部对局一半
  由 <2,738 分差决定。tie 应按 0.5 胜计。

## 二、场子动力学
- 换血按 sweep：一个谱系 2 天占 25-50% 座位、5 天灭绝；场子半衰期 ~2.1 天
  （measure-twice 口径）。脚本一字不改也会掉分（2913→2731；asteriam 同款）。
- 周四周的榜首已从脚本变成 5 个私有 live policy——脚本的周期已过。

## 三、谱系/血缘仪器
- DNA test 的"day barcode"：只取每 day hour1-4 的结构通道（farmer/hands/
  结构订单，去掉 sells 和数量）hash → 30 个位点；首个不同位点 = 分叉日。
- 前缀 hash（turn 24/100/200/400/719）+ 模态归属：clone/descendant/mutation
  三级定义。fossil record 用 turn24 群、turn100 子群、turn200 孙群。

## 四、coverage 路线组合（现成配方）
- who-is-beating-you：on reveal 分叉 = 路由缺口 → 修法 coverage；between
  reveals = policy → flag。
- can-i-clone：爬全史 → stream hash 去重（238→19）→ 挂自己 dispatch、按世界
  序列最长前缀键控 → 强度带×世界矩阵终审。**不必学它的规则**。
- the-trades-were-paying-for-the-farm：卖掉"市场通道"的 knockout 40 局全败——
  **sell 序列就是融资序列**（sell 在 buy 前，9208/9208），收割路线必须连融资
  通道一起保留，不能自己重生成交易。
- dissecting-the-top-two：榜首 1/2 都是多路线组合 + 路线混合旋钮（A: 甜瓜20/
  草莓34；B: 甜瓜12/草莓42）。
- island-ga：四条产路线之路（手写规则/RL/照抄/搜索）；"owned schedule = moat"。

## 五、测量纪律（我们应立刻吸收）
- 同局同种子同座位同对手，逐局相减再求和（compare-two-agents：108 vs 107
  总胜、逐局 83 局落后 -7656、p=3e-7）。
- off-means-off 字节级校验；引擎行为校验而非版本字符串。
- 按"行为"数对手而不是名字（40 名 = 19 行为；8 名 = 4 行为）。
- 漏斗：transferability 过滤 → 去重 → 在声明的总体上线评 → 成对 live 裁决 →
  提交后不要过早读分。rating 稳定看局数不看小时。

## 六、经济/结构
- 一局钱有限且可闭式算；史上最佳 < 一半；场上普遍种了 2 倍于小麦可支付量。
- 关键决策 = "什么在成熟时还值钱"（共享订单簿），不是作物表。
- 一天 = 带时间窗的 Team Orienteering；顶尖脚本路由效率≈2.56×下界——别再手写
  路线，去抄/去搜。
- what-kind-of-optimisation：冻结 plan、只剩 market 数量；有模型就不该 RL；
  共享钱包下目标仍是 P(win)。

## 七、对我们计划的修订
- P0 遥测（静默损失台账）不变，外加六检查/逐局配对/池按行为去重。
- P1 收割 coverage：必须 ①去重 ②保留融资通道 ③按 64 有序世界键控 ④带×世界终审。
- P2 路由器：用 day-barcode 族谱 + "reveal 分叉=换线"规则；长线走 island-GA
  拥有自己的 schedule。
- 评价标准改为配对胜率/tie 率，margin 只当估计器；257 池去重并按 2.1 天半衰期
  刷新。
