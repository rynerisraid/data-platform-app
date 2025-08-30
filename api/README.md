# Web Template API

这是一个使用 FastAPI 构建的 Web API 项目。

## 项目结构

```
.
├── app
│   ├── config          # 配置模块
│   ├── models          # 数据模型
│   ├── router          # API 路由
│   ├── services        # 业务逻辑
│   └── utils           # 工具函数
├── main.py             # 应用入口
└── pyproject.toml      # 项目配置和依赖
```

## 开发环境配置

### 使用 uv (推荐)

1. 安装 [uv](https://github.com/astral-sh/uv) 工具:
   ```bash
   # Windows (使用 PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. 创建虚拟环境并安装依赖:
   ```bash
   uv venv
   uv pip install -e .
   ```

### 使用 pip

1. 创建虚拟环境:
   ```bash
   python -m venv venv
   ```

2. 激活虚拟环境:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. 安装依赖:
   ```bash
   pip install -e .
   ```

## 运行项目

```bash
uv run main.py
# 或者
python main.py
```

## IDE 配置

推荐使用 VS Code 并安装以下扩展:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Flake8 (ms-python.flake8)
- Black Formatter (ms-python.black-formatter)

确保选择正确的 Python 解释器:
1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "Python: Select Interpreter"
3. 选择项目虚拟环境中的 Python 解释器