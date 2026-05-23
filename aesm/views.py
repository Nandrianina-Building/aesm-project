from urllib import request
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from cr.models import Publication, Files, Category, FileCategory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Inscription, Paiement, Quitus, User , TokiPayPaiement
from accounts.models import Etudiant
from .utils import generate_qr_code, generate_pdf
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import LigneBudget
from django.http import JsonResponse
from django.template.loader import render_to_string
from functools import wraps
from django.http import JsonResponse
from django.http import FileResponse

import secrets
import requests
import json
import logging
 
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
 
 
logger = logging.getLogger(__name__)
 
MONTANT_ADHESION = 2000   # Ariary

# =========================
# HELPER : MEMBRE ACTIF
# =========================

def membre_actif_required(view_func):
    """
    Decorator qui vérifie que l'utilisateur est connecté
    ET que son inscription est au statut 'paye'.
    Sinon redirige vers le dashboard avec un message d'erreur.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # 1. Doit être connecté
        if not request.user.is_authenticated:
            return redirect('account_login')

        # 2. Doit avoir un profil étudiant
        etudiant = Etudiant.objects.filter(
            user=request.user
        ).first()

        if not etudiant:
            return redirect('dashboardAesm')

        # 3. Doit avoir une inscription active (paye)
        inscription = Inscription.objects.filter(
            etudiant=etudiant
        ).first()

        if not inscription or inscription.statut != 'paye':
            return redirect('dashboardAesm')

        return view_func(request, *args, **kwargs)

    return wrapper

def scanner_qr(request):
    if not request.user.is_staff:
        return redirect('dashboardAesm')
    return render(
        request,
        'aesm/scanner.html'
    )

def verify_quitus(request, transaction_id):

    paiement = get_object_or_404(
        Paiement,
        transaction_id=transaction_id
    )

    etudiant = paiement.inscription.etudiant

    context = {

        'paiement': paiement,
        'etudiant': etudiant,
    }

    return render(
        request,
        'aesm/verify_quitus.html',
        context
    )
    
def dashboardAesmView(request):

    count_pub = Publication.objects.filter(
        section='AESM'
    ).count()

    publication = Publication.objects.filter(
        section='AESM'
    ).order_by(
        '-date_publication'
    )[:3]

    count_file = Files.objects.filter(
        section="AESM"
    ).count()

    count_actif = Inscription.objects.filter(
        statut='paye'
    ).count()

    count_evenement = Publication.objects.filter(
        section='AESM',
        categorie__name='Evenement'
    ).count()

    user = request.user

    etudiant = Etudiant.objects.filter(
        user=user
    ).first() if user.is_authenticated else None

    payement = Paiement.objects.filter(
        inscription__etudiant=etudiant
    ).first() if etudiant else None


    context = {
        'count_pub': count_pub,
        'count_file': count_file,
        'count_actif': count_actif,
        'count_evenement': count_evenement,
        'publication': publication,
        'user': user,
        'etudiant': etudiant,
        'payement': payement
    }

    if not request.user.is_authenticated:
        context['etat'] = "visiteur"
        return render(
            request,
            "aesm/dashboard_aesm.html",
            context
        )

    etudiant = Etudiant.objects.filter(
        user=request.user
    ).first()

    inscription = Inscription.objects.filter(
        etudiant=etudiant
    ).first() if etudiant else None

    if inscription and inscription.statut == "paye":
        context['etat'] = "actif"
        try:
            context['quitus'] = inscription.paiement.quitus
        except Quitus.DoesNotExist:
            verfification_url = f"https://nandrianina04.pythonanywhere.com/aesm/verify/{inscription.paiement.transaction_id}/"
            
            qr_file = generate_qr_code(verfification_url)
            pdf_file = generate_pdf(inscription.paiement.transaction_id, qr_file, etudiant)
            quitus = Quitus.objects.create(
                paiement=inscription.paiement,
                qr_code=qr_file,
                fichier_pdf=pdf_file
            )
            context['quitus'] = quitus
    else:
        context['etat'] = "en_attente"

    return render(
        request,
        "aesm/dashboard_aesm.html",
        context
    )


def liste_publication(request):
    """
    Liste des publications AESM avec :
    - Recherche full-text (titre + contenu)
    - Filtre par catégorie
    - Pagination 10 par page
    La pagination reste cohérente avec la recherche et le filtre actifs.
    """

    # ── Paramètres GET ────────────────────────────────────────
    search   = request.GET.get('q', '').strip()
    cat_id   = request.GET.get('category', '').strip()
    page_num = request.GET.get('page', 1)

    # ── Queryset de base ──────────────────────────────────────
    qs = Publication.objects.filter(
        section='AESM',
        statut='publie'
    ).select_related('categorie').order_by('-date_publication')

    # ── Filtre : recherche ────────────────────────────────────
    if search:
        qs = qs.filter(
            Q(titre__icontains=search) | Q(contenu__icontains=search)
        )

    # ── Filtre : catégorie ────────────────────────────────────
    if cat_id and cat_id != 'all':
        try:
            qs = qs.filter(categorie__id=int(cat_id))
        except (ValueError, TypeError):
            pass

    # ── Pagination ────────────────────────────────────────────
    paginator = Paginator(qs, 9)

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = Category.objects.filter(section='AESM')

    return render(request, 'aesm/publication.html', {
        'publications': page_obj,
        'page_obj':     page_obj,
        'categories':   categories,
        'search':       search,
        'cat_id':       cat_id,
        'total':        paginator.count,
    })

def publication_detail_aesm(request, pub_id):
    pub = get_object_or_404(
        Publication,
        id=pub_id
    )
    return render(
        request,
        'aesm/publication_detail_aesm.html',
        {'pub': pub}
    )

@login_required
def like_publication(request, pub_id):

    if request.method != "POST":

        return JsonResponse({
            'error': 'Méthode invalide'
        }, status=400)

    publication = get_object_or_404(
        Publication,
        id=pub_id,
        section='AESM'
    )

    utilisateur = request.user

    liked = False

    if publication.like.filter(id=utilisateur.id).exists():

        publication.like.remove(utilisateur)

    else:

        publication.like.add(utilisateur)
        liked = True

    return JsonResponse({

        'liked': liked,
        'likes_count': publication.like.count()

    })
# =========================
# LISTE FICHIERS — MEMBRES ACTIFS UNIQUEMENT
# =========================

@membre_actif_required
def liste_fichiersView(request):
    """
    Liste des fichiers AESM avec :
    - Recherche par nom de fichier
    - Filtre par catégorie
    - Pagination 10 par page
    La pagination conserve search + category dans l'URL.
    """

    # ── Paramètres GET ────────────────────────────────────────
    search   = request.GET.get('search', '').strip()
    cat_id   = request.GET.get('category', 'all').strip()
    page_num = request.GET.get('page', 1)

    # ── Queryset de base ──────────────────────────────────────
    qs = Files.objects.filter(
        section='AESM'
    ).select_related('categorie').order_by('-date_upload')

    # ── Filtre : recherche ────────────────────────────────────
    if search:
        qs = qs.filter(nom_fichier__icontains=search)

    # ── Filtre : catégorie ────────────────────────────────────
    if cat_id and cat_id != 'all':
        try:
            qs = qs.filter(categorie__id=int(cat_id))
        except (ValueError, TypeError):
            pass

    # ── Pagination ────────────────────────────────────────────
    paginator = Paginator(qs, 10)

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = FileCategory.objects.filter(section='AESM')

    return render(request, 'aesm/fichiers.html', {
        'fichiers':   page_obj,
        'page_obj':   page_obj,
        'categories': categories,
        'search':     search,
        'cat_id':     cat_id,
        'total':      paginator.count,
    })
def dowload_fichierView(request, fichier_id):
    fichier = get_object_or_404(
        Files,
        id=fichier_id
    )
    fichier.download_count += 1
    fichier.save()
    return FileResponse(fichier.fichier.open(), as_attachment=True)


# ───────────────────────────────────────────────────────────────────
# HELPER — Authentification TokiPay
# Le token expire dans 1h — on en récupère un frais à chaque paiement.
# Pour une app à fort trafic, mettre en cache avec django-cache ou Redis.
# ───────────────────────────────────────────────────────────────────
 
def _get_tokipay_token():
    '''
    POST /auth/token → access_token
    Retourne le token ou lève une exception.
    '''
    resp = requests.post(
        f'{settings.TOKIPAY_BASE_URL}/auth/token',
        json={
            'client_id':     settings.TOKIPAY_CLIENT_ID,
            'client_secret': settings.TOKIPAY_CLIENT_SECRET,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()['access_token']
 
 
# ───────────────────────────────────────────────────────────────────
# HELPER — Finaliser le paiement (Quitus + PDF)
# ───────────────────────────────────────────────────────────────────
 
def _finaliser(tokipay_paiement):
    '''
    Crée le Paiement Django + le Quitus (QR + PDF).
    Idempotent : si le Quitus existe déjà, ne rien faire.
    '''
    inscription = tokipay_paiement.inscription
    etudiant    = inscription.etudiant
 
    # Idempotence — évite les doublons si le webhook arrive deux fois
    if Paiement.objects.filter(
        transaction_id=tokipay_paiement.reference
    ).exists():
        return Quitus.objects.get(
            paiement__transaction_id=tokipay_paiement.reference
        )
 
    paiement = Paiement.objects.create(
        inscription=inscription,
        montant=tokipay_paiement.montant,
        statut='succes',
        transaction_id=tokipay_paiement.reference,
    )
 
    inscription.statut = 'paye'
    inscription.save()
 
    verification_url = (
        f"{settings.SITE_URL}/aesm/verify/{tokipay_paiement.reference}/"
    )
    qr_file  = generate_qr_code(verification_url)
    pdf_file = generate_pdf(
        paiement.transaction_id, qr_file, etudiant, paiement
    )
 
    quitus = Quitus.objects.create(
        paiement=paiement,
        qr_code=qr_file,
        fichier_pdf=pdf_file,
    )
 
    tokipay_paiement.statut = 'valide'
    tokipay_paiement.save()
 
    return quitus
 
 
# ───────────────────────────────────────────────────────────────────
# VUE 1 — Page de paiement  →  appelle TokiPay  →  redirect
# ───────────────────────────────────────────────────────────────────
 
@login_required
def creer_paiement(request):
    etudiant    = Etudiant.objects.get(user=request.user)
    inscription = Inscription.objects.get(etudiant=etudiant)
 
    if inscription.statut == 'paye':
        return redirect('dashboardAesm')
 
    if request.method == 'POST':
        # Référence unique côté AESM
        reference = f'AESM-{uuid.uuid4().hex[:12].upper()}'
 
        # Sauvegarder AVANT l'appel API pour que le webhook retrouve l'inscription
        tokipay_obj = TokiPayPaiement.objects.create(
            reference=reference,
            inscription=inscription,
            montant=MONTANT_ADHESION,
        )
 
        try:
            # ── ÉTAPE 1 : Obtenir le token ──────────────────────
            token = _get_tokipay_token()
 
            # ── ÉTAPE 2 : Créer le paiement ─────────────────────
            resp = requests.post(
                f'{settings.TOKIPAY_BASE_URL}/payments/checkout',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type':  'application/json',
                },
                json={
                    'amount':    MONTANT_ADHESION,
                    'reference': reference,          # external_reference dans le webhook
                    'lines': [
                        {
                            'description': 'Adhésion AESM',
                            'unit_price':  MONTANT_ADHESION,
                            'quantity':    1,
                        }
                    ],
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
 
            # Sauvegarder le payment_id TokiPay
            tokipay_obj.payment_id = data.get('payment_id', '')
            tokipay_obj.save()
 
            checkout_url = data['checkout_url']
 
            # ── ÉTAPE 3 : Rediriger vers TokiPay ────────────────
            return redirect(checkout_url)
 
        except Exception as e:
            logger.error('TokiPay — erreur création paiement : %s', e)
            tokipay_obj.statut = 'echec'
            tokipay_obj.save()
            return redirect('paiement_echec')
 
    # GET → afficher la page de paiement
    return render(request, 'aesm/paiement.html', {
        'montant': MONTANT_ADHESION,
    })
 
 
# ───────────────────────────────────────────────────────────────────
# VUE 2 — Retour après paiement (redirect depuis TokiPay)
# NE PAS finaliser ici — attendre le webhook.
# ───────────────────────────────────────────────────────────────────
 
@login_required
def tokipay_retour(request):
    '''
    TokiPay redirige l'utilisateur ici après qu'il ait soumis
    sa preuve de paiement. Le paiement n'est pas encore validé.
    On affiche une page d'attente.
    '''
    return render(request, 'aesm/tokipay_attente.html')
 
 
# ───────────────────────────────────────────────────────────────────
# VUE 3 — Webhook TokiPay  (POST serveur→serveur)
# C'est ici que le paiement est officiellement confirmé.
# ───────────────────────────────────────────────────────────────────
 
@csrf_exempt     # TokiPay n'envoie pas de CSRF token
@require_POST
def tokipay_webhook(request):
    '''
    TokiPay appelle ce endpoint quand le paiement est validé.
    Header : X-Client-Secret = ton client_secret
    Body   : { event, payment: { external_reference, status, ... } }
    '''
 
    # ── 1. Vérifier l'authenticité via X-Client-Secret ──────────
    secret_recu = request.headers.get('X-Client-Secret', '')
    if not secrets.compare_digest(
        secret_recu,
        settings.TOKIPAY_CLIENT_SECRET,
    ):
        logger.warning('TokiPay webhook — secret invalide')
        return HttpResponse(status=401)
 
    # ── 2. Parser le body JSON ───────────────────────────────────
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)
 
    event   = data.get('event')
    payment = data.get('payment', {})
 
    logger.info('TokiPay webhook reçu — event=%s', event)
 
    # ── 3. Traiter uniquement payment.validated ──────────────────
    if event != 'payment.validated':
        return HttpResponse('event ignoré', status=200)
 
    # external_reference = la reference qu'on a envoyée lors de la création
    external_reference = payment.get('external_reference')
    if not external_reference:
        return HttpResponse(status=400)
 
    # ── 4. Retrouver le paiement TokiPay en DB ──────────────────
    try:
        tokipay_obj = TokiPayPaiement.objects.get(
            reference=external_reference
        )
    except TokiPayPaiement.DoesNotExist:
        logger.error('TokiPay — référence introuvable : %s', external_reference)
        return HttpResponse(status=404)
 
    # ── 5. Enrichir avec les données du webhook ──────────────────
    tokipay_obj.provider     = payment.get('provider', '')
    tokipay_obj.sender_phone = payment.get('sender_phone', '')
    tokipay_obj.save()
 
    # ── 6. Finaliser le paiement (Quitus + PDF) ──────────────────
    try:
        _finaliser(tokipay_obj)
    except Exception as e:
        logger.error('TokiPay — finalisation échouée : %s', e)
        return HttpResponse(status=500)
 
    # ── 7. Retourner 200 dans les 30 secondes ────────────────────
    return HttpResponse('OK', status=200)
 
 
# ───────────────────────────────────────────────────────────────────
# VUE 4 — Succès
# ───────────────────────────────────────────────────────────────────
 
@login_required
def paiement_success(request, reference):
    quitus = get_object_or_404(
        Quitus,
        paiement__transaction_id=reference,
    )
    return render(request, 'aesm/paiement_success.html', {'quitus': quitus})
 
 
# ───────────────────────────────────────────────────────────────────
# VUE 5 — Échec
# ───────────────────────────────────────────────────────────────────
 
@login_required
def paiement_echec(request):
    return render(request, 'aesm/paiement_echec.html')
# =========================
# DASHBOARD BUDGET — MEMBRES ACTIFS UNIQUEMENT
# =========================

@membre_actif_required
def dashboard_budget(request):

    # =========================
    # EVOLUTION MENSUELLE
    # =========================
    evolution_mensuelle = (
        LigneBudget.objects
        .annotate(mois=TruncMonth('date_operation'))
        .values('mois', 'type')
        .annotate(total=Sum('montant'))
        .order_by('mois')
    )

    # =========================
    # RECETTES PAR CATEGORIE
    # =========================
    recettes_categories = (
        LigneBudget.objects
        .filter(type='recette')
        .values('categorie__nom')
        .annotate(total=Sum('montant'))
    )

    # =========================
    # DEPENSES PAR CATEGORIE
    # =========================
    depenses_categories = (
        LigneBudget.objects
        .filter(type='depense')
        .values('categorie__nom')
        .annotate(total=Sum('montant'))
    )

    # =========================
    # HISTORIQUE TRANSACTIONS
    # =========================
    transactions = (
        LigneBudget.objects
        .select_related('categorie', 'rapport')
        .order_by('-date_operation')[:10]
    )

    # =========================
    # TOTAL RECETTES
    # =========================
    total_recettes = (
        LigneBudget.objects
        .filter(type='recette')
        .aggregate(total=Sum('montant'))['total']
        or 0
    )

    # =========================
    # TOTAL DEPENSES
    # =========================
    total_depenses = (
        LigneBudget.objects
        .filter(type='depense')
        .aggregate(total=Sum('montant'))['total']
        or 0
    )

    # =========================
    # TAUX EPARGNE
    # =========================
    if total_recettes > 0:
        taux_epargne = (
            (total_recettes - total_depenses) / total_recettes
        ) * 100
    else:
        taux_epargne = 0

    # =========================
    # MOYENNES
    # =========================
    nombre_mois = 12
    recette_moyenne = total_recettes / nombre_mois
    depense_moyenne = total_depenses / nombre_mois

    # =========================
    # RATIO DEPENSE
    # =========================
    if total_recettes > 0:
        ratio_depense = (total_depenses / total_recettes) * 100
    else:
        ratio_depense = 0

    # =========================
    # RECOMMANDATION
    # =========================
    if ratio_depense > 80:
        recommendation = "Les dépenses sont trop élevées."
    elif taux_epargne > 50:
        recommendation = "Bonne gestion financière."
    else:
        recommendation = "Situation financière stable."

    contexte = {
        'evolution_mensuelle': list(evolution_mensuelle),
        'recettes_categories': list(recettes_categories),
        'depenses_categories': list(depenses_categories),
        'transactions': transactions,
        'total_recettes': total_recettes,
        'total_depenses': total_depenses,
        'taux_epargne': taux_epargne,
        'recette_moyenne': recette_moyenne,
        'depense_moyenne': depense_moyenne,
        'ratio_depense': ratio_depense,
        'recommendation': recommendation,
    }

    return render(
        request,
        'aesm/dashboard_budget.html',
        contexte
    )
