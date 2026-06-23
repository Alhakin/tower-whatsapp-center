from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/novo/', views.usuario_form, name='usuario_novo'),
    path('usuarios/<int:pk>/editar/', views.usuario_form, name='usuario_editar'),
    path('listas/', views.listas, name='listas'),
    path('listas/nova/', views.lista_form, name='lista_nova'),
    path('listas/<int:pk>/', views.lista_detalhe, name='lista_detalhe'),
    path('listas/<int:pk>/contato/novo/', views.contato_form, name='contato_novo'),
    path('disparos/', views.disparos, name='disparos'),
    path('disparos/novo/', views.disparo_novo, name='disparo_novo'),
    path('conversas/', views.conversas, name='conversas'),
    path('conversas/finalizadas/', views.conversas_finalizadas, name='conversas_finalizadas'),
    path('conversas/nova/', views.conversa_nova, name='conversa_nova'),
    path('conversas/<int:pk>/', views.conversa_detalhe, name='conversa_detalhe'),
    path('conversas/<int:pk>/assumir/', views.conversa_assumir, name='conversa_assumir'),
    path('conversas/<int:pk>/transferir/', views.conversa_transferir, name='conversa_transferir'),
    path('conversas/<int:pk>/editar-contato/', views.conversa_editar_contato, name='conversa_editar_contato'),
    path('conversas/<int:pk>/solicitar-transferencia/', views.conversa_solicitar_transferencia, name='conversa_solicitar_transferencia'),
    path('conversas/<int:pk>/aguardar/', views.conversa_aguardar, name='conversa_aguardar'),
    path('conversas/<int:pk>/finalizar/', views.conversa_finalizar, name='conversa_finalizar'),
    path('conversas/<int:pk>/reabrir/', views.conversa_reabrir, name='conversa_reabrir'),
    path('conversas/<int:pk>/simular-recebida/', views.simular_recebida, name='simular_recebida'),
    path('whatsapp-api/', views.whatsapp_api_config, name='whatsapp_api_config'),
    path('whatsapp-api/logs/', views.whatsapp_api_logs, name='whatsapp_api_logs'),
    path('whatsapp-api/testar/', views.whatsapp_api_testar, name='whatsapp_api_testar'),
    path('api/whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
]
