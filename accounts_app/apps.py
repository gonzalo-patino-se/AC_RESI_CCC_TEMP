from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts_app'
    
    # Keep the original label to avoid migration/table churn
    label = "accounts"

