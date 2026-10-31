# v3 线上回放损失模式

数据：58 局实际回放；CHEN Xiang 为 v3，23 胜负结果中的负局。回放约定：`steps[t+1]` 的 action 是 callback `t` 选择的动作，作用于 `steps[t]` 的 observation；结果状态记在 `steps[t+1]`；不把替换对手回放当因果证据。

## 总体

- 胜负：35 胜、23 负；胜负分差均值 907.8，负局均值 -646.1，中位数 -532.0。
- 负局中双方逐步完全相同的 action 比例均值 92.0%；这反映部分对手使用相同/近似 tape，不能只靠动作差判断强弱。
- 负局按分差：

|Episode|对手|seed|v3/对手终局|分差|相同 action 比例|
|---:|---|---:|---:|---:|---:|
|110065863|Debmalya|1906337675|53004/55903|-2899|93.3%|
|110065738|yukio|292399891|72321/74162|-1841|92.2%|
|110068976|Kilupy|451123334|74671/76205|-1534|88.0%|
|110096055|Debmalya|674191907|103519/104569|-1050|89.4%|
|110086280|Jules|1105013480|130713/131720|-1007|91.1%|
|110101498|xi luo|856884331|111137/111976|-839|95.1%|
|110061427|Ryota-Di|999631866|98965/99769|-804|87.5%|
|110079805|Han Chen|1687303310|112608/113345|-737|96.0%|
|110051331|Aura Farming|1305666881|100434/101124|-690|85.3%|
|110081967|Amyel21|1292252155|95332/95933|-601|90.7%|
|110085201|Silhouette|616968264|74916/75453|-537|95.5%|
|110066822|lemon13418|185891267|124270/124802|-532|67.7%|
|110071610|nena|1457157189|100840/101291|-451|91.2%|
|110093867|Affriza Wildan Fauzan|1238396659|67290/67728|-438|95.5%|
|110089535|ansheng jhang|1812008023|106557/106819|-262|93.7%|
|110075468|Yanis Belami|893198257|120376/120601|-225|91.7%|
|110051646|Unkn0wn|258810144|97204/97321|-117|94.2%|
|110077640|s_a_ai_engineer|392397189|122048/122161|-113|99.2%|
|110072246|pig7selene|2140122705|69730/69823|-93|80.1%|
|110090621|Marti|907787993|73770/73798|-28|99.9%|
|110074399|KOSUKE MATSUDA|1522193321|138995/139023|-28|99.9%|
|110101510|Akshay Mathur|1321067649|107549/107575|-26|99.7%|
|110084132|Rifqi Haikal|1798975081|101811/101820|-9|99.9%|

## 官方内核逐 callback 核对与成交归因

从每个真实 `observation[t]` 开始，采用 `steps[t+1]` 的双方实际 action，调用官方 `_apply_unit_action` 与 `_process_market`。五局合计 3595 个 callback，现金与下一条回放 observation 全部吻合，0 mismatch。产量来自实际执行 HARVEST/COLLECT_FERTILIZER 后库存增量；成交量来自官方 `_commit_unit` 成功记录。它们均为事实账本，不是请求数量。

|Episode|对手|v3 实际产量|对手实际产量|
|---:|---|---|---|
|110065863|Debmalya|FERTILIZER=369, WHEAT=587, WOOL=99, MILK=147, EGG=161, MELON=72, STRAWBERRY=249, CARROT=107|FERTILIZER=369, WHEAT=590, WOOL=99, MILK=147, EGG=161, MELON=72, STRAWBERRY=249, CARROT=107|
|110065738|yukio|FERTILIZER=357, WHEAT=544, WOOL=239, MILK=160, MELON=72, STRAWBERRY=247, CARROT=110|FERTILIZER=373, WHEAT=547, WOOL=261, MILK=160, MELON=72, STRAWBERRY=249, CARROT=110|
|110051331|Aura Farming|FERTILIZER=368, WHEAT=540, WOOL=105, MILK=152, MELON=72, EGG=147, STRAWBERRY=249, CARROT=133|FERTILIZER=368, WHEAT=540, WOOL=105, MILK=152, MELON=66, EGG=147, STRAWBERRY=249, CARROT=133|
|110074399|KOSUKE MATSUDA|FERTILIZER=373, WHEAT=585, WOOL=273, MILK=190, MELON=72, STRAWBERRY=249, CARROT=87|FERTILIZER=373, WHEAT=585, WOOL=273, MILK=190, MELON=72, STRAWBERRY=249, CARROT=87|
|110084132|Rifqi Haikal|FERTILIZER=370, WHEAT=609, WOOL=155, MILK=176, MELON=72, EGG=149, STRAWBERRY=249, CARROT=92|FERTILIZER=370, WHEAT=609, WOOL=155, MILK=176, MELON=72, EGG=149, STRAWBERRY=249, CARROT=92|

五局交易数据都保存在 `transactions_<episode>.json`，其中含逐 callback 单位、金额、成交价范围、原始双方 action 与整局汇总。

