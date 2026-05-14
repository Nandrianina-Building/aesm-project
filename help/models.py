from django.db import models

class FAQ(models.Model):

    question = models.CharField(
        max_length=255
    )

    reponse = models.TextField()

    categorie = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.question