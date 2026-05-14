from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.instructions_faq,
        name='instructions_faq'
    )
]