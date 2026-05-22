from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    SECTION_CHOICES = [
        ('AESM', 'AESM'),
        ('CR', 'Centre de Réflexion'),
    ]
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
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
    count_view = models.PositiveIntegerField(default=0)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='images/',blank=True,null=True)
    categorie = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    date_publication = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    like = models.ManyToManyField(User, related_name='likes', blank=True)
    
    def __str__(self):
        return self.titre
    
class Comment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='comments')
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contenu = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f'Commentaire de {self.auteur or "Anonyme"} sur {self.publication}'

class FileCategory(models.Model):
    nom = models.CharField(
        max_length=100,
        unique=True
    )
    SECTION_CHOICES = [
        ('AESM', 'AESM'),
        ('CR', 'Centre de Réflexion'),
    ]
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    def __str__(self):
         return self.nom
     
class Files(models.Model):
    SECTION_CHOICES = [
        ('AESM', 'AESM'),
        ('CR', 'Centre de Réflexion'),
    ]
    ACCESS_CHOICE = [
        ('public' , 'Publilque'),
        ('membre', 'Membre uniquement'),
        ('admin' , 'Admin')
    ]
    nom_fichier = models.CharField(max_length=100)
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    contenu = models.CharField(max_length=100,null=True , blank=True)
    fichier = models.FileField(upload_to='fichiers/')
    date_upload = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    categorie = models.ForeignKey(FileCategory,on_delete=models.SET_NULL,null=True , blank=True)
    access = models.CharField(choices=ACCESS_CHOICE , default='public',max_length=20)
    download_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.nom_fichier
