from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('create-project/', views.create_project, name='create_project'),
    path('jobs/', views.jobs, name='jobs'),
    path('project/<int:pk>/join/', views.request_to_join, name='request_join'),
    path('join-requests/', views.join_requests, name='join_requests'),
    path('my-requests/', views.my_join_requests, name='my_join_requests'),
    path('chat/<int:request_id>/', views.chat_view, name='chat'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('inbox/', views.inbox, name='inbox'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('message/<str:username>/', views.send_direct_message, name='send_message'),
    path('messages/', views.messages_inbox, name='messages_inbox'),
    path('message-thread/<str:username>/', views.message_thread, name='message_thread'),
    path('settings/', views.settings_page, name='settings'),
    path('post/<int:post_id>/request-chat/', views.request_to_chat, name='request_chat'),
    path('project/<int:project_id>/request-chat/', views.request_to_chat_project, name='request_chat_project'),
    path('chat-requests/', views.chat_requests_inbox, name='chat_requests_inbox'),
    path('chat-request/<int:chat_request_id>/approve/', views.approve_chat_request, name='approve_chat_request'),
    path('chat-request/<int:chat_request_id>/reject/', views.reject_chat_request, name='reject_chat_request'),
    path('chat/', views.unified_chat, name='unified_chat'),
]
