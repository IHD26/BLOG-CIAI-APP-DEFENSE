# blog/apps.py
from django.apps import AppConfig

class BlogConfig(AppConfig):
    """
    Configuration for the Blog application.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # Specify the default auto field for new models
    name = 'blog'  # The name of the application as it is referred to in code
    verbose_name = 'blog'  # A human-readable name for the application (optional)