|Episode|现金贡献差 v3−对手|贡献差总和|
|---:|---|---:|
|110065863|BUY_PRODUCT:WHEAT -3011；SELL:WHEAT +604；SELL:STRAWBERRY -423；SELL:MILK -52；SELL:WOOL -11；BUY_SEED:WHEAT +10；SELL:CARROT -8；BUY_PRODUCT:FERTILIZER -7；SELL:EGG -1|-2899|
|110065738|SELL:WOOL -2045；SELL:WHEAT +1001；BUY_PRODUCT:WHEAT -504；BUY_ANIMAL:SHEEP +500；SELL:FERTILIZER -428；SELL:MILK -310；BUY_PRODUCT:FERTILIZER -31；SELL:CARROT -18；SELL:STRAWBERRY -16；BUY_SEED:WHEAT +10|-1841|
|110051331|SELL:WHEAT -1600；BUY_PRODUCT:WHEAT +1288；SELL:MELON +1258；SELL:CARROT -1011；SELL:EGG -360；SELL:MILK -331；SELL:STRAWBERRY +128；BUY_SEED:MELON -80；BUY_PRODUCT:FERTILIZER +45；SELL:FERTILIZER -16；SELL:WOOL -11|-690|
|110074399|BUY_PRODUCT:WHEAT -559；SELL:WHEAT +531|-28|
|110084132|BUY_PRODUCT:WHEAT -659；SELL:WHEAT +650|-9|

三局的关键解释：

- **Debmalya，110065863，终局 −2899。** 除小麦产量 587 vs 590，其余实际收获量一致；小麦买卖净现金为 v3 10146、对手 12553，差 −2407。草莓同卖249，收入7152 vs7575，差−423。其余金额在表中，所有交易贡献差相加恰好等于终局分差。callback300，双方买WHEAT48，v3先BUY_SEED再BUY_PRODUCT、对手反序，实付2080 vs2010（差70）；callback368双方买89，3889 vs3656（差233）；callback524双方买90，3940 vs3700（差240）。这是竞争下动态商品购买槽位滞后造成的实际成本差。
- **yukio，110065738，终局 −1841。** callback217 双方发出同一 SELL FERTILIZER1→HIRE→BUY_ANIMAL SHEEP2：起始现金847 vs965，双方卖肥81，HIRE后v3只成功买1只羊，对手买2只。整局v3共买10只羊、对手11只；实际羊毛239 vs261、肥料357 vs373。羊毛收入差−2045，肥料−428，少买羊省500，其他贡献如表。callback406，羊毛实际卖2收入464 vs卖8收入1850；这一次现金差恶化1386。现金曾暂时领先只是少投入500，不能视为生产更强。
- **Aura Farming，110051331，终局 −690。** v3实际比对手多收6MELON，产胡萝卜均133、牛奶均152、鸡蛋均147。最后胡萝卜都卖133但收入60832 vs61843，少1011；牛奶收入4910 vs5241少331。鸡蛋v3卖139、对手147，少8枚。逐夜实物核对：callback503 v3溢出4蛋，callback551溢出2蛋+7麦，callback575溢出2蛋+4麦；对手对应夜晚均无这些丢弃。callback696双方有40胡萝卜，v3卖36小麦收762、对手卖32胡萝卜收16065；v3等下一回合才卖33胡萝卜。最终胡萝卜数量相同而收入不同，关键是销售时机。
- **近乎镜像两局。** 110074399（KOSUKE MATSUDA）所有非小麦成交、全商品收获一致，终局−28全部来自小麦买卖净现金差；110084132（Rifqi Haikal）同理终局−9全部来自小麦。两局双方仅开场订单量不同（v3=25，对手=5/1）等极少动作不同，比赛按现金胜负，几十元也足以输一局。

方法边界：部分 JSON 留有以实际同时对手动作固定、仅改当前回合买单顺序的 `within_turn_product_priority_counterfactual` 字段，目的是检查当前回合的结算机制。它不重放未来，不能相加成整场收益，也不证明修改后的线上提升。报告的归因表全部基于真实双方行动，无需该反事实字段。

结论：这些代表局主要差在竞争市场中的动态商品购买顺序、资金不足导致投资缺口、提前销售与夜间容量管理。不能据此把 v3 的 2397 分唯一归因于某个漏洞；该58局样本不是随机代表全线上对手，也没有足够不同生产范式的负局样本。其提供的是可复验的亏损机制和下一轮对抗测试目标。

## 三局代表回放

### Episode 110065863：Debmalya，分差 -2899

终局：v3 53004，对手 55903；双方 callback action 相同 93.3%（671/719）。

每日 callback=day*24 的现金差：

