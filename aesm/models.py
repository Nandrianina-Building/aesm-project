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
        default='en_attente'
    )
    
    date_inscription = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"Inscription {self.etudiant}"
    
class Paiement(models.Model):
    STATUT_CHOICES = [
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
        max_length=20
    )
    transaction_id = models.CharField(
        max_length=100
    )
    
    def __str__(self):
        return f"Payement de {self.transaction_id}"
    

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
        max_length=200
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
    )
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.titre
    
class LigneBudget(models.Model):
    TYPE_CHOICES = [
        ('recette', 'Recette'),
        ('depense', 'Dépense'),
    ]

    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name='lignes')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.IntegerField()
    description = models.TextField()
    
    def __str__(self):
        return f"{self.type} - {self.montant}"