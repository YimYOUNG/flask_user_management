# Flask 用户管理系统

**技术栈:** Python / Flask / SQLite3 / WTForms / pytest / GitHub Actions / 阿里云 VPS

## 快速开始

### 1. 创建虚拟环境
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动应用
```bash
python run.py
```

访问 http://localhost:5000

## 项目结构
```
flask-user-system/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── config.py            # 配置文件
│   ├── routes/              # 路由 (auth, user, api)
│   ├── templates/           # HTML 模板
│   ├── static/              # 静态资源 (CSS/JS)
│   └── utils/               # 工具 (DB, 表单, 验证器)
├── tests/                   # 测试用例
├── .github/workflows/       # CI/CD 部署配置
├── users.db                 # SQLite 数据库文件 (自动生成)
├── requirements.txt
└── run.py
```

## 功能特性
- 用户注册（含表单验证）
- 用户登录/登出
- 用户管理（管理员权限）
- RESTful API 接口
- CSRF 跨站请求伪造防护
- 密码加密存储（scrypt 算法）
- SQLite3 数据库（原生 SQL 操作）
- 数据库自动初始化
- 100% 测试覆盖率（488 条语句全覆盖）

## 运行测试
```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

## 部署到阿里云 VPS

### GitHub Secrets 配置
在 GitHub 仓库 Settings > Secrets 中添加：
- `SERVER_IP`: 8.136.60.141
- `SSH_USER`: root
- `SSH_PASSWORD`: 你的服务器密码

### 部署流程
1. 推送代码到 `main` 分支
2. GitHub Actions 自动运行测试
3. 测试通过后自动部署到服务器
4. systemd 守护进程自动重启应用

## API 接口
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/users` - 用户列表（管理员）
- `GET/PUT/DELETE /api/users/<id>` - 用户操作

## 管理员账号
首次注册的用户需在数据库中手动设置为管理员，或通过代码初始化创建。