|day|v3 cash|opp cash|v3-opp|
|---:|---:|---:|---:|
|0|3000|3000|0|
|1|13|43|-30|
|2|102|103|-1|
|3|215|216|-1|
|4|267|297|-30|
|5|677|707|-30|
|6|790|820|-30|
|7|1313|1350|-37|
|8|702|770|-68|
|9|1208|1339|-131|
|10|1959|2090|-131|
|11|13763|13896|-133|
|12|12732|12865|-133|
|13|15310|15581|-271|
|14|17020|17399|-379|
|15|19049|19430|-381|
|16|21434|22280|-846|
|17|24607|25638|-1031|
|18|26859|27890|-1031|
|19|28541|29758|-1217|
|20|29334|30756|-1422|
|21|30191|31805|-1614|
|22|31271|33123|-1852|
|23|32230|34085|-1855|
|24|33402|35258|-1856|
|25|34463|36319|-1856|
|26|36480|38622|-2142|
|27|38019|40848|-2829|
|28|39824|42711|-2887|
|29|44112|46999|-2887|

关键时刻库存和位置：

|t|v3 cash|opp cash|v3 shed/held|opp shed/held|v3 pos|opp pos|
|---:|---:|---:|---|---|---|---|
|0|3000|3000|0/0|0/0|[4, 4]|[4, 4]|
|24|13|43|3/0|3/0|[4, 4]|[4, 4]|
|48|102|103|7/0|8/0|[4, 4]|[4, 4]|
|96|267|297|9/0|12/0|[4, 4]|[4, 4]|
|192|702|770|7/0|9/0|[4, 4]|[4, 4]|
|288|12732|12865|80/0|80/0|[4, 4]|[4, 4]|
|432|26859|27890|67/0|67/0|[4, 4]|[4, 4]|
|576|33402|35258|96/0|96/0|[4, 4]|[4, 4]|
|648|38019|40848|91/0|91/0|[4, 4]|[4, 4]|
|696|44112|46999|98/0|98/0|[4, 4]|[4, 4]|
|719|53004|55903|0/0|0/0|[5, 4]|[5, 4]|

前 12 个双方动作分歧（动作只表示回放事实，不代表替换后会有同一状态）：

- callback=0（recorded step=1，动作作用于 observation[callback] 状态）day=0 h=0
  - v3 `{'farmer': ['PASS'], 'hands': [], 'market': [['BUY_PRODUCT', 'WHEAT', 25], ['SELL', 'WHEAT', 25]]}`
  - opp `{'farmer': ['PASS'], 'hands': [], 'market': [['BUY_PRODUCT', 'WHEAT', 10], ['SELL', 'WHEAT', 10]]}`
- callback=20（recorded step=21，动作作用于 observation[callback] 状态）day=0 h=20
  - v3 `{'farmer': ['PASS'], 'hands': [['WEST'], ['PASS'], ['PASS'], ['PLANT', 'WHEAT'], ['NORTH']], 'market': [['BUY_SEED', 'WHEAT', 1]]}`
  - opp `{'farmer': ['PASS'], 'hands': [['WEST'], ['PASS'], ['PASS'], ['PLANT', 'WHEAT'], ['NORTH']], 'market': [['BUY_SEED', 'WHEAT', 2]]}`
- callback=21（recorded step=22，动作作用于 observation[callback] 状态）day=0 h=21
  - v3 `{'farmer': ['PASS'], 'hands': [['PLANT', 'WHEAT'], ['PASS'], ['PASS'], ['WATER'], ['PASS']], 'market': []}`
  - opp `{'farmer': ['PASS'], 'hands': [['PLANT', 'WHEAT'], ['PASS'], ['PASS'], ['WATER'], ['PLANT', 'WHEAT']], 'market': []}`
- callback=96（recorded step=97，动作作用于 observation[callback] 状态）day=4 h=0
  - v3 `{'farmer': ['PICKUP', 'WHEAT', 5], 'hands': [], 'market': [['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['SELL', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['PICKUP', 'WHEAT', 5], 'hands': [], 'market': [['SELL', 'FERTILIZER', 1], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']]}`
- callback=120（recorded step=121，动作作用于 observation[callback] 状态）day=5 h=0
  - v3 `{'farmer': ['WEST'], 'hands': [], 'market': [['HIRE'], ['HIRE'], ['HIRE'], ['SELL', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['WEST'], 'hands': [], 'market': [['SELL', 'FERTILIZER', 1], ['HIRE'], ['HIRE'], ['HIRE']]}`
- callback=150（recorded step=151，动作作用于 observation[callback] 状态）day=6 h=6
  - v3 `{'farmer': ['EAST'], 'hands': [['PLACE', 'WOOL', 6], ['NORTH'], ['CARE'], ['WATER'], ['COLLECT_FERTILIZER'], ['CARE'], ['SOUTH']], 'market': [['SELL', 'WOOL', 4], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2], ['BUY_PRODUCT', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['EAST'], 'hands': [['PLACE', 'WOOL', 6], ['NORTH'], ['CARE'], ['WATER'], ['COLLECT_FERTILIZER'], ['CARE'], ['SOUTH']], 'market': [['SELL', 'WOOL', 4], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2]]}`
