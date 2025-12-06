from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .import views 

urlpatterns = [
    path('', RedirectView.as_view(url='accounts/login/', permanent=False), name='root'),
    path('admin/', admin.site.urls),
    
    path('accounts/', include('accounts_app.urls')),
    
    # --- Testable proxy endpoint --
    path('api/charger-lookup/<str:serial>/', views.charger_lookup_by_serial, name='charger_lookup_by_serial'),
    
    #Charger by chargerID
    path('api/charger-lookup/id/<str:charger_id>/', views.charger_by_id, name='charger_by_id'),
]