import asyncio
import json
import redis.asyncio as aioredis
from fastapi import WebSocket
from app.infrastructure.config import settings
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # Maps task_id to the active WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        # Immediately start listening for the specific task's result in Redis
        asyncio.create_task(self.listen_to_redis(task_id))

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]

    async def listen_to_redis(self, task_id: str):
        """
        Subscribes to Redis and waits for the worker to publish 
        the AI summary for this specific task.
        """
        redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        pubsub = redis.pubsub()
        
        # Subscribe to the channel name used in your worker
        channel_name = f"notifications_{task_id}"
        await pubsub.subscribe(channel_name)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    # Get the AI data (summary, word count, etc.)
                    data = json.loads(message["data"])
                    
                    # Push it directly to the user's browser via WebSocket
                    if task_id in self.active_connections:
                        await self.active_connections[task_id].send_json(data)
                    
                    # Once we send the final "COMPLETED" message, we can stop listening
                    if data.get("status") in ["COMPLETED", "FAILED"]:
                        break
        except Exception as e:
            print(f"WebSocket Redis Error: {e}")
        finally:
            await pubsub.unsubscribe(channel_name)
            await redis.close()
            # Optional: disconnect the socket once the job is done
            self.disconnect(task_id)

manager = ConnectionManager()