- callback=163（recorded step=164，动作作用于 observation[callback] 状态）day=6 h=19
  - v3 `{'farmer': ['PLANT', 'STRAWBERRY'], 'hands': [['PLANT', 'STRAWBERRY'], ['PLANT', 'WHEAT'], ['WATER'], ['WATER'], ['WEST'], ['PLANT', 'WHEAT'], ['PLANT', 'STRAWBERRY']], 'market': []}`
  - opp `{'farmer': ['PLANT', 'STRAWBERRY'], 'hands': [['PLANT', 'STRAWBERRY'], ['PLANT', 'WHEAT'], ['WATER'], ['WATER'], ['WEST'], ['PLANT', 'WHEAT'], ['PLANT', 'STRAWBERRY']], 'market': [['SELL', 'WOOL', 2]]}`
- callback=170（recorded step=171，动作作用于 observation[callback] 状态）day=7 h=2
  - v3 `{'farmer': ['FEED'], 'hands': [['WEST'], ['NORTH'], ['PICKUP', 'COW'], ['FEED'], ['WEST'], ['EAST'], ['NORTH']], 'market': [['BUY_PRODUCT', 'WHEAT', 1]]}`
  - opp `{'farmer': ['FEED'], 'hands': [['WEST'], ['NORTH'], ['PICKUP', 'COW'], ['FEED'], ['WEST'], ['EAST'], ['NORTH']], 'market': []}`
- callback=194（recorded step=195，动作作用于 observation[callback] 状态）day=8 h=2
  - v3 `{'farmer': ['COLLECT_FERTILIZER'], 'hands': [['HARVEST'], ['PICKUP', 'WHEAT'], ['NORTH'], ['PICKUP', 'WHEAT'], ['FEED'], ['FEED'], ['NORTH'], ['NORTH']], 'market': [['BUY_PRODUCT', 'WHEAT', 2]]}`
  - opp `{'farmer': ['COLLECT_FERTILIZER'], 'hands': [['HARVEST'], ['PICKUP', 'WHEAT'], ['NORTH'], ['PICKUP', 'WHEAT'], ['FEED'], ['FEED'], ['NORTH'], ['NORTH']], 'market': []}`
- callback=196（recorded step=197，动作作用于 observation[callback] 状态）day=8 h=4
  - v3 `{'farmer': ['EAST'], 'hands': [['DROP'], ['NORTH'], ['NORTH'], ['FEED'], ['PLACE', 'MILK', 6], ['COLLECT_FERTILIZER'], ['NORTH'], ['WEST']], 'market': [['SELL', 'MILK', 12], ['BUY_PRODUCT', 'WHEAT', 6], ['BUY_ANIMAL', 'SHEEP', 2], ['BUY_PRODUCT', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['EAST'], 'hands': [['DROP'], ['NORTH'], ['NORTH'], ['FEED'], ['PLACE', 'MILK', 6], ['COLLECT_FERTILIZER'], ['NORTH'], ['WEST']], 'market': [['SELL', 'MILK', 12], ['BUY_PRODUCT', 'WHEAT', 6], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_ANIMAL', 'SHEEP', 2]]}`
- callback=217（recorded step=218，动作作用于 observation[callback] 状态）day=9 h=1
  - v3 `{'farmer': ['FEED'], 'hands': [['PICKUP', 'WHEAT'], ['WEST'], ['NORTH'], ['PICKUP', 'WHEAT', 2], ['CARE'], ['EAST'], ['NORTH'], ['PICKUP', 'WHEAT', 3]], 'market': [['BUY_ANIMAL', 'SHEEP', 1], ['BUY_PRODUCT', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['FEED'], 'hands': [['PICKUP', 'WHEAT'], ['WEST'], ['NORTH'], ['PICKUP', 'WHEAT', 2], ['CARE'], ['EAST'], ['NORTH'], ['PICKUP', 'WHEAT', 3]], 'market': [['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_ANIMAL', 'SHEEP', 1]]}`
- callback=241（recorded step=242，动作作用于 observation[callback] 状态）day=10 h=1
  - v3 `{'farmer': ['WEST'], 'hands': [['WEST'], ['WEST'], ['WEST'], ['WEST'], ['NORTH'], ['WEST'], ['WEST'], ['NORTH'], ['WEST']], 'market': [['HIRE'], ['HIRE'], ['BUY_ANIMAL', 'GOOSE', 2], ['BUY_PRODUCT', 'FERTILIZER', 3]]}`
  - opp `{'farmer': ['WEST'], 'hands': [['WEST'], ['WEST'], ['WEST'], ['WEST'], ['NORTH'], ['WEST'], ['WEST'], ['NORTH'], ['WEST']], 'market': [['BUY_PRODUCT', 'FERTILIZER', 3], ['HIRE'], ['HIRE'], ['BUY_ANIMAL', 'GOOSE', 2]]}`

### Episode 110065738：yukio，分差 -1841

终局：v3 72321，对手 74162；双方 callback action 相同 92.2%（663/719）。

每日 callback=day*24 的现金差：

