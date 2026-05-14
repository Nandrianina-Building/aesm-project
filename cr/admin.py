from django.contrib import admin
from .models import Publication , Category , Files ,FileCategory
# Register your models here.
@admin.register(Category)
class CategorieAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    search_fields = (
        'name',
    )
@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'admin',
        'section',
        'statut',
        'date_publication'
    )
    
    list_filter = (
        'section',
        'categorie',
        'statut',
        'date_publication'
    )
    search_fields = (
         'titre',
         'contenu',
         'categorie',
         'admin_username'
     )
@admin.register(Files)
class FichierAdmin(admin.ModelAdmin):
    list_display = (
        'nom_fichier',
        'section',
        'categorie',
        'download_count'
    )
    list_filter = (
        'nom_fichier',
        'section',
        'date_upload',
        'categorie'
    )
    search_fields = (
        'nom_fichier',
        'contenu',
        'admin_username',
        'categorie'
    )
@admin.register(FileCategory)
class CategorieFileAdmin(admin.ModelAdmin):
    list_display = (
        'nom',
    )
    search_fields = (
        'nom',
    )