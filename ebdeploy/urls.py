from django.contrib import admin
from django.urls import path
import gyuri.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',gyuri.views.home,name='home')
]
