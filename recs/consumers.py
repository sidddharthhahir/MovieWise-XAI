from channels.generic.websocket import AsyncJsonWebsocketConsumer
class RatingsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self): await self.accept()
