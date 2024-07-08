from django.urls import path,include
from . import views


urlpatterns=[
    path('',views.searching,name='searching'),
    path('download/',views.download,name='download'),
    path('goback_with_error/', views.goback_with_error, name='goback_with_error'),
]