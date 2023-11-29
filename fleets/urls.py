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
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.list_fleet, name='list_fleet'),
    path('history', views.list_fleet_history, name='list_fleet_history'),
    path('create', views.create_fleet, name='create_fleet'),
    path('<int:pk>/', views.view_fleet, name='fleet_detail'),
    path('<int:pk>/edit', views.edit_fleet, name='edit_fleet'),
    path('<int:pk>/delete', views.delete_fleet, name='delete_fleet'),
    path('<int:pk>/preping', views.preping_fleet, name='preping_fleet'),
    path('<int:pk>/ping', views.ping_fleet, name='ping_fleet'),
    path('<int:pk>/esi', views.create_esi_fleet, name='create_esi_fleet'),
    path('<int:pk>/esi/refresh_members', views.refresh_esi_fleet_members, name='refresh_esi_fleet_members'),
    path('<int:pk>/esi/delete', views.delete_esi_fleet, name='delete_esi_fleet'),
    path('fittings', views.list_fittings, name='list_fittings'),
    path('fittings/cargo', views.view_fittings_items, name='all_fittings_items'),
    path('fittings/<slug:fitting_slug>/', views.view_fitting, name='fitting_detail'),
    path('fittings/<slug:fitting_slug>/multibuy', views.view_fitting_multibuy, name='fitting_multibuy'),
    path('doctrines', views.list_doctrines, name='list_doctrines'),
    path('doctrines/<slug:doctrine_slug>/', views.view_doctrine, name='doctrine_detail'),
    path('doctrines/<slug:doctrine_slug>/fitting/<slug:fitting_slug>/', views.view_doctrine_fitting, name='doctrine_fitting_detail'),
    path('fittings/mark_as_complete/<str:alliance>/', views.mark_as_complete, name='mark_as_complete'),
]
