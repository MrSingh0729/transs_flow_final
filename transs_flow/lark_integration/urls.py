from django.urls import path
from . import views


app_name = 'lark_integration'


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.lark_login, name='login'),
    path('callback/', views.lark_callback, name='callback'),
    path('webhook/', views.lark_webhook, name='webhook'),
]