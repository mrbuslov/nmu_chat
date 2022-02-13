from django.contrib import admin
from .models import Room, Message, File


class RoomAdmin(admin.ModelAdmin): # класс-редактор представления модели
    list_display=('name', 'participant_1', 'participant_2')# последовательность имен полей, которые должны выводиться в списке записей
    fields = ('name', 'participant_1', 'participant_2')
    search_fields = ('name',)

class MessageAdmin(admin.ModelAdmin): # класс-редактор представления модели
    list_display=('value', 'room')# последовательность имен полей, которые должны выводиться в списке записей
    fields = ('value', 'room', 'date', 'sender', 'receiver')
    search_fields = ('room',)

admin.site.register(Room, RoomAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(File)
