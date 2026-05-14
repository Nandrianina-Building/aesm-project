from django import forms
from django.db import IntegrityError
from django.shortcuts import render
from allauth.account.forms import SignupForm
from allauth.core.exceptions import ImmediateHttpResponse
from aesm.models import Inscription
from .models import Etudiant

class CustomSignUpForm(SignupForm):
    
    
    first_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(
            attrs={
                'class' : 'form-control',
                'placeholder' : 'eg : RAKOTOARISOA',
                'type' : 'text'
            }
        )
    )
    
    last_name = forms.CharField(
        max_length=100,required=True,
        widget=forms.TextInput(
            attrs = {
                'class' : 'form-control',
                'placeholder' : 'eg : Nandrianina',
                'type' : 'text'
            }
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class' : 'form-control',
                'placeholder' : 'eg : xxxxxx.com',
                'type' : 'email'
            }
        )
    )
    
    password1 = forms.CharField(
        required=True,
        help_text=None,
        widget=forms.PasswordInput(
            attrs={
                'class' : 'form-control'
            }
        )
    )
    password2 = forms.CharField(
        required=True,
        help_text=None,
        widget=forms.PasswordInput(
            attrs={
                'class' : 'form-control'
            }
        )
    )
    
    matricule = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class' : 'form-control',
                'placeholder' : 'eg : 123445'
            }
        )
    )
    
    def clean_matricule(self):
        matricule = self.cleaned_data.get('matricule')
        if Etudiant.objects.filter(matricule=matricule).exists():
            raise forms.ValidationError('Ce matricule est déjà utilisé.')
        return matricule
    
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        try:
            Etudiant.objects.create(
                user=user,
                matricule=self.cleaned_data['matricule']
            )
        except IntegrityError:
            user.delete()
            self.add_error('matricule', 'Ce matricule est déjà utilisé.')
            raise ImmediateHttpResponse(
                render(request, 'account/signup.html', {'form': self})
            )
        
        etudiant = Etudiant.objects.get(
            user=user
        )
        Inscription.objects.create(
            etudiant=etudiant,
            statut='en_attente'
        )
        return user