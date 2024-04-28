from django.urls import path

from . import views

# URL routes for each view
urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('change_password/', views.change_password, name='change_password')
]
