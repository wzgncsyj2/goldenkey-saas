# 金钥匙智知 (GoldenKey AI)

> 企业AI知识库，一问就知

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

## 产品简介

**金钥匙智知** 是北京金钥匙凯丽科技发展有限公司推出的企业级AI知识库+在线客服SaaS产品。

### 核心功能

- **智能知识库**: 上传文档自动解析、向量化，支持语义检索
- **AI客服**: 基于RAG的智能问答，支持多轮对话
- **人工协作**: AI无法解决时无缝转接人工客服
- **多租户**: 企业隔离，独立管理
- **可嵌入Widget**: 一行代码集成到任意网站

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  管理后台     │  │  客服工作台   │  │  访客Widget  │      │
│  │  (Next.js)   │  │  (Next.js)   │  │   (React)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────┐
│         ▼                  ▼                  ▼             │
│                     API Gateway (Traefik)                    │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────────────┐  │
│  │                       ▼                               │  │
│  │              Backend Services (FastAPI)               │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │  │
│  │  │ Auth       │ │ Knowledge  │ │ Chat       │        │  │
│  │  │ Service    │ │ Service    │ │ Service    │        │  │
│  │  └────────────┘ └────────────┘ └────────────┘        │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────────────┐  │
│  │              Data Layer│                               │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │  │
│  │  │ PostgreSQL │ │ Redis      │ │ ChromaDB   │        │  │
│  │  │ + pgvector │ │ (Cache)    │ │ (Vectors)  │        │  │
│  │  └────────────┘ └────────────┘ └────────────┘        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
goldenkey-saas/
├── backend/                 # FastAPI 后端服务
│   ├── app/
│   │   ├── api/routes/     # API 路由
│   │   ├── core/           # 核心配置、安全、依赖
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── knowledge/  # 知识库相关服务
│   │   │   ├── chat/       # 对话相关服务
│   │   │   ├── tenant/     # 租户管理服务
│   │   │   └── billing/    # 计费相关服务
│   │   ├── repositories/   # 数据访问层
│   │   └── utils/          # 工具函数
│   ├── migrations/         # Alembic 数据库迁移
│   ├── tests/              # 测试
│   ├── data/               # 运行时数据 (SQLite/ChromaDB)
│   ├── uploads/            # 上传文件存储
│   ├── pyproject.toml      # 项目依赖配置
│   └── .env.example        # 环境变量模板
├── frontend/               # Next.js 前端 (管理后台+客服工作台)
├── widget/                 # 可嵌入聊天组件
├── deploy/                 # 部署配置
│   ├── docker/            # Docker 相关
│   ├── k8s/               # Kubernetes 配置
│   └── nginx/             # Nginx 配置
├── docs/                   # 项目文档
├── scripts/                # 工具脚本
└── README.md
```

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 15+ (可选，开发阶段用SQLite)
- Redis 7+ (可选)

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入必要配置

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

## 开发进度

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1.1 | 项目目录结构 | ✅ 进行中 |
| 1.2 | Git初始化 | ⬜ 待开始 |
| ... | ... | ... |

## 公司

**北京金钥匙凯丽科技发展有限公司**

---

*Copyright © 2026 GoldenKey AI. All rights reserved.*
