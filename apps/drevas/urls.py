from django.urls import path
from . import views

app_name = 'drevas'

urlpatterns = [
    path('', views.dreva_list_view, name='dreva_list'),
    path('<int:dreva_id>/', views.dreva_detail_view, name='dreva_detail'),
    path('create/', views.dreva_create_view, name='dreva_create'),
    path('<int:dreva_id>/edit/', views.dreva_edit_view, name='dreva_edit'),
    path('sessions/', views.training_session_list_view, name='session_list'),
    path('sessions/<int:session_id>/', views.training_session_detail_view, name='session_detail'),
    path('sessions/create/', views.training_session_create_view, name='session_create'),
]
