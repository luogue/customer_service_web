# 客服聊天系统

## 项目结构

```
customer_service_web/
├── frontend/          # 前端项目 (Vue3 + Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatComponent.vue    # 聊天组件
│   │   │   └── LoginComponent.vue   # 登录组件
│   │   ├── views/
│   │   │   └── admin/               # 管理后台页面
│   │   ├── App.vue                  # 主应用
│   │   ├── main.js                  # 入口文件
│   │   └── style.css                # 全局样式
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # 前端依赖
│   └── vite.config.js               # Vite 配置
│
└── backend/           # 后端项目 (Python + FastAPI)
    ├── api_gateway/       # 接入层：请求入口/路由/鉴权
    ├── dialogue_engine/   # 对话引擎层：意图/多轮/对话逻辑
    ├── knowledge_base/    # 知识底座层：检索/上下文/知识库
    ├── llm_adapter/       # 大模型交互层：模型调用/提示词
    ├── ops_monitor/       # 运维层：日志/异常处理
    ├── config/            # 全局配置：密钥/模型参数
    ├── main.py            # FastAPI 主应用
    └── requirements.txt   # Python 依赖
```

## 快速开始

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 功能特性

- 实时聊天（WebSocket）
- 用户登录/注册（JWT 鉴权）
- 管理后台（模型配置、Prompt模板、FAQ管理等）
- Mock 数据回复
- 订单/退款/物流/投诉管理接口
