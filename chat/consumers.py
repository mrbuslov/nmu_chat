from datetime import datetime
import json
from time import time
# from aiohttp import request
from channels.generic.websocket import AsyncWebsocketConsumer
from django.dispatch import receiver
from pytest import console_main

from account.models import Account
from .models import Message, Room 
from django.db.models import Q, F
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        self.user = self.scope["user"]
        await user_online(self, self.user)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await user_offline(self, self.user)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        email = text_data_json['email']
        room_name = text_data_json['roomName']

        room = await database_sync_to_async(Room.objects.get, thread_sensitive=True)(name=room_name)
        if room.participant_1.email == email:
            receiver = room.participant_2
        else:
            receiver = room.participant_1
        
            
        msg_date = await database_sync_to_async(Message.objects.create, thread_sensitive=True)(value=message, room=room, sender=email, receiver=receiver)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'sender': email,
                'receiver': receiver.email,
                'date': str(msg_date.date),
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        date = event['date']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'date': date,
        }))



# online/offline
@database_sync_to_async
def user_online(self, user):
    Account.objects.filter(email=user).update(online=True)

@database_sync_to_async
def user_offline(self, user):
    Account.objects.filter(email=user).update(online=False)
    Account.objects.filter(email=user).update(last_online=datetime.now())