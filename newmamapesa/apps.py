from django.apps import AppConfig


class NewmamapesaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newmamapesa'
    
    def ready(self):
        from . import signals
