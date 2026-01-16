from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.show_id = self.scope['url_route']['kwargs']['show_id']
        self.room_group_name = f"show_{self.show_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def seat_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))
