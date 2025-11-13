from django.shortcuts import render


def landing_page(request):
    context = {
        'site_title': 'Sistema de Help Desk',
    }
    return render(request, 'landing/index.html', context)
