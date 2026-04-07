from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    #Holy moly
    path('', views.welcome_stage, name='home'),
    path('register/', views.join_the_scene, name='register'),
    path('login/', views.access_gateway, name='login'),
    path('logout/', views.exit_stage, name='logout'),
    path('home/', views.discover_creations, name='post_list'),
    path('post/<int:pk>/', views.creation_spotlight, name='post_detail'),
    path('create/', views.craft_creation, name='create_post'),
    path('projects/', views.collab_quest, name='project_list'),
    path('project/<int:pk>/', views.collaboration_space, name='project_detail'),
    path('create-project/', views.launch_vision, name='create_project'),
    path('jobs/', views.opportunity_board, name='jobs'),
    path('project/<int:pk>/join/', views.pitch_for_collab, name='request_join'),
    path('join-requests/', views.collab_applications, name='join_requests'),
    path('my-requests/', views.my_pitches, name='my_join_requests'),
    path('chat/<int:request_id>/', views.collaboration_dialog, name='chat'),
    path('approve/<int:request_id>/', views.greenlight_artist, name='approve_request'),
    path('reject/<int:request_id>/', views.decline_application, name='reject_request'),
    path('inbox/', views.conversation_hub, name='inbox'),
    path('post/<int:pk>/comment/', views.share_feedback, name='add_comment'),
    path('message/<str:username>/', views.craft_message, name='send_message'),
    path('messages/', views.message_lounge, name='messages_inbox'),
    path('message-thread/<str:username>/', views.direct_connection, name='message_thread'),
    path('settings/', views.artist_studio, name='settings'),
    path('post/<int:post_id>/request-chat/', views.initiate_collab_chat, name='request_chat'),
    path('project/<int:project_id>/request-chat/', views.initiate_project_chat, name='request_chat_project'),
    path('chat-requests/', views.collaboration_queue, name='chat_requests_inbox'),
    path('chat-request/<int:chat_request_id>/approve/', views.accept_collaboration, name='approve_chat_request'),
    path('chat-request/<int:chat_request_id>/reject/', views.decline_collaboration, name='reject_chat_request'),
    path('chat/', views.conversation_lounge, name='unified_chat'),
    
    # 2Fa route
    path('setup-2fa/', views.fortify_account, name='setup_2fa'),
    path('disable-2fa/', views.unlock_vault, name='disable_2fa'),
    path('login-2fa/', views.vault_entry, name='login_2fa'),
    path('api/notification-count/', views.pulse_check, name='get_notification_count'),
]