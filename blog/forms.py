# blog/forms.py
from django import forms
from .models import Article, Reference, Contact, UserProfile, Category, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Entrez une adresse email valide.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'category', 'tags', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de l\'article'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Contenu de l\'article'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'data-placeholder': 'Sélectionnez des tags'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')
        self.fields['category'].queryset = Category.objects.all().order_by('name')

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['authors', 'title', 'journal', 'year', 'doi']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),  # Ensuring valid year range
            'doi': forms.URLInput(attrs={'placeholder': 'https://doi.org/...'}),  # Adding a placeholder for clarity
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre email'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet du message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre message'
            })
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parlez-nous de vous'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
