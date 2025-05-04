from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log
from ollama import chat
import time
import random
import threading

_log = get_log()
config.set_bot_uin("2102014845")  # 设置 bot qq 号 (必填)
config.set_ws_uri("ws://localhost:3001")  # 设置 napcat websocket server 地址
config.set_token("") # 设置 token (napcat 服务器的 token)


bot = BotClient()

# 用户跟踪状态管理
user_tracking = {}  # {user_id: expiration_timestamp}
tracking_lock = threading.Lock()  # 线程锁
modelstr = 'deepseek-sex-r1-14bQ6-Alice'
history_length = 50
# 用户跟踪状态管理
user_tracking = {}  # {user_id: expiration_timestamp}


def check_tracking(user_id):
    """检查用户是否在跟踪状态中"""
    expiration = user_tracking.get(user_id)
    if expiration and time.time() < expiration:
        return True
    if expiration:  # 清理过期跟踪
        del user_tracking[user_id]
    return False

gropnum = [491884473,422049652,1007377144,"测试num"]

# 初始化状态
need_init = True

def get_msg(input=None, sender="用户", tracking_priority=False, user_id=None, group_id=None,inregard = False):
    global need_init
     # 结构化消息格式（新增上下文信息）
    # context_info = f"[From: {sender} | UserID: {user_id} | timestamp: { time.time()} | GroupID: {group_id or '私聊'}]"
    localtime = time.asctime( time.localtime(time.time()) )
    context_info = f"Systerm：[发送人:{sender}|时间:{localtime}|群聊: {group_id or '私聊'}]"
 
    if inregard == True:
        get_msg.history.append({"role": "user", "content": f"{context_info}\n{str(input)}"})
        return
    # 初始化对话历史
    if not hasattr(get_msg, 'history'):
        get_msg.history = []

    # 用户统一退出命令处理（新增模型控制出口）
    exit_commands = ["exit", "quit", "stop", "baibai", "拜拜"]
    if input and input.lower() in exit_commands:
        with tracking_lock:
            get_msg.history = []
        return {'message': {'content': '对话已结束，已清空历史并停止跟踪'}}

    # 添加当前消息到历史
    get_msg.history.append({"role": "user", "content": f"{context_info}\n{str(input)}"})
    
    # 限制历史长度（保留最近50条消息）
    if len(get_msg.history) > history_length:
        get_msg.history = get_msg.history[-history_length:]


    # 主动跟踪选择
    if not tracking_priority:
        with tracking_lock:
            # 计算当前活跃跟踪数
            active_tracks = sum(1 for exp in user_tracking.values() if time.time() < exp)
            
            # 如果当前跟踪数小于3（可配置），从已出现用户中随机选择跟踪
            if active_tracks < 1 and random.random() < 0.3:  # 30%概率选择新用户
                # 获取所有已出现用户
                seen_users = set(user_tracking.keys())
                if seen_users:  # 如果有已出现用户
                    # 随机选择一个已出现用户
                    selected_user = random.choice(list(seen_users))
                    user_tracking[selected_user] = time.time() + 600  # 跟踪10分钟
                    tracking_priority = True
                    _log.info(f"主动选择跟踪已出现用户 {selected_user} 至 {time.time()+60}")
    
    # 添加系统提示词规范输出格式
    try:
        # 如果处于跟踪模式，添加优先级提示
        if tracking_priority:
            # 创建带优先级标记的新消息
            priority_msg = {"role": "user", "content": f"[优先级消息]\n{get_msg.history[-1]['content']}"}
            # 替换最后一条消息
            get_msg.history[-1] = priority_msg
        
        # 使用完整历史记录生成响应
        response = chat(
            model=modelstr,
            messages=get_msg.history,
            stream=False
        )
        
        
    except Exception as e:
        _log.error(f"Chat error: {str(e)}")
        return {'message': {'content': '处理消息时出错，请稍后再试'}}
    
    # 分离思考内容和正式响应
    full_response = response['message']['content']
    try:
        # 提取并记录think内容到终端
        think_blocks = []
        while '<think>' in full_response and '</think>' in full_response:
            start = full_response.find('<think>') + len('<think>')
            end = full_response.find('</think>')
            think_content = full_response[start:end].strip()
            think_blocks.append(think_content)
            # 格式化输出到终端
            _log.debug("="*40)
            _log.debug(f"THINK PROCESS [{time.strftime('%Y-%m-%d %H:%M:%S')}]")
            _log.debug("-"*40)
            _log.debug(think_content)
            _log.debug("="*40)
            full_response = full_response[:start-len('<think>')] + full_response[end+len('</think>'):]
        
        # 处理停止跟踪指令
        if '<stop_tracking>' in full_response:
            with tracking_lock:
                if user_id in user_tracking:
                    del user_tracking[user_id]
                    _log.info(f"已停止跟踪用户 {user_id}")
            full_response = full_response.replace('<stop_tracking>', '').replace('</stop_tracking>', '')
        
        # 提取<response>标签内容，如果没有则使用整个响应
        if '<response>' in full_response and '</response>' in full_response:
            response_content = full_response.split('<response>')[1].split('</response>')[0].strip()
        else:
            response_content = full_response.strip()
            
        # 去除多余空行
        response_content = '\n'.join([line.strip() for line in response_content.split('\n') if line.strip()])
        
        # 添加助手响应到历史
        get_msg.history.append({"role": "assistant", "content": response_content})
        print("当前对话历史为:\n",get_msg.history)
        print("响应为:\n", response)

        return {'message': {'content': response_content}}
    except Exception as e:
        _log.error(f"解析响应失败: {str(e)}")
        return {'message': {'content': '解析响应时出错，请检查日志'}}

