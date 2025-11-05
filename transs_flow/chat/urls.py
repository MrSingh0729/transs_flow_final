from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_index, name="index"),
    path("room/<int:room_id>/", views.chat_room, name="room"),
    path("private/<int:user_id>/", views.create_private_chat, name="private"),
    path("group/create/", views.create_group_chat, name="create_group"),
    
]
