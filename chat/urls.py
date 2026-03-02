from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('chat/<int:recipient_id>/', views.chat_room, name='chat_room'),
    path('api/save_public_key/', views.save_public_key, name='save_public_key'),
    path('api/get_public_key/<int:user_id>/', views.get_public_key, name='get_public_key'),
    path('api/send_message/', views.send_message, name='send_message'),
    path('api/get_messages/<int:other_user_id>/', views.get_messages, name='get_messages'),
    path('api/edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('api/delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('api/delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
]
