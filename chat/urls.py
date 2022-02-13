from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)