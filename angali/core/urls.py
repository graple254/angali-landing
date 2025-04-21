from django.urls import path
from .views import *

urlpatterns = [
    path('track/start/', track_start, name='track_start'),
    path('track/end/', track_end, name='track_end'),
    path('', home, name='home'),
]