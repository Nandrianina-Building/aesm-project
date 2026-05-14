from django.shortcuts import render
from .models import FAQ


# =====================
# PAGE STATIQUE
# =====================
def instructions_faq(request):
    faqs = FAQ.objects.all()
    return render(
        request,
        'help/dashboard_help.html',
        {
            'faqs': faqs
        }
    )

