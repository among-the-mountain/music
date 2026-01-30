# Selenium 实现用户登录的爬虫项目

## 项目说明

这是一个使用 Selenium 自动化登录并爬取数据的示例项目。

## 文件结构

```
project/
├── server.py                # Flask 服务器
├── spider_login.py          # Selenium 爬虫脚本
└── templates/               # HTML 模板
    ├── login.html          # 登录页面
    └── show.html           # 商品展示页面
```

## 功能说明

### 1. Flask 服务器 (server.py)

- **登录页面** (`/`): 提供用户登录表单
- **登录验证** (`/login`): 验证用户名和密码
  - 正确凭证: `admin` / `123456`
  - 登录成功后显示商品列表
  - 登录失败返回错误信息

### 2. Selenium 爬虫 (spider_login.py)

自动化流程：
1. 访问登录页面
2. 填写用户名和密码
3. 点击登录按钮
4. 提取商品表格数据并打印

## 使用方法

### 1. 启动 Flask 服务器

```bash
cd project
python server.py
```

服务器将在 `http://127.0.0.1:5000/` 运行

### 2. 运行 Selenium 爬虫

在另一个终端窗口中：

```bash
cd project
python spider_login.py
```

### 预期输出

```
商品名 价格
苹果 5
香蕉 3
橘子 4
```

## 依赖安装

```bash
pip install flask selenium
```

## 注意事项

1. **ChromeDriver**: 爬虫脚本需要 ChromeDriver。如果您的系统中没有安装，请从 [ChromeDriver 官网](https://chromedriver.chromium.org/) 下载对应版本。

2. **无头模式**: 当前版本配置了 Chrome 的无头模式（headless），适合在服务器环境中运行。如果需要看到浏览器界面，可以注释掉以下行：
   ```python
   chrome_options.add_argument('--headless')
   ```

3. **端口冲突**: 如果 5000 端口被占用，可以修改 `server.py` 中的端口号。

4. **仅限学习使用**: 本项目仅用于教学演示目的。Flask 服务器以调试模式运行（`debug=True`），不适合生产环境部署。在生产环境中应使用 WSGI 服务器（如 Gunicorn）并禁用调试模式。

## 测试账号

- 用户名: `admin`
- 密码: `123456`
