from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list_view, name='exam_list'),
    path('<int:exam_id>/', views.exam_detail_view, name='exam_detail'),
    path('create/', views.exam_create_view, name='exam_create'),
    path('<int:exam_id>/assign/', views.exam_assign_view, name='exam_assign'),
    path('assignment/<int:assignment_id>/pdf/', views.generate_exam_paper_view, name='generate_paper'),
]
