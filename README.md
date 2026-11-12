# SQLite · Aide 数据库插件

Aide `sqlite` 插件的独立分发仓库，版本 **1.0.3**，MIT 许可。源码来自 [Aide f795a240](https://github.com/skyelan1999/aide/tree/f795a240cdb37e9b92a37d91664bd1bb3053b809/plugins/sqlite)。1.0.1 修复多语句危险写确认、实际 ATTACH 授权和 CSV 路径边界；历史 1.0.0 ZIP 不覆盖。

## 工具与读写行为

| 工具 | 用途 | 默认行为 |
| --- | --- | --- |
| `sqlite_query` | 单条参数化查询或写入 | 默认只读；写入需 `readonly=false` |
| `sqlite_transaction` | 顺序执行语句并提交，失败回滚 | 默认可写 |
| `sqlite_execute` | 在事务中执行多语句脚本 | 默认可写 |
| `sqlite_tables` | 表与视图清单 | 只读 |
| `sqlite_schema` | 建表 SQL、列、索引和外键 | 只读 |
| `sqlite_export` | CSV 导出或 `VACUUM INTO` 数据库副本 | 写出文件；dump 以可写方式打开数据库 |

这些工具实际读写数据库或输出文件，不只是生成文件提案。执行前应审阅 SQL、数据库及导出路径，并备份重要数据库。现有危险语句检查要求部分 `DROP` 和无 `WHERE` 的 `UPDATE/DELETE` 使用 `confirm=true`，不能替代 SQL 审核。

使用位置参数 `?` 配合数组，或命名参数配合对象，避免把输入值拼进 SQL。普通查询最多返回 500 行，文本单元格超过 10,000 字符截断；这限制的是返回结果，不能视为 SQL 内存预算。`busy_timeout` 限制锁等待，不是同步 SQL 的硬执行时限。

## 环境与路径

需要支持插件导入的 Aide（本版市场最低版本 `0.1.19.0 RC1`）及提供 `node:sqlite` / `DatabaseSync` 的 Node.js，验证环境为 Node 24。零 npm 依赖，不自动安装运行时。

本地相对路径以宿主本次绑定的工作区为基准；传统绝对路径继续限制在允许挂载根内。SSH 工作区和已启用、AI 可见引用使用下述受控快照，不回退到本地目录。`/context` 通常为只读挂载。平台标签对应 Aide 宿主环境，不代表原生 Windows 路径已验证。

Node 插件属于可信宿主代码，不是权限沙箱。SQLite 扩展加载关闭；既有路径及 SQL 检查不构成对恶意 SQL 的安全隔离保证。

## 安装

从 [Release](https://github.com/skyelan1999/aide-pkg-sqlite/releases/tag/v1.0.3) 说明的固定提交链接下载 `aide-pkg-sqlite-v1.0.3.zip` 和 `SHA256SUMS`，运行 `sha256sum -c SHA256SUMS` 后通过 Aide 插件管理导入；也可在[官方市场](https://skyelan1999.github.io/aide-pkg-shop/)搜索 `sqlite`。已有同 ID、同版本无需重复安装。

文件由本仓库 `packages/v1.0.3/` 托管，Release 提供固定提交链接，不额外上传附件。市场分发相同字节的 ZIP。摘要用于完整性校验，不是发布者签名。

## 验证

`node test.js` 运行既有 CRUD、事务提交/回滚、表结构、只读拒绝、危险语句、路径与扩展拒绝、参数绑定、截断、锁等待及导出回归。测试使用并删除 `/workspace/.sqltest`，运行前必须确认该目录不存在；不要在此路径存放用户数据。测试仅使用新建的样本数据库。

发布还使用 Aide 宿主加载实际 ZIP 并调用工具，验证打包后仍可查询与执行事务；没有调用付费模型或访问用户数据库。

## 1.0.1 的安全边界（Aide #583/#584/#586）

1.0.1 安装包包含本节修复；公开发行状态应以 Release 页面为准。运行时需要 Linux 挂载根及 `/proc/self/fd`，并提供 `DatabaseSync.setAuthorizer` 的 Node.js（本次验证24.19.0）；缺少授权API时明确拒绝打开数据库。

危险写检查逐条处理SQL，忽略字符串、标识符、参数名和注释；子查询中的WHERE不能授权无条件外层写，NUL输入拒绝。此确认检查仍不代替SQL审核或数据备份。每次实际ATTACH还由SQLite原生授权器校验；使用允许根内的绝对字面路径或`:memory:`，未知动态目标与`file:` URI拒绝；相对路径仅在SQLite实际工作目录仍属于允许根时接受。

CSV导出验证实际父目录，持有目录句柄，在同目录生成0600临时文件后原子替换目标目录项，拒绝现有符号链接，并防止发布时新出现的链接指向外部文件。数据库本体与dump仍保留原有路径检查；本节不声称实现了所有文件操作的操作系统隔离。

新增回归：`node --test security.test.cjs`。既有`node test.js`须使用隔离容器或确认其固定测试目录没有用户数据。


### SSH 工作区与引用（1.0.3）

默认 `db` 相对选中的工作区；可用 `source` 指定宿主返回的已启用且对当前工作区 AI 可见的来源 ID。远端路径必须为来源内的相对路径。`outputSource` 可单独指定导出目标，目标引用必须为 RW。宿主需要支持 `api.sources` 的 checkout/commit；旧宿主明确报错，不回退到本机 `/workspace`。

远端 SQLite 使用**停写文件快照**：操作前请停止其他写入并完成 WAL checkpoint。宿主拒绝非空 WAL/journal；执行后重新核对文件摘要、连接身份和权限，再写回。它没有跨主机 SQLite 锁，也不提供跨数据库文件与导出文件的原子事务；外部写入必须保持停止直到调用完成。单文件及每次 checkout 总量限 64 MiB。SQL 无法 ATTACH 任意本机文件，CSV/dump 只写入明确授权的导出槽。升级通过市场或手动导入完成，不会由 Aide 主程序升级自动替换已安装插件。

本地相对数据库与导出路径以本次宿主绑定的工作区为基准，支持选中的 `/local/...` 和 `/mounts/...` 工程；本地数据库仍使用原文件和 SQLite 锁。已明确输入的传统本地绝对路径继续沿用原有根边界。
