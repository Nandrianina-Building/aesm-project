from django.shortcuts import render ,get_object_or_404 ,redirect
from .models import Publication , Files , FileCategory , Category
from django.core.paginator import Paginator
from django.contrib.auth.views import redirect_to_login
from django.db.models import F
from django.http import FileResponse

def dashboardCrView(request):
    
    categories = Category.objects.filter(
        section='CR'
    )
    publications = Publication.objects.filter(
        section='CR',
        statut='publie'
    )[:2]
    
    return render(
        request,
        "cr/dashboard_cr.html",
        {
            'categories': categories,
            'publications': publications
        }
        
    )

def liste_publicationView(request):
    categories = Category.objects.filter(
        section='CR'
    )
    
    publications = Publication.objects.filter(
        section='CR'
    )
    
    return render(
        request,
        "cr/publication.html",
        {
            'publications' : publications,
            'categories' : categories
        }
    )
    
def publication_detailView(request , pub_id):
    publication = get_object_or_404(
        Publication,
        id = pub_id,
        section = 'CR'
    )
    publication.count_view += 1
    publication.save()
    
    publication.refresh_from_db()
    return render(
        request,
        'cr/publication_detail.html',
        {
            'publication' : publication
        }
    )

def liste_fichiersView(request):
    categories = FileCategory.objects.filter(
        section='CR'
    )
        # Les utilisateurs non connectés ou inactifs ne voient que les fichiers publics
    fichiers = Files.objects.filter(
        section='CR',
        access='public'
    ).order_by('-date_upload')
    
    
    return render(
        request,
        'cr/fichiers.html',
        {
            'fichiers' : fichiers,
            'categories' : categories
        }
    )

def dowload_fichierView(request, fichier_id):
    fichier = get_object_or_404(
        Files,
        id=fichier_id 
    )
    
    # Si l'utilisateur est actif, autoriser le téléchargement
    fichier.download_count += 1
    fichier.save()
    return FileResponse(fichier.fichier.open(), as_attachment=True)
