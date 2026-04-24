"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from agendamentos import views
from agendamentos.views import dashboard_barbeiro, lista_estoque, lista_equipe
from usuarios import views as usuarios_views

urlpatterns = [
    # Página inicial (abre direto na dashboard)
    path('', dashboard_barbeiro, name='index'),
    
    # URLs de autenticação do Django
    path('', include('django.contrib.auth.urls')),
    
    # Painel Administrativo do Django
    path('admin/', admin.site.urls),
    
    # Telas customizadas com o novo Frontend
    path('dashboard/', dashboard_barbeiro, name='dashboard'),
    path('estoque/', lista_estoque, name='estoque'),
    path('equipe/', lista_equipe, name='equipe'),
    path('novo-agendamento/', views.novo_agendamento, name='novo_agendamento'),
    path('editar-agendamento/<int:pk>/', views.editar_agendamento, name='editar_agendamento'),
    path('excluir-agendamento/<int:pk>/', views.excluir_agendamento, name='excluir_agendamento'),
    path('estoque/novo/', views.novo_produto, name='novo_produto'),
    path('estoque/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('estoque/deletar/<int:pk>/', views.deletar_produto, name='deletar_produto'),
    
    # Novas funcionalidades
    path('historico/', views.historico_agendamentos, name='historico'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('agendamento/status/<int:pk>/', views.atualizar_status_agendamento, name='atualizar_status'),
    path('agendamento/verificar-pendentes/', views.verificar_agendamentos_pendentes, name='verificar_pendentes'),
    path('agendamento/confirmar/<int:pk>/', views.confirmar_chegada, name='confirmar_chegada'),
    path('painel-admin/', views.painel_admin, name='painel_admin'),
    path('meus-agendamentos/', views.portal_cliente, name='portal_cliente'),
    path('portal-barbeiro/', views.portal_barbeiro, name='portal_barbeiro'),
    path('avaliacoes/', views.avaliacoes, name='avaliacoes'),
    path('avaliacoes/nova/', views.nova_avaliacao, name='nova_avaliacao'),
    
    # Usuários
    path('novo-usuario/', usuarios_views.cadastrar_usuario, name='novo_usuario'),
]