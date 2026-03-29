# Workers Codemap

**最后更新：** 2026-03-29

项目当前没有独立的消息队列 Worker 进程，离线任务主要由脚本触发。

## 离线任务入口

- `prepare_data/data_spider.py`：数据采集
- `prepare_data/build_data.py`：数据清洗与构建
- `neo4j_import.py`：图谱导入
- `demo_*.py`：演示或批量流程脚本

## 调度方式

- 以 `.bat` 和手动命令为主，无内置调度器。
- 典型启动脚本：`start-all.bat`, `run*.bat`, `运行*.bat`。

## 建议

如需稳定后台任务，可后续引入：

- Celery + Redis（任务队列）
- APScheduler（轻量定时）
- 或独立 worker 服务目录（`workers/`）
