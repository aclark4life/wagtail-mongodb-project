from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django_mongodb.fields.ObjectIdAutoField"
    name = "home"
    label = "home"
