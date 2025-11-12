# Landing App - Gesticket

Este é o app da landing page do Gesticket, criado para apresentar o sistema de gestão de tickets.

## Estrutura

```
landing/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
├── static/
│   └── landing/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── images/
└── templates/
    └── landing/
        └── index.html
```

## Funcionalidades

- **Hero Section**: Apresentação principal com título, subtítulo e CTAs
- **Features Section**: Grade com 6 recursos principais do Gesticket
- **About Section**: Informações sobre o sistema e seus benefícios
- **CTA Section**: Chamada para ação para criar conta
- **Contact Section**: Informações de contato
- **Footer**: Links rápidos e informações legais
- **Responsive Design**: Totalmente responsivo para mobile e desktop
- **Animações**: Efeitos de scroll e hover para melhor UX

## Rotas

- `/` - Landing page principal

## Configuração

1. O app já está configurado em `INSTALLED_APPS` no `settings.py`
2. As URLs estão mapeadas no `urls.py` principal
3. Os templates usam `{% load static %}` para carregar arquivos estáticos

## Design

- **Paleta de cores**:
  - Primary: #6366f1 (Indigo)
  - Secondary: #10b981 (Green)
  - Background: #f9fafb (Light Gray)
  
- **Fontes**: Poppins (Google Fonts)

- **Componentes**:
  - Navbar fixa no topo
  - Menu hamburguer para mobile
  - Cards de features com hover effects
  - Smooth scroll para navegação interna
  - Animações on-scroll

## Integração

A landing page possui links para:
- Login: `{% url 'account:login' %}`
- Registro: `{% url 'account:register' %}`

Certifique-se de que essas rotas estão configuradas no app `account`.
