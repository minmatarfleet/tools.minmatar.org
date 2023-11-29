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
    path('public', views.public_contract_list, name='public-contract-list'),
    path('publicdoctrines', views.public_doctrine_contract_list, name='public-doctrine-contract-list'),
    path('alliancedoctrines', views.alliance_doctrine_contract_list, name='alliance-doctrine-contract-list'),
    path('taxes', views.taxes, name='contract-taxes'),
    path('sales/fittings', views.sales_fittings, name='contract-sales-fittings'),
    path('sales/fittings.json', views.sales_fittings_json, name='contract-sales-fittings-json'),
    path('sales/ships', views.sales_ships, name='contract-sales-ships'),
    path('sales/ships.json', views.sales_ships_json, name='contract-sales-ships-json'),
    path('sales/items', views.sales_items, name='contract-sales-items'),
    path('sales/items.json', views.sales_items_json, name='contract-sales-items-json'),
    path('statistics.json', views.statistics_json, name='contract-statistics'),
    path('entities.json', views.contract_entities_json, name='contract-entities-json'),
    path('create_contract_character_entity', views.create_contract_character_entity, name='create-contract-character-entity'),
    path('create_contract_corporation_entity', views.create_contract_corporation_entity, name='create-contract-corporation-entity'),
    path('submit_contract_entity', views.submit_contract_entity, name='submit-contract-entity'),
    path('settings/<int:entity_id>/', views.settings, name='contract-entity-settings'),
    path('settings/<int:entity_id>/refresh', views.refresh_contract_corporation_entity_token, name='contract-entity-refresh'),
    path('submit_contract_entity_reponsibility', views.submit_contract_entity_reponsibility, name='submit-contract-entity-responsibility'),
    path('submit_contract_entity_manager', views.submit_contract_entity_manager, name='submit-contract-entity-manager'),
    path('delete_contract_entity/<int:entity_id>/', views.delete_contract_entity, name='delete-contract-entity'),
    path('delete_contract_entity_manager/<int:manager_id>/', views.delete_contract_entity_manager, name='delete-contract-entity-manager'),
    path('delete_contract_entity_reponsibility/<int:entity_id>/<int:expectation_id>/', views.delete_contract_entity_responsbility, name='delete-contract-entity-reponsibility'),
]