|day|v3 cash|opp cash|v3-opp|
|---:|---:|---:|---:|
|0|3000|3000|0|
|1|13|43|-30|
|2|102|103|-1|
|3|215|216|-1|
|4|267|297|-30|
|5|677|707|-30|
|6|790|820|-30|
|7|1019|1049|-30|
|8|508|626|-118|
|9|1061|1179|-118|
|10|2485|2202|283|
|11|15147|14486|661|
|12|12726|12332|394|
|13|16323|16081|242|
|14|17673|17431|242|
|15|20010|19621|389|
|16|27666|27343|323|
|17|32898|34058|-1160|
|18|37530|38692|-1162|
|19|41391|42551|-1160|
|20|43985|45176|-1191|
|21|46258|48118|-1860|
|22|48679|50539|-1860|
|23|50188|52075|-1887|
|24|51733|53473|-1740|
|25|52238|53995|-1757|
|26|53602|55406|-1804|
|27|54127|55898|-1771|
|28|56312|58134|-1822|
|29|61506|63332|-1826|

关键时刻库存和位置：

|t|v3 cash|opp cash|v3 shed/held|opp shed/held|v3 pos|opp pos|
|---:|---:|---:|---|---|---|---|
|0|3000|3000|0/0|0/0|[4, 4]|[4, 4]|
|24|13|43|3/0|3/0|[4, 4]|[4, 4]|
|48|102|103|7/0|8/0|[4, 4]|[4, 4]|
|96|267|297|9/0|12/0|[4, 4]|[4, 4]|
|192|508|626|10/0|10/0|[4, 4]|[4, 4]|
|288|12726|12332|72/0|71/0|[4, 4]|[4, 4]|
|432|37530|38692|54/0|54/0|[4, 4]|[4, 4]|
|576|51733|53473|100/0|100/0|[4, 4]|[4, 4]|
|648|54127|55898|100/0|100/0|[4, 4]|[4, 4]|
|696|61506|63332|97/0|97/0|[4, 4]|[4, 4]|
|719|72321|74162|0/0|0/0|[5, 4]|[5, 4]|

前 12 个双方动作分歧（动作只表示回放事实，不代表替换后会有同一状态）：

- callback=0（recorded step=1，动作作用于 observation[callback] 状态）day=0 h=0
  - v3 `{'farmer': ['PASS'], 'hands': [], 'market': [['BUY_PRODUCT', 'WHEAT', 25], ['SELL', 'WHEAT', 25]]}`
  - opp `{'farmer': ['PASS'], 'hands': [], 'market': [['BUY_PRODUCT', 'WHEAT', 10], ['SELL', 'WHEAT', 10]]}`
- callback=20（recorded step=21，动作作用于 observation[callback] 状态）day=0 h=20
  - v3 `{'farmer': ['PASS'], 'hands': [['WEST'], ['PASS'], ['PASS'], ['PLANT', 'WHEAT'], ['NORTH']], 'market': [['BUY_SEED', 'WHEAT', 1]]}`
  - opp `{'farmer': ['PASS'], 'hands': [['WEST'], ['PASS'], ['PASS'], ['PLANT', 'WHEAT'], ['NORTH']], 'market': [['BUY_SEED', 'WHEAT', 2]]}`
- callback=21（recorded step=22，动作作用于 observation[callback] 状态）day=0 h=21
  - v3 `{'farmer': ['PASS'], 'hands': [['PLANT', 'WHEAT'], ['PASS'], ['PASS'], ['WATER'], ['PASS']], 'market': []}`
  - opp `{'farmer': ['PASS'], 'hands': [['PLANT', 'WHEAT'], ['PASS'], ['PASS'], ['WATER'], ['PLANT', 'WHEAT']], 'market': []}`
- callback=96（recorded step=97，动作作用于 observation[callback] 状态）day=4 h=0
  - v3 `{'farmer': ['PICKUP', 'WHEAT', 5], 'hands': [], 'market': [['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['SELL', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['PICKUP', 'WHEAT', 5], 'hands': [], 'market': [['SELL', 'FERTILIZER', 1], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']]}`
- callback=120（recorded step=121，动作作用于 observation[callback] 状态）day=5 h=0
  - v3 `{'farmer': ['WEST'], 'hands': [], 'market': [['HIRE'], ['HIRE'], ['HIRE'], ['SELL', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['WEST'], 'hands': [], 'market': [['SELL', 'FERTILIZER', 1], ['HIRE'], ['HIRE'], ['HIRE']]}`
- callback=150（recorded step=151，动作作用于 observation[callback] 状态）day=6 h=6
  - v3 `{'farmer': ['EAST'], 'hands': [['PLACE', 'WOOL', 6], ['NORTH'], ['CARE'], ['WATER'], ['COLLECT_FERTILIZER'], ['CARE'], ['SOUTH']], 'market': [['SELL', 'WOOL', 4], ['SELL', 'FERTILIZER', 1], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_LAND'], ['BUY_ANIMAL', 'COW', 2], ['BUY_PRODUCT', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['EAST'], 'hands': [['PLACE', 'WOOL', 6], ['NORTH'], ['CARE'], ['WATER'], ['COLLECT_FERTILIZER'], ['CARE'], ['SOUTH']], 'market': [['SELL', 'WOOL', 4], ['SELL', 'FERTILIZER', 1], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_PRODUCT', 'FERTILIZER', 1], ['BUY_LAND'], ['BUY_ANIMAL', 'COW', 2]]}`
