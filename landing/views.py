from django.shortcuts import render


def landing_page(request):
    """
    View para a landing page do Gesticket
    """
    return render(request, 'landing/index.html')
