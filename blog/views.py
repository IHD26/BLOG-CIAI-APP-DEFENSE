# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Article, Category, Reference, Tag, Contact, UserProfile
from .forms import ArticleForm, ContactForm, UserProfileForm, UserUpdateForm

from django.http import JsonResponse
from .models import Message
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

from django.shortcuts import render

def entrainements_view(request):
    return render(request, 'blog/entrainements.html')



def home(request):
    """
    Vue pour la page d'accueil du blog.
    Affiche les articles les plus récents et les catégories principales.
    """
    # Récupérer les 6 derniers articles
    latest_articles = Article.objects.filter(
        status='published',
        created_at__lte=timezone.now()
    ).order_by('-created_at')[:6]

    # Récupérer les catégories principales (celles qui ont le plus d'articles)
    main_categories = Category.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')[:4]

    # Récupérer les tags les plus populaires
    popular_tags = Tag.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')[:10]

    context = {
        'latest_articles': latest_articles,
        'main_categories': main_categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'blog/home.html', context)

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
        
        # Filtrage par catégorie si spécifié
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtrage par tag si spécifié
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Recherche si un terme de recherche est fourni
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            ).distinct()
        
        return queryset.order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Articles similaires (même catégorie)
        context['similar_articles'] = Article.objects.filter(
            category=article.category,
            status='published',
            published_at__lte=timezone.now()
        ).exclude(
            id=article.id
        ).select_related('author', 'category')[:3]

        # Statistiques de l'article
        context['article_stats'] = {
            'views': article.views,
            'comments_count': article.comments.count() if hasattr(article, 'comments') else 0,
        }

        # Catégories populaires
        context['popular_categories'] = Category.objects.annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        ).order_by('-article_count')[:5]

        # Tags populaires
        context['popular_tags'] = Tag.objects.annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        ).order_by('-article_count')[:10]

        return context

    def get_object(self, queryset=None):
        article = super().get_object(queryset)
        # Incrémenter le compteur de vues
        article.views += 1
        article.save(update_fields=['views'])
        return article

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article créé avec succès!')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm()
    
    return render(request, 'blog/article_form.html', {'form': form, 'action': 'Créer'})

@login_required
def article_update(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        messages.error(request, 'Vous n\'êtes pas autorisé à modifier cet article.')
        return redirect('blog:article_detail', slug=slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article mis à jour avec succès!')
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'blog/article_form.html', {'form': form, 'action': 'Modifier'})

@login_required
def article_delete(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        messages.error(request, 'Vous n\'êtes pas autorisé à supprimer cet article.')
        return redirect('blog:article_detail', slug=slug)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article supprimé avec succès!')
        return redirect('blog:article_list')
    
    return render(request, 'blog/article_confirm_delete.html', {'article': article})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'blog/category_detail.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre message a été envoyé avec succès!')
            return redirect('blog:contact')
    else:
        form = ContactForm()
    
    return render(request, 'blog/contact.html', {'form': form})

def about(request):
    return render(request, 'blog/about.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('blog:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'blog/profile.html', {'form': form})

def search(request):
    query = request.GET.get('q')
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()
    else:
        articles = Article.objects.none()
    
    context = {
        'articles': articles,
        'query': query,
    }
    return render(request, 'blog/search_results.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès!')
            return redirect('blog:article_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'blog/signup.html', {'form': form})

def send_suggestion(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre suggestion a été envoyée avec succès!')
            return redirect('blog:article_list')
    else:
        form = ContactForm()
    
    return render(request, 'blog/suggestion_form.html', {'form': form})

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('blog:article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Article créé avec succès!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Créer'
        return context

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    slug_url_kwarg = 'slug'

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author

    def form_valid(self, form):
        messages.success(self.request, 'Article mis à jour avec succès!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Modifier'
        return context

    def get_success_url(self):
        return reverse_lazy('blog:article_detail', kwargs={'slug': self.object.slug})
    






def entrainements_drones(request):
    return render(request, 'blog/drones.html')

def entrainements_forces_speciales(request):
    return render(request, 'blog/Forces_speciales.html')

def entrainements_Aviation(request):
    return render(request, 'blog/Aviation_strategique.html')

def entrainements_patrouille_maritime(request):
    return render(request, 'blog/entrainements_patrouille_maritime.html')


def drones_swarms(request):
    return render(request, 'blog/drones_swarms.html')


def chat_view(request):
    return render(request, 'blog/chatbox.html')



