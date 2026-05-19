from urllib import request
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from cr.models import Publication, Files, Category, FileCategory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Inscription, Paiement, Quitus, User
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
    paginator = Paginator(qs, 10)

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

    fichiers = Files.objects.filter(
        section='AESM'
    ).order_by('-date_upload')

    # =========================
    # SEARCH
    # =========================

    search = request.GET.get('search', '')

    if search:
        fichiers = fichiers.filter(
            nom_fichier__icontains=search
        )

    # =========================
    # CATEGORY
    # =========================

    category = request.GET.get('category', 'all')

    if category != 'all':
        fichiers = fichiers.filter(
            categorie__id=category
        )

    # =========================
    # PAGINATION
    # =========================

    paginator = Paginator(fichiers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = FileCategory.objects.filter(section='AESM')

    # =========================
    # AJAX
    # =========================

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'aesm/includes/fichier_list.html',
            {'fichiers': page_obj}
        )
        return JsonResponse({'html': html})

    return render(
        request,
        'aesm/fichiers.html',
        {
            'fichiers': page_obj,
            'page_obj': page_obj,
            'categories': categories,
        }
    )


def dowload_fichierView(request, fichier_id):
    fichier = get_object_or_404(
        Files,
        id=fichier_id
    )
    fichier.download_count += 1
    fichier.save()
    return FileResponse(fichier.fichier.open(), as_attachment=True)


@login_required
def creer_paiement(request):

    etudiant = Etudiant.objects.get(
        user=request.user
    )

    inscription = Inscription.objects.get(
        etudiant=etudiant
    )

    if inscription.statut == "paye":
        return redirect('dashboardAesm')

    if request.method == "POST":
        transaction_id = str(uuid.uuid4())

        paiement = Paiement.objects.create(
            inscription=inscription,
            montant=2000,
            statut='succes',
            transaction_id=transaction_id
        )

        inscription.statut = 'paye'
        inscription.save()

        verfification_url = (
            f"https://nandrianina04.pythonanywhere.com/aesm/verify/{transaction_id}/"
            
        )

        qr_file = generate_qr_code(verfification_url)
        pdf_file = generate_pdf(paiement.transaction_id, qr_file, etudiant)

        Quitus.objects.create(
            paiement=paiement,
            qr_code=qr_file,
            fichier_pdf=pdf_file
        )

        quitus = Quitus.objects.get(paiement=paiement)

        return render(
            request,
            'aesm/paiement_success.html',
            {'quitus': quitus}
        )

    return render(request, 'aesm/paiement.html')


@login_required
def simulation_success(request, transaction_id):
    paiement = get_object_or_404(
        Paiement,
        transaction_id=transaction_id
    )
    return render(
        request,
        'aesm/paiement_success.html',
        {'paiement': paiement}
    )


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
