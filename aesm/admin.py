from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import (
    Rapport,
    LigneBudget,
    CategorieBudget
)


@admin.register(CategorieBudget)
class CategorieBudgetAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom'
    )
    
    search_fields = (
        'nom',
    )


@admin.register(LigneBudget)
class LigneBudgetAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'rapport',
        'type',
        'categorie',
        'montant',
        'date_operation'
    )

    list_filter = (
        'type',
        'categorie',
        'date_operation'
    )

    search_fields = (
        'description',
    )

    date_hierarchy = 'date_operation'


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'admin',
        'date_creation',
        'total_recettes',
        'total_depenses',
        'solde'
    )

    search_fields = (
        'titre',
    )

    readonly_fields = (
        'total_recettes',
        'total_depenses',
        'solde'
    )