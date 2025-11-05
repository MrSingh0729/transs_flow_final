import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        is_member = await database_sync_to_async(self._check_member)(user)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        if not message:
            return

        msg_obj = await database_sync_to_async(self._save_message)(user, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg_obj.content,
                "sender_name": getattr(user, "full_name", str(user)),
                "created_at": msg_obj.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    def _check_member(self, user):
        try:
            room = ChatRoom.objects.get(pk=self.room_id)
            return room.participants.filter(pk=user.pk).exists()
        except ChatRoom.DoesNotExist:
            return False

    def _save_message(self, user, content):
        room = ChatRoom.objects.get(pk=self.room_id)
        return Message.objects.create(room=room, sender=user, content=content, created_at=timezone.now())
