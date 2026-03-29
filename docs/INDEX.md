# 项目文档索引

**最后更新：** 2026-03-29  
**适用分支：** 当前工作区代码

本目录采用“索引制文档树”，按代码地图、接口、开发、架构四层组织。

## 文档树

```text
docs/
├── INDEX.md
├── API/
│   └── README.md
├── DEVELOPMENT/
│   └── README.md
├── architecture/
│   ├── INDEX.md
│   ├── 01-system-overview.md
│   ├── 02-backend-flow.md
│   └── 03-database.md
└── CODEMAPS/
    ├── INDEX.md
    ├── frontend.md
    ├── backend.md
    ├── database.md
    ├── agent.md
    ├── api.md
    ├── integrations.md
    └── workers.md
```

## 快速导航

- 代码地图总览：`docs/CODEMAPS/INDEX.md`
- 接口文档：`docs/API/README.md`
- 开发文档：`docs/DEVELOPMENT/README.md`
- 架构文档：`docs/architecture/INDEX.md`

## 推荐阅读顺序

1. `docs/CODEMAPS/INDEX.md`（先看全局）
2. `docs/architecture/01-system-overview.md`（再看分层）
3. `docs/API/README.md`（对接接口）
4. `docs/DEVELOPMENT/README.md`（本地开发与扩展）
