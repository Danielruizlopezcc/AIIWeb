from . import views
from django.urls import path

urlpatterns = [
    path('', views.main, name='main'),
    path('juegos/', views.juegos, name='juegos'),
    path('scraping/', views.scraping, name='scraping'),
    path('scraping_manual/', views.scraping_manual, name='scraping_manual'),
    path('juegos/<int:juego_id>/', views.detalle_juego, name='detalle_juego'),    

] 
