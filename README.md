# NCatBot - 基于NapCat和Ollama的智能QQ机器人

## 项目简介

NCatBot是一个基于NapCat QQ协议和Ollama架构大语言模型的智能聊天机器人，支持私聊和群聊消息处理，具备以下功能：

- 智能对话回复
- 用户跟踪和优先级处理
- 消息队列管理
- 自动暖场互动
- 多用户混合上下文感知对话
- 主动找事功能()

## 前置要求

在运行本项目前，请确保已安装以下组件：

1. [NapCat](https://napneko.github.io/guide/napcat) - QQ协议实现
2. [Ollama](https://ollama.ai/) - 本地大语言模型运行环境
3. Python 3.8+

## 安装指南

### 1. 安装NapCat

请按照[NapCat官方指南](https://napneko.github.io/guide/napcat)安装并配置NapCat

### 2. 安装Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-sex-r1-14bQ6-Alice
```

### 3. 安装Python依赖

```bash
git clone https://github.com/your-repo/ncatbot.git
cd ncatbot
pip install -r requirements.txt
```

## 配置说明

### NapCat配置

1. 修改`napcat/config/napcat.json`:
```json
{
  "ws_uri": "ws://localhost:3001",
  "token": "your_token_here"
}
```

### 机器人配置

修改`src/ncatbot/bot-init.py`中的配置项：
```python
config.set_bot_uin("2102014845")  # 设置机器人QQ号
config.set_ws_uri("ws://localhost:3001")  # NapCat WebSocket地址
config.set_token("your_token")  # NapCat token
```

### Ollama模型配置

默认使用`deepseek-sex-r1-14bQ6-Alice`模型，如需更换：
```python
# 在bot-init.py中修改
modelstr = 'your-model-name'
```

## 使用说明

### 启动机器人

1. 首先启动NapCat服务
2. 然后运行机器人：
```bash
python src/ncatbot/bot-init.py
```

### 功能命令

- 私聊：直接发送消息即可获得回复
- 群聊：
  - `跟踪用户` - 开启消息优先级处理
  - `停止跟踪` - 关闭消息优先级
  - `API测试` - 测试机器人响应

## 常见问题

### NapCat连接失败
- 检查NapCat服务是否正常运行
- 确认`ws_uri`和`token`配置正确

### 模型响应慢
- 检查Ollama服务状态
- 尝试使用性能更好的模型

### 权限问题
- 确保NapCat已登录正确的QQ账号
- 检查机器人QQ号是否有权限访问目标群组

## 贡献指南

欢迎提交Issue或Pull Request贡献代码！

## 许可证

MIT License
