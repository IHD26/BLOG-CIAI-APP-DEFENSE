from django.urls import path
from . import views
from .views import home, ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView
from django.contrib.auth import views as auth_views
from .views import signup

from django.urls import path
from .views import entrainements_view  # <=== exactement ce nom


app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/category/<slug:category_slug>/', views.ArticleListView.as_view(), name='article_list_by_category'),
    path('articles/tag/<slug:tag_slug>/', views.ArticleListView.as_view(), name='article_list_by_tag'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<slug:slug>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<slug:slug>/delete/', views.article_delete, name='article_delete'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('signup/', views.signup, name='signup'),  # Pour l'inscription
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),  # Pour la connexion
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Pour la déconnexion
    path('suggestions/', views.send_suggestion, name='suggestions'),
    path('signup/', signup, name='signup'),
    path('entrainements/', views.entrainements_view, name='entrainements'),
    path('entrainements/drones/', views.entrainements_drones, name='entrainements_drones'),
    path('entrainements/entrainements_patrouille_maritime/', views.entrainements_patrouille_maritime, name='entrainements_patrouille_maritime'),    
    path('entrainements/Forces_speciales/', views.entrainements_forces_speciales, name='entrainements_forces_speciales'),
    path('entrainements/Aviation_strategique/', views.entrainements_Aviation, name='entrainements_Aviation_strategique'),
    path('entrainements/Drones_swarms/', views.drones_swarms, name='Drones_swarms'),
    path('chat/', views.chat_view, name='chatbox'),

]
