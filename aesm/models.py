from django.db import models
from accounts.models import Etudiant
from django.contrib.auth.models import User

class Inscription(models.Model):
    STATUS_CHOICES =  [
        ('en_attente' , 'En attente'),
        ('paye' , 'paye'),
        ('expire' , 'expire')
    ]
    
    etudiant = models.OneToOneField(
        Etudiant,
        on_delete=models.CASCADE
    )
    statut =  models.CharField(
        choices=STATUS_CHOICES,
        default='en_attente',
        max_length=20
    )
    
    date_inscription = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"Inscription {self.etudiant}"
    
class Paiement(models.Model):
    STATUT_CHOICES = [
        ('pending', 'En attente'),
        ('succes' , 'Succès'),
        ('echec' , 'Echec')
    ]
    inscription = models.OneToOneField(
        Inscription,
        on_delete=models.CASCADE,
        related_name='paiement'
    )
    montant = models.IntegerField()
    date_payement = models.DateTimeField(
        auto_now_add=True
    )
    statut = models.CharField(
        choices=STATUT_CHOICES,
        max_length=20,
        default='pending'
    )
    transaction_id = models.CharField(
        max_length=100
    )
    
    payment_url = models.URLField(blank=True)
    def __str__(self):
        return f"Payement de {self.transaction_id}"
 
 
class TokiPayPaiement(models.Model):
    '''
    Stocke chaque tentative de paiement TokiPay.
    Permet de retrouver l'inscription depuis le webhook
    sans dépendre de la session Django.
    '''
    reference      = models.CharField(max_length=100, unique=True)   # order ID AESM
    payment_id     = models.CharField(max_length=200, blank=True)    # ID retourné par TokiPay
    inscription    = models.ForeignKey(
        'Inscription', on_delete=models.CASCADE,
        related_name='tokipay_paiements'
    )
    montant        = models.PositiveIntegerField(default=2000)
    statut         = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('valide',     'Validé'),
            ('echec',      'Échoué'),
        ],
        default='en_attente'
    )
    provider       = models.CharField(max_length=30, blank=True)     # mvola / orange_money
    sender_phone   = models.CharField(max_length=20, blank=True)
    cree_le        = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le  = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f'{self.reference} — {self.statut}'
 
    class Meta:
        verbose_name        = 'Paiement TokiPay'
        verbose_name_plural = 'Paiements TokiPay'
        
class Quitus(models.Model):
    paiement = models.OneToOneField(
        Paiement,
        on_delete= models.CASCADE
    )
    qr_code = models.ImageField(
        upload_to='quitus/'
    )
    fichier_pdf = models.FileField(
        upload_to='quitus/',
    )
    date_generation = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"Quitus {self.paiement.transaction_id}"

class Rapport(models.Model):
    
    titre = models.CharField(
        max_length=200,
    )
    description = models.TextField(
        blank=True, 
        
        null=True
    )
    date_creation = models.DateTimeField(
        auto_now_add=True
    )
    
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    def __str__(self):
        return self.titre
    @property
    def total_recettes(self):
        return sum(
            ligne.montant
            for ligne in self.lignes.filter(
                type='recette'
            )
        )
    @property
    def total_depenses(self):
        return sum(
            ligne.montant
            for ligne in self.lignes.filter(
                type='depense'
            )
        )
    @property
    def solde(self):
        return self.total_recettes - self.total_depenses
    
class CategorieBudget(models.Model):
    nom = models.CharField(
        max_length=100,
        unique=True
    )
    def __str__(self):
        return self.nom

class LigneBudget(models.Model):
    TYPE_CHOICES = [
        ('recette' , 'Recette'),
        ('depense' , 'Dépense')
    ]
    rapport = models.ForeignKey(
        Rapport,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=20
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    categorie = models.ForeignKey(
        CategorieBudget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date_operation = models.DateTimeField(
        auto_now_add=True
    )
    justificatif = models.FileField(
        upload_to='budget/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f"{self.type.capitalize()} - {self.montant} - {self.categorie.nom if self.categorie else 'Sans catégorie'}"
    
