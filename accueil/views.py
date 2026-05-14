from django.shortcuts import render

def accueilView(request):
    
    return render(
        request,
        "accueil/home.html"
    )