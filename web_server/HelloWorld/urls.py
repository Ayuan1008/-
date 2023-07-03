from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.getmessag),
    path('login/', views.login),
    path('register/', views.register),
    path('usercenter/', views.usercenter),
    path('searchhistory/', views.searchhistory),
    path('updatepassword/', views.updatepassword),
    path('addorder/', views.addorder),
    path('searchorder/',views.searchorder)

]
