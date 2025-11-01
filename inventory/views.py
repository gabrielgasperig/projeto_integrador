from django.shortcuts import render, redirect
from .models import Hardware, Software, Subscription
from .forms import HardwareForm, SoftwareForm, SubscriptionForm

def index(request):
    hardwares = Hardware.objects.all()
    softwares = Software.objects.all()
    subscriptions = Subscription.objects.all()

    context = {
        'hardwares': hardwares,
        'softwares': softwares,
        'subscriptions': subscriptions,
        'site_title':'Inventário de Ativos',
    }
    return render(request, 'inventory/index.html', context)

def create_asset(request, asset_type):
    if asset_type == 'hardware':
        form_class = HardwareForm
        template_name = 'inventory/create_asset.html'
    elif asset_type == 'software':
        form_class = SoftwareForm
        template_name = 'inventory/create_asset.html'
    elif asset_type == 'subscription':
        form_class = SubscriptionForm
        template_name = 'inventory/create_asset.html'
    else:
        return redirect('inventory:index')

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:index')
    else:
        form = form_class()

    context = {
        'form': form,
        'asset_type': asset_type,
    }
    return render(request, template_name, context)