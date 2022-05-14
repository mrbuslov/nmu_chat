from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from . import apps_functions

app_name='chat'
urlpatterns = [
    path('', views.index, name='index'),
    path('show_chats/', views.show_chats, name = 'show_chats'),
    path('get_last_msg/', views.get_last_msg, name = 'get_last_msg'),
    path('room/', views.room, name='room'),
    path('get_room/', views.get_room, name='get_room'),
    path('upload/', views.upload_my_img, name='upload_my_img'),
    path('upload_file_to_chat/', views.upload_file_to_chat, name='upload_file_to_chat'),
    path('update_data/', views.update_data, name='update_data'),
    path('get_settings_data/', views.get_settings_data, name='get_settings_data'),
    path('chat_delete/', views.chat_delete, name='chat_delete'),
    path('msg_action/', views.msg_action, name='msg_action'),

    # приём и отправка данных приложений
    path('app/', apps_functions.app_index, name='app_index'),
    path('return_room_name/', apps_functions.return_room_name, name='return_room_name'),
    path('get_messages/', apps_functions.get_messages, name='get_messages'),
    path('app_upload_file/', apps_functions.app_upload_file, name='app_upload_file'),
    path('get_settings/', apps_functions.get_settings, name='get_settings'),
    path('update_settings/', apps_functions.update_settings, name='update_settings'),
    path('app_login/', apps_functions.app_login, name='app_login'),
    path('app_register/', apps_functions.app_register, name='app_register'),
    path('app_get_users/', apps_functions.app_get_users, name='app_get_users'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)