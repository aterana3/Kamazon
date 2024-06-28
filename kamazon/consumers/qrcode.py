from django.contrib.sessions.backends.db import SessionStore
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.auth import get_user_model

User = get_user_model()

class QRConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.room_group_name = None

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'{self.token}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected to group: {self.token}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.token, self.channel_name)
        print(f"WebSocket disconnected from group: {self.token}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            action = data.get('action')
            if action == 'authorize':
                await self.authorize(data)
            elif action == 'authenticated':
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'authenticated',
                    'data': data
                })

    async def authorize(self, data):
        user = await self.get_user(data['user_id'])
        if user:
            session_key = await self.create_session(user)
            await self.send(text_data=json.dumps({
                'action': 'successful',
                'session_key': session_key
            }))
        else:
            await self.send(text_data=json.dumps({
                'action': 'error',
                'error': 'User not found'
            }))

    @database_sync_to_async
    def get_user(self, user_id):
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
