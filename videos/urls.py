from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.searching,name='searching'),
    path('download/',views.download,name='download'),
]