# 私聊消息处理（始终启用）
@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    response = get_msg(msg.raw_message, user_id=msg.user_id ,sender=msg.sender.nickname)
    await bot.api.post_private_msg(msg.user_id, text=response['message']['content'])

@bot.group_event()
async def on_group_message(msg: GroupMessage):
    # 检查群聊开关配置
    if not True:
        return
        
    # 记录消息上下文
    context = {
        'timestamp': time.time(),
        'user_name': msg.sender.nickname,
        'group_id': msg.group_id,
        'message': msg.raw_message
    }
    _log.info(f"收到群消息: {context}")
    
    # 处理消息并发
    with threading.Lock():
        # 检查是否是跟踪用户的消息
        is_tracking = check_tracking(msg.user_id)
    
    # 检查跟踪命令
    if msg.raw_message.startswith("跟踪用户"):
        with tracking_lock:
            user_tracking[msg.user_id] = time.time() + 3600  # 跟踪1小时
        await bot.api.post_group_msg(msg.group_id,
                                   text=f"@{msg.sender.nickname} 已开启消息跟踪模式，接下来将优先处理您的消息")
        return
    
    if msg.raw_message.startswith("停止跟踪"):
        with tracking_lock:
            if msg.user_id in user_tracking:
                del user_tracking[msg.user_id]
            await bot.api.post_group_msg(msg.group_id,
                                       text=f"@{msg.sender.nickname} 已停止消息跟踪")
        return

    # 带全局锁的消息处理
    global_lock = threading.Lock()
    with global_lock:
        # 带状态锁的跟踪检查
        with tracking_lock:
            is_tracked = check_tracking(msg.user_id)
            current_time = time.time()
            
            # 清理过期跟踪（超过2分钟未活动）
            expired_users = [uid for uid, exp in user_tracking.items() if exp < current_time]
            for uid in expired_users:
                del user_tracking[uid]
                
            # 如果没有跟踪用户 或 当前用户需要跟踪
            if not user_tracking or is_tracked:
                # 更新跟踪状态
                user_tracking[msg.user_id] = current_time + 120  # 跟踪2分钟
                tracking_status = True
            else:
                # 随机选择是否中断当前处理（10%概率）
                tracking_status = random.random() < 0.1

        if tracking_status or (msg.group_id in gropnum and any(keyword in msg.raw_message.lower() for keyword in {"爱丽丝", "alice"})):
            response = get_msg(input=msg.raw_message,sender=msg.sender.nickname,group_id=msg.group_id)
            await bot.api.post_group_msg (msg.group_id, text=response['message']['content'])
        elif msg.raw_message == "API测试":
            await bot.api.post_group_msg(msg.group_id, text="Bot 已接收到您的 API 请求")
            response = get_msg("API测试，如果你收到此消息，请回答：已收到API请求")
            await bot.api.post_group_msg (msg.group_id, text=response['message']['content'])
            
        else:
            get_msg(input=msg.raw_message,sender=msg.sender.nickname,group_id=msg.group_id,inregard=True)
            # await bot.api.post_private_msg(msg.user_id, text=response['message']['content'])


if __name__ == "__main__":
    # 初始化异步事件循环
    import asyncio
    from message_tracker import MessageTracker  # 假设已实现消息追踪类
    
    # 创建事件循环并启动后台任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    message_tracker = MessageTracker()
    
    # 启动机器人并保持运行
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        _log.info("Received exit signal, shutting down...")
    finally:
        loop.close()
        _log.info("Event loop closed")
