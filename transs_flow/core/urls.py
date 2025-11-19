from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_issue, name='create_issue'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('issue/<int:issue_id>/reminder/', views.send_reminder, name='send_reminder'),
]