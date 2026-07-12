from django.urls import path
from . import views

app_name = 'follows'

urlpatterns = [
    path('toggle/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('status/<int:user_id>/', views.get_follow_status, name='follow_status'),
]