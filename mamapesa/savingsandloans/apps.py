from django.apps import AppConfig


class SavingsandloansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'savingsandloans'
    
    def ready(self):
        from . import signals
        # from . import newSignals
        
