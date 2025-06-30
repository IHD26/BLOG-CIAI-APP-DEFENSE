from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Category, Tag, Contact, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Nombre d\'articles'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Nombre d\'articles'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'views', 'image_preview')
    list_filter = ('status', 'category', 'author', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-published_at', '-created_at')
    filter_horizontal = ('tags',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'content', 'image')
        }),
        ('Catégorisation', {
            'fields': ('category', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'published_at')
        }),
        ('Métadonnées', {
            'fields': ('author', 'views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = 'Aperçu'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_preview', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('user', 'bio', 'avatar')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.avatar.url)
        return "Pas d'avatar"
    avatar_preview.short_description = 'Avatar'