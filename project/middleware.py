from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages


class AdminAccessMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    messages.error(
                        request, 
                        'Acesso negado. Apenas o administrador pode acessar o painel de controle.'
                    )
                    return redirect('ticket:index')
        
        response = self.get_response(request)
        return response
