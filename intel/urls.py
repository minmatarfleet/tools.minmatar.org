"""tools URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.views.generic import TemplateView
from . import views 

urlpatterns = [
    path('structures', views.list_structures, name='list-structures'),
    path('structures/<int:structure_id>/', views.view_structure, name='view-structure'),
    path('structures/<int:structure_id>/delete', views.delete_structure, name='delete-structure'),
    path('structures/create', views.create_structure, name='create-structure'),
    path('structures/campaigns', views.list_structure_campaigns, name='list-structure-campaigns'),
    path('structures/campaigns/<int:campaign_id>/', views.view_structure_campaign, name='view-structure-campaign'),
]