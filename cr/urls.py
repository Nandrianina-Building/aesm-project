from django.urls import path
from . import views

urlpatterns = [
    path(
        'dashboard_cr', 
        views.dashboardCrView , 
        name="dashboardCr"
    ),
    
    path(
        'list_publication_cr/',
        views.liste_publicationView, 
        name='publication_cr'
    ),
    path(
        'publication_detail_cr/<int:pub_id>/',
        views.publication_detailView, 
        name='publication_detail_cr'
    ),
    path(
        'list_fichier_cr/',
        views.liste_fichiersView , 
        name="list_fichier"
    ),
    
    path(
        'dowload/<int:fichier_id>',
        views.dowload_fichierView , 
        name = 'download_fichier'
    )
]
