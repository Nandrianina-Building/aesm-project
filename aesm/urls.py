from django.urls import path
from . import views

urlpatterns = [
    path(
        'dashboard_aesm/',
        views.dashboardAesmView , 
        name="dashboardAesm"
    ),
    
    path(
        'list_publication_aesm/',
        views.liste_publication, 
        name='publication_easm'
    ),
    
    path(
        'list_fichier_aesm/',
        views.liste_fichiersView , 
        name="list_fichier_aesm"
    ),
    
    path(
        'dowload/<int:fichier_id>',
        views.dowload_fichierView , 
        name = 'download_fichier_aesm'
    ),
    
    path('payement/',
         views.creer_paiement,
         name='payement_adhesion'),
 
    # TokiPay redirige ici après paiement
    path('payement/retour/',
         views.tokipay_retour,
         name='tokipay_retour'),
 
    # Webhook TokiPay (POST serveur→serveur)
    path('payement/webhook/',
         views.tokipay_webhook,
         name='tokipay_webhook'),
 
    # Succès (après finalisation)
    path('payement/success/<str:reference>/',
         views.paiement_success,
         name='paiement_success'),
 
    # Échec / annulation
    path('payement/echec/',
         views.paiement_echec,
         name='paiement_echec'),
    
    path(
        'dashboard-budget/',
        views.dashboard_budget,
        name='dashboard_budget'
    ),
    
    path(
        'publication_detail_aesm/<int:pub_id>/',
        views.publication_detail_aesm,
        name='publication_detail_aesm'
    ),
     path(
        'toggle_like/<int:pub_id>/',
        views.like_publication,
        name='toggle_like'
    ),
     path(
        'scanner/',
        views.scanner_qr,
        name='scanner_qr'
    ),
     path(
        'verify/<str:transaction_id>/',
        views.verify_quitus,
        name='verify_quitus'
    ),
]
