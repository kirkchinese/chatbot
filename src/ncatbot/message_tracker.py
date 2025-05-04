import asyncio
import time
import random
from collections import defaultdict
from typing import Dict, Deque
from ncatbot.utils.logger import get_log

_log = get_log()

class MessageTracker:
    def __init__(self):
        # 群组最后活动时间跟踪 {group_id: last_active_time}
        self.group_activity: Dict[int, float] = defaultdict(float)
        # 消息队列 {group_id: Deque}
        self.message_queues = defaultdict(lambda: asyncio.Queue(maxsize=20))
        # 异步锁
        self.lock = asyncio.Lock()
        # 暖场消息模板
        self.warmup_templates = [
            "大家最近有什么有趣的事情分享吗？",
            "听说今天有热点新闻，大家怎么看？",
            "我们来玩个接龙游戏怎么样？",
            "最近发现一个不错的电影/游戏，想推荐给大家~",
            "天气变化要注意身体哦，大家今天都做了什么？"
        ]
    
    async def update_activity(self, group_id: int):
        """更新群组活动时间"""
        async with self.lock:
            self.group_activity[group_id] = time.time()
    
    async def get_inactive_groups(self, timeout: int = 300) -> list:
        """获取超时未活动的群组列表"""
        async with self.lock:
            current_time = time.time()
            return [
                gid for gid, last_time in self.group_activity.items()
                if current_time - last_time > timeout
            ]
    
    async def add_message(self, group_id: int, message: str):
        """添加消息到队列"""
        try:
            # 自动清理旧消息保持队列长度
            if self.message_queues[group_id].qsize() >= 15:
                await self.message_queues[group_id].get()
            await self.message_queues[group_id].put((
                time.time(),
                message
            ))
        except asyncio.QueueFull:
            _log.warning(f"Message queue full for group {group_id}")
    
    async def get_last_message(self, group_id: int) -> str:
        """获取队列中最后一条有效消息"""
        try:
            # 获取最近3条消息中的最后一条
            messages = []
            for _ in range(3):
                if not self.message_queues[group_id].empty():
                    messages.append(await self.message_queues[group_id].get())
            
            if messages:
                # 按时间排序并返回最新
                sorted_msgs = sorted(messages, key=lambda x: x[0], reverse=True)
                # 把未处理的消息放回队列
                for msg in sorted_msgs[1:]:
                    await self.message_queues[group_id].put(msg)
                return sorted_msgs[0][1]
        except asyncio.QueueEmpty:
            pass
        return ""
    
    async def generate_warmup_message(self) -> str:
        """生成暖场消息"""
        return random.choice(self.warmup_templates)