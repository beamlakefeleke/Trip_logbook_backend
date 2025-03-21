import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TripTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        self.trip_group_name = f"trip_{self.trip_id}"

        # Join trip group
        await self.channel_layer.group_add(self.trip_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave trip group
        await self.channel_layer.group_discard(self.trip_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        # Broadcast message to trip group
        await self.channel_layer.group_send(
            self.trip_group_name, {"type": "trip_update", "message": message}
        )

    async def trip_update(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
