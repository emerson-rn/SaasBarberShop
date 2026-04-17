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
from django.urls import path
from agendamentos import views
from agendamentos.views import dashboard_barbeiro, lista_estoque, lista_equipe

urlpatterns = [
    # Página inicial (abre direto na dashboard)
    path('', dashboard_barbeiro, name='index'),
    
    # Painel Administrativo do Django
    path('admin/', admin.site.urls),
    
    # Telas customizadas com o novo Frontend
    path('dashboard/', dashboard_barbeiro, name='dashboard'),
    path('estoque/', lista_estoque, name='estoque'),
    path('equipe/', lista_equipe, name='equipe'),
    path('novo-agendamento/', views.novo_agendamento, name='novo_agendamento'),
    path('editar-agendamento/<int:pk>/', views.editar_agendamento, name='editar_agendamento'),
    path('estoque/novo/', views.novo_produto, name='novo_produto'),
    path('estoque/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('estoque/deletar/<int:pk>/', views.deletar_produto, name='deletar_produto'),
    
    # Novas funcionalidades
    path('historico/', views.historico_agendamentos, name='historico'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('agendamento/status/<int:pk>/', views.atualizar_status_agendamento, name='atualizar_status'),
]