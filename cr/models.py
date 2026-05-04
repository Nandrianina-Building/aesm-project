from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Publication(models.Model):
    SECTION_CHOICES = [
        ('AESM', 'AESM'),
        ('CR', 'Centre de Réflexion'),
    ]

    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
    ]

    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    
    categorie = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    date_publication = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)

    def __str__(self):
        return self.titre