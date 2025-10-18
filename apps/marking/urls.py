from django.urls import path
from . import views

app_name = 'marking'

urlpatterns = [
    path('results/', views.exam_result_list_view, name='result_list'),
    path('results/<int:result_id>/', views.exam_result_detail_view, name='result_detail'),
    path('assignment/<int:assignment_id>/marks/', views.record_marks_view, name='record_marks'),
    path('dreva/<int:dreva_id>/progress/', views.dreva_progress_view, name='dreva_progress'),
]
