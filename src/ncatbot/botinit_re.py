from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log
from ollama import chat
import time
import threading
import asyncio

_log = get_log()
config.set_bot_uin("2102014845") 
config.set_ws_uri("ws://localhost:3001") 
config.set_token("")

class GroupActivityMonitor(BotClient):
    def __init__(self):
        super().__init__()
        self.group_activity = {}  # {group_id: last_active_timestamp}
        self.lock = threading.Lock()
        self.modelstr = 'deepseek-sex-r1-14bQ6'
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        
    def _monitor_loop(self):
        """后台监控线程主循环"""
        while True:
            time.sleep(300)  # 每5分钟检查一次
            self.check_inactive_groups()
            
    def check_inactive_groups(self):
        """检查不活跃群组"""
        now = time.time()
        inactive_groups = []
        
        with self.lock:
            # 获取超过30分钟未活动的群组
            for group_id, last_active in self.group_activity.items():
                if now - last_active > 1800:  # 30分钟
                    inactive_groups.append(group_id)
            
            # 清理超过1天未活动的群组
            self.group_activity = {k:v for k,v in self.group_activity.items() if now - v < 86400}
        
        # 处理不活跃群组
        for group_id in inactive_groups:
            self.handle_inactive_group(group_id)
            
    def handle_inactive_group(self, group_id):
        """处理不活跃群组"""
        context = {
            "group_id": group_id,
            "last_active": self.group_activity.get(group_id, 0),
            "current_time": time.time()
        }
        
        try:
            # 构建模型请求
            messages = [{
                "role": "system",
                "content": f"当前群组 {group_id} 已{int((time.time()-context['last_active'])/60)}分钟无发言。请生成1条轻松有趣的消息来活跃气氛，要求：\n"
                           "- 使用口语化中文\n"
                           "- 包含疑问句或互动内容\n"
                           "- 避免敏感话题\n"
                           "- 直接输出消息内容，不要包含思考过程"
            }]
            
            response = chat(
                model=self.modelstr,
                messages=messages,
                stream=False
            )
            
            # 过滤回复内容
            full_response = response['message']['content']
            cleaned_response = self._clean_response(full_response)
            
            # 发送群消息
            asyncio.run_coroutine_threadsafe(
                self.api.post_group_msg(group_id, text=cleaned_response),
                asyncio.get_event_loop()
            )
            
            _log.info(f"已向不活跃群组 {group_id} 发送活跃消息")
            
        except Exception as e:
            _log.error(f"处理不活跃群组失败: {str(e)}")
            
    def _clean_response(self, response):
        """清理模型回复中的思考内容"""
        # 移除<think>标签内容
        while '<think>' in response and '</think>' in response:
            start = response.find('<think>')
            end = response.find('</think>') + len('</think>')
            response = response[:start] + response[end:]
        return response.strip()
    
    @GroupMessage.handler
    async def on_group_message(self, msg: GroupMessage):
        """更新群组活跃时间"""
        with self.lock:
            self.group_activity[msg.group_id] = time.time()
        
        # 保持原有消息处理逻辑
        await super().on_group_message(msg)
        
    def run(self):
        """启动监控"""
        self.monitor_thread.start()
        super().run()

if __name__ == "__main__":
    monitor = GroupActivityMonitor()
    monitor.run()