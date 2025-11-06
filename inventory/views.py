from django.shortcuts import render

def index(request):
    context = {
        'site_title': 'Inventário',
    }
    return render(request, 'inventory/index.html', context)