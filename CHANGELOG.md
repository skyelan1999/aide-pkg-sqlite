# Changelog

## 1.0.1

- 每个 UPDATE/DELETE 独立校验确认，其他语句或子查询的 WHERE 不代替外层约束。
- SQLite 原生授权器校验每次 ATTACH，拒绝越界、未知动态目标及 file URI。
- CSV 经已验证目录句柄与原子发布，拒绝符号链接逃逸。
- 需要提供 DatabaseSync.setAuthorizer 的 Node.js，缺 API 明确拒绝；验证目标为 Aide Linux 运行环境。
- 回归关联 Aide #583、#584、#586；未覆盖数据库本体/dump 的所有路径竞争。

## 1.0.0

- 将 Aide 已有 SQLite 插件独立分发，保留 MIT 许可。
- 保留原代码、manifest、测试与安装 ZIP 字节内容。
- 补充各工具实际读写默认值、Node 运行依赖、固定挂载根与结果规模限制说明。
