# 提交准备状态

状态：已达到“可以在用户明确指令后消耗两次机会”的内部门槛；当前没有执行提交。

推荐顺序：

1. `h5sim96.tar.gz`：线上最高分基线，优先提交。
2. `cap2.tar.gz`：h5sim96 的低风险多样性版本，第二次提交。

两包均只有根目录 `main.py`，已 `py_compile`，720-step 本地面板全部 DONE。上传前仍需由用户明确下发提交任务；上传后逐次核对 submission id、状态和 active submission queue。