- callback=176（recorded step=177，动作作用于 observation[callback] 状态）day=7 h=8
  - v3 `{'farmer': ['PLACE', 'FERTILIZER'], 'hands': [['PLACE', 'FERTILIZER'], ['SOUTH'], ['EAST'], ['EAST'], ['PLACE', 'FERTILIZER'], ['EAST'], ['WEST'], ['WEST']], 'market': [['SELL', 'FERTILIZER', 3], ['BUY_ANIMAL', 'SHEEP', 1]]}`
  - opp `{'farmer': ['PLACE', 'FERTILIZER'], 'hands': [['PLACE', 'FERTILIZER'], ['SOUTH'], ['EAST'], ['EAST'], ['PLACE', 'FERTILIZER'], ['EAST'], ['WEST'], ['WEST']], 'market': [['SELL', 'WOOL', 2], ['SELL', 'FERTILIZER', 3], ['BUY_ANIMAL', 'SHEEP', 1]]}`
- callback=177（recorded step=178，动作作用于 observation[callback] 状态）day=7 h=9
  - v3 `{'farmer': ['NORTH'], 'hands': [['NORTH'], ['SOUTH'], ['PLACE', 'SHEEP'], ['PLACE', 'FERTILIZER'], ['NORTH'], ['EAST'], ['WATER'], ['WATER']], 'market': [['SELL', 'FERTILIZER', 1], ['SELL', 'WOOL', 2]]}`
  - opp `{'farmer': ['NORTH'], 'hands': [['NORTH'], ['SOUTH'], ['PLACE', 'SHEEP'], ['PLACE', 'FERTILIZER'], ['NORTH'], ['EAST'], ['WATER'], ['WATER']], 'market': [['SELL', 'FERTILIZER', 1]]}`
- callback=178（recorded step=179，动作作用于 observation[callback] 状态）day=7 h=10
  - v3 `{'farmer': ['WEST'], 'hands': [['NORTH'], ['PLACE', 'FERTILIZER'], ['CARE'], ['NORTH'], ['NORTH'], ['EAST'], ['WEST'], ['NORTH']], 'market': [['BUY_SEED', 'STRAWBERRY', 1]]}`
  - opp `{'farmer': ['WEST'], 'hands': [['NORTH'], ['PLACE', 'FERTILIZER'], ['CARE'], ['NORTH'], ['NORTH'], ['EAST'], ['WEST'], ['NORTH']], 'market': [['SELL', 'WOOL', 2], ['BUY_SEED', 'STRAWBERRY', 1]]}`
- callback=191（recorded step=192，动作作用于 observation[callback] 状态）day=7 h=23
  - v3 `{'farmer': ['PASS'], 'hands': [['PASS'], ['PASS'], ['PASS'], ['PASS'], ['PASS'], ['WATER'], ['PASS'], ['PASS']], 'market': [['BUY_PRODUCT', 'WHEAT', 3]]}`
  - opp `{'farmer': ['PASS'], 'hands': [['PASS'], ['PASS'], ['PASS'], ['PASS'], ['PASS'], ['WATER'], ['PASS'], ['PASS']], 'market': []}`
- callback=241（recorded step=242，动作作用于 observation[callback] 状态）day=10 h=1
  - v3 `{'farmer': ['WEST'], 'hands': [['WEST'], ['WEST'], ['WEST'], ['WEST'], ['WEST'], ['WEST'], ['NORTH'], ['NORTH'], ['WEST'], ['WEST']], 'market': [['HIRE'], ['BUY_ANIMAL', 'SHEEP', 2], ['BUY_PRODUCT', 'FERTILIZER', 8]]}`
  - opp `{'farmer': ['WEST'], 'hands': [['WEST'], ['WEST'], ['WEST'], ['WEST'], ['WEST'], ['WEST'], ['NORTH'], ['NORTH'], ['WEST'], ['WEST']], 'market': [['BUY_PRODUCT', 'FERTILIZER', 8], ['HIRE'], ['BUY_ANIMAL', 'SHEEP', 2]]}`
- callback=256（recorded step=257，动作作用于 observation[callback] 状态）day=10 h=16
  - v3 `{'farmer': ['PLACE', 'MILK', 12], 'hands': [['NORTH'], ['PLANT', 'WHEAT'], ['NORTH'], ['NORTH'], ['WEST'], ['NORTH'], ['PLANT', 'WHEAT'], ['CARE'], ['FEED'], ['NORTH'], ['EAST']], 'market': [['SELL', 'MILK', 9], ['BUY_PRODUCT', 'WHEAT', 2]]}`
  - opp `{'farmer': ['PLACE', 'MILK', 12], 'hands': [['NORTH'], ['PLANT', 'WHEAT'], ['NORTH'], ['NORTH'], ['WEST'], ['NORTH'], ['PLANT', 'WHEAT'], ['CARE'], ['FEED'], ['NORTH'], ['EAST']], 'market': [['SELL', 'MILK', 9], ['BUY_PRODUCT', 'WHEAT', 5]]}`

