from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('identify', views.identify,name="identify"),
    path('login',views.Login,name="login"),
    path("verify",views.Verify,name="verify"),
    path('newreg',views.newreg,name="newreg"),
    path("update",views.update,name="update"),
    
]
