from django.db import models
from django.contrib.auth.models import User

class Etudiant(models.Model):
    user = models.OneToOneField(
        User , 
        on_delete=models.CASCADE
    )
    
    matricule = models.CharField(
        max_length=90,
        unique = True
    )
    
    def __str__(self):
        return self.user.username