### Episode 110051331：Aura Farming，分差 -690

终局：v3 100434，对手 101124；双方 callback action 相同 85.3%（613/719）。

每日 callback=day*24 的现金差：

|day|v3 cash|opp cash|v3-opp|
|---:|---:|---:|---:|
|0|3000|3000|0|
|1|88|36|52|
|2|147|95|52|
|3|260|208|52|
|4|341|289|52|
|5|751|699|52|
|6|864|812|52|
|7|1388|1338|50|
|8|808|758|50|
|9|1401|1450|-49|
|10|2180|2361|-181|
|11|15022|13684|1338|
|12|13548|12210|1338|
|13|16159|14821|1338|
|14|17919|16581|1338|
|15|19025|17687|1338|
|16|21482|20144|1338|
|17|24572|23253|1319|
|18|26789|25472|1317|
|19|29015|28042|973|
|20|30009|28889|1120|
|21|30476|29359|1117|
|22|31494|30369|1125|
|23|32396|31624|772|
|24|33075|32671|404|
|25|33935|33609|326|
|26|35299|35085|214|
|27|36264|35856|408|
|28|49541|48263|1278|
|29|61126|60185|941|

关键时刻库存和位置：

|t|v3 cash|opp cash|v3 shed/held|opp shed/held|v3 pos|opp pos|
|---:|---:|---:|---|---|---|---|
|0|3000|3000|0/0|0/0|[4, 4]|[4, 4]|
|24|88|36|3/0|3/0|[4, 4]|[4, 4]|
|48|147|95|8/0|8/0|[4, 4]|[4, 4]|
|96|341|289|12/0|12/0|[4, 4]|[4, 4]|
|192|808|758|9/0|9/0|[4, 4]|[4, 4]|
|288|13548|12210|67/0|67/0|[4, 4]|[4, 4]|
|432|26789|25472|94/0|94/0|[4, 4]|[4, 4]|
|576|33075|32671|100/0|95/0|[4, 4]|[4, 4]|
|648|36264|35856|95/0|96/0|[4, 4]|[4, 4]|
|696|61126|60185|98/0|100/0|[4, 4]|[4, 4]|
|719|100434|101124|0/0|0/0|[5, 4]|[5, 4]|

前 12 个双方动作分歧（动作只表示回放事实，不代表替换后会有同一状态）：

- callback=0（recorded step=1，动作作用于 observation[callback] 状态）day=0 h=0
  - v3 `{'farmer': ['PASS'], 'hands': [], 'market': [['BUY_PRODUCT', 'WHEAT', 25], ['SELL', 'WHEAT', 25]]}`
  - opp `{'farmer': ['PASS'], 'hands': [], 'market': [['BUY_PRODUCT', 'WHEAT', 55], ['SELL', 'WHEAT', 55]]}`
- callback=17（recorded step=18，动作作用于 observation[callback] 状态）day=0 h=17
  - v3 `{'farmer': ['PASS'], 'hands': [['WEST'], ['PASS'], ['WATER'], ['PLANT', 'WHEAT'], ['WEST']], 'market': [['BUY_SEED', 'MELON', 2]]}`
  - opp `{'farmer': ['PASS'], 'hands': [['WEST'], ['PASS'], ['WATER'], ['PLANT', 'WHEAT'], ['WEST']], 'market': [['BUY_SEED', 'MELON', 1]]}`
- callback=18（recorded step=19，动作作用于 observation[callback] 状态）day=0 h=18
  - v3 `{'farmer': ['PASS'], 'hands': [['PLANT', 'MELON'], ['PASS'], ['PASS'], ['WATER'], ['PLANT', 'MELON']], 'market': []}`
  - opp `{'farmer': ['PASS'], 'hands': [['PLANT', 'MELON'], ['PASS'], ['PASS'], ['WATER'], ['PASS']], 'market': []}`
- callback=96（recorded step=97，动作作用于 observation[callback] 状态）day=4 h=0
  - v3 `{'farmer': ['PICKUP', 'WHEAT', 5], 'hands': [], 'market': [['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['SELL', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['PICKUP', 'WHEAT', 5], 'hands': [], 'market': [['SELL', 'FERTILIZER', 1], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']]}`
- callback=120（recorded step=121，动作作用于 observation[callback] 状态）day=5 h=0
  - v3 `{'farmer': ['WEST'], 'hands': [], 'market': [['HIRE'], ['HIRE'], ['HIRE'], ['SELL', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['WEST'], 'hands': [], 'market': [['SELL', 'FERTILIZER', 1], ['HIRE'], ['HIRE'], ['HIRE']]}`
