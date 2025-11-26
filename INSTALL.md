# 项目依赖安装指南

## 快速安装

### 方法 1: 安装所有依赖（推荐）

```bash
pip install -r requirements.txt
```

### 方法 2: 分步安装（如果遇到问题）

#### 1. 核心依赖（爬虫和数据处理）
```bash
pip install pymysql lxml python-dotenv tqdm
```

#### 2. 数据库驱动
```bash
pip install neo4j-driver sqlalchemy
```

#### 3. 其他依赖（如果后续需要）
```bash
pip install langchain faiss-cpu fastapi pydantic requests
```

## 使用虚拟环境（推荐）

### 创建虚拟环境

```bash
# Windows
python -m venv .venv

# Linux/Mac
python3 -m venv .venv
```

### 激活虚拟环境

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 在虚拟环境中安装依赖

```bash
pip install -r requirements.txt
```

## 检查依赖安装状态

运行依赖检查脚本：

```bash
python check_dependencies.py
```

## 依赖说明

### 核心依赖（必须）

| 包名 | 用途 | 是否必需 |
|------|------|----------|
| `pymysql` | MySQL 数据库连接 | ✅ 必需 |
| `lxml` | HTML/XML 解析（爬虫） | ✅ 必需 |
| `python-dotenv` | 环境变量管理 | ✅ 必需 |
| `neo4j-driver` | Neo4j 图数据库连接 | ✅ 必需（导入 Neo4j） |
| `tqdm` | 进度条显示 | ✅ 必需 |

### 可选依赖（按需安装）

| 包名 | 用途 | 何时需要 |
|------|------|----------|
| `langchain` | RAG 框架 | GraphRAG 集成时 |
| `faiss-cpu` | 向量数据库 | 向量检索时 |
| `fastapi` | Web API 框架 | API 服务时 |
| `sqlalchemy` | ORM 框架 | ORM 操作时 |
| `requests` | HTTP 请求库 | HTTP 请求时 |

## 常见问题

### 1. lxml 安装失败

**Windows 用户**：可能需要先安装 Microsoft Visual C++ Build Tools

**解决方案**：
```bash
# 使用预编译的 wheel 包
pip install --only-binary :all: lxml

# 或者下载对应版本的 wheel 文件手动安装
# 访问: https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
```

### 2. faiss-cpu 安装失败

**如果只需要运行爬虫和导入数据**：可以暂时不安装 faiss-cpu

**如果遇到错误**：
```bash
# 尝试使用 conda 安装
conda install -c conda-forge faiss-cpu

# 或者使用指定版本
pip install faiss-cpu==1.7.4
```

### 3. MySQL 连接失败

确保 MySQL 服务正在运行，并检查 `.env` 文件中的数据库配置。

### 4. Neo4j 连接失败

确保 Neo4j 服务正在运行，并检查 `.env` 文件中的 Neo4j 配置。

## 最小化安装（仅爬虫和导入）

如果只需要运行爬虫和数据导入，可以只安装以下依赖：

```bash
pip install pymysql lxml python-dotenv tqdm neo4j-driver
```

## 验证安装

安装完成后，运行测试脚本验证：

```bash
# 检查依赖
python check_dependencies.py

# 测试爬虫（如果依赖已安装）
cd prepare_data
python test_spider.py
```

