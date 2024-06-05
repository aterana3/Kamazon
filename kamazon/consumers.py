from django.contrib.sessions.backends.db import SessionStore
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.auth import get_user_model

class QRConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        await self.channel_layer.group_add(self.token, self.channel_name)
        await self.accept()
        print(f"WebSocket connected to group: {self.token}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.token, self.channel_name)
        print(f"WebSocket disconnected from group: {self.token}")

    async def receive(self, event):
        message = event['message']
        if message == "authorize":
            user_id = event['user_id']
            user = await self.get_user(user_id)
            if not user:
                await self.send(text_data=json.dumps({
                    'status': 400,
                    'success': False,
                    'message': 'User not found',
                }))
                return
            session_key = await self.create_session(user)
            await self.send(text_data=json.dumps({
                'status': 200,
                'success': True,
                'message': 'Created session key',
                'session_key': session_key
            }))

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def create_session(self, user):
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
        session.save()
        return session.session_key