- callback=150（recorded step=151，动作作用于 observation[callback] 状态）day=6 h=6
  - v3 `{'farmer': ['EAST'], 'hands': [['PLACE', 'WOOL', 6], ['NORTH'], ['CARE'], ['WATER'], ['COLLECT_FERTILIZER'], ['CARE'], ['SOUTH']], 'market': [['SELL', 'WOOL', 4], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2], ['BUY_PRODUCT', 'FERTILIZER', 1]]}`
  - opp `{'farmer': ['EAST'], 'hands': [['PLACE', 'WOOL', 6], ['NORTH'], ['CARE'], ['WATER'], ['COLLECT_FERTILIZER'], ['CARE'], ['SOUTH']], 'market': [['SELL', 'WOOL', 6], ['BUY_PRODUCT', 'WHEAT', 2], ['BUY_LAND'], ['BUY_ANIMAL', 'GOOSE', 2], ['BUY_PRODUCT', 'FERTILIZER', 1]]}`
- callback=153（recorded step=154，动作作用于 observation[callback] 状态）day=6 h=9
  - v3 `{'farmer': ['NORTH'], 'hands': [['BUILD_COOP'], ['SOUTH'], ['EAST'], ['PASS'], ['DROP'], ['BUILD_PASTURE'], ['PLACE', 'FERTILIZER', 2]], 'market': [['SELL', 'FERTILIZER', 3]]}`
  - opp `{'farmer': ['NORTH'], 'hands': [['BUILD_COOP'], ['SOUTH'], ['EAST'], ['PASS'], ['DROP'], ['BUILD_PASTURE'], ['PLACE', 'FERTILIZER', 2]], 'market': []}`
- callback=154（recorded step=155，动作作用于 observation[callback] 状态）day=6 h=10
  - v3 `{'farmer': ['PASS'], 'hands': [['PASS'], ['DROP'], ['PLACE', 'FERTILIZER'], ['PASS'], ['WEST'], ['EAST'], ['NORTH']], 'market': [['SELL', 'FERTILIZER', 2], ['BUY_SEED', 'WHEAT', 1]]}`
  - opp `{'farmer': ['PASS'], 'hands': [['PASS'], ['DROP'], ['PLACE', 'FERTILIZER'], ['PASS'], ['WEST'], ['EAST'], ['NORTH']], 'market': [['SELL', 'FERTILIZER', 5], ['BUY_SEED', 'WHEAT', 1]]}`
- callback=205（recorded step=206，动作作用于 observation[callback] 状态）day=8 h=13
  - v3 `{'farmer': ['SOUTH'], 'hands': [['SOUTH'], ['WATER'], ['PLANT', 'STRAWBERRY'], ['WATER'], ['PASS'], ['WATER'], ['WATER'], ['COLLECT_FERTILIZER']], 'market': []}`
  - opp `{'farmer': ['SOUTH'], 'hands': [['SOUTH'], ['WATER'], ['PLANT', 'STRAWBERRY'], ['WATER'], ['PASS'], ['WATER'], ['WATER'], ['COLLECT_FERTILIZER']], 'market': [['SELL', 'WHEAT', 1]]}`
- callback=206（recorded step=207，动作作用于 observation[callback] 状态）day=8 h=14
  - v3 `{'farmer': ['FEED'], 'hands': [['SOUTH'], ['HARVEST'], ['WATER'], ['NORTH'], ['PASS'], ['NORTH'], ['SOUTH'], ['WEST']], 'market': [['BUY_PRODUCT', 'WHEAT', 3]]}`
  - opp `{'farmer': ['FEED'], 'hands': [['SOUTH'], ['HARVEST'], ['WATER'], ['NORTH'], ['PASS'], ['NORTH'], ['SOUTH'], ['WEST']], 'market': [['SELL', 'WHEAT', 1], ['BUY_PRODUCT', 'WHEAT', 3]]}`
- callback=207（recorded step=208，动作作用于 observation[callback] 状态）day=8 h=15
  - v3 `{'farmer': ['CARE'], 'hands': [['DROP'], ['PLANT', 'STRAWBERRY'], ['WEST'], ['WATER'], ['PASS'], ['NORTH'], ['WATER'], ['WEST']], 'market': [['SELL', 'FERTILIZER', 2]]}`
  - opp `{'farmer': ['CARE'], 'hands': [['DROP'], ['PLANT', 'STRAWBERRY'], ['WEST'], ['WATER'], ['PASS'], ['NORTH'], ['WATER'], ['WEST']], 'market': [['SELL', 'FERTILIZER', 2], ['SELL', 'WHEAT', 1]]}`
- callback=208（recorded step=209，动作作用于 observation[callback] 状态）day=8 h=16
  - v3 `{'farmer': ['COLLECT_FERTILIZER'], 'hands': [['NORTH'], ['WATER'], ['WATER'], ['EAST'], ['PASS'], ['WATER'], ['SOUTH'], ['SOUTH']], 'market': [['BUY_SEED', 'STRAWBERRY', 1]]}`
  - opp `{'farmer': ['COLLECT_FERTILIZER'], 'hands': [['NORTH'], ['WATER'], ['WATER'], ['EAST'], ['PASS'], ['WATER'], ['SOUTH'], ['SOUTH']], 'market': [['SELL', 'WHEAT', 1], ['BUY_SEED', 'STRAWBERRY', 1]]}`

