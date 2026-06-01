from django.urls import path, include, reverse_lazy
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

urlpatterns = [

    # Root → login
    path(
        '',
        RedirectView.as_view(url=reverse_lazy('template_login')),
        name='root'
    ),

    # Accounts URLs
    path('', include('accounts.urls')),

    # Dashboard
    path(
        'dashboard/',
        TemplateView.as_view(template_name='dashboard/index.html'),
        name='dashboard'
    ),

    # App modules
    path('pos/', include('sales.urls')),
    path('products/', include('products.urls')),
    path('reports/', include('reports.urls')),
    path('subscriptions/', include('subscriptions.urls')),

    # API
    path('api/auth/', include('accounts.api.urls')),
    path('api/sales/', include('sales.api_urls')),

    # Admin
    path('admin/', admin.site.urls),
]