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
    
    #Capabilities
    path('api/charger/<uuid:charger_id>/capabilities/', views.charger_capabilities, name='charger_capabilities'),
    
    #Cloud status
    path('api/charger/<uuid:charger_id>/cloudstatus/', views.charger_cloudstatus, name='charger_cloudstatus'),
    
    #Charge history #FIXME: I am able to get 200 but empty arrays perhaps because there is no data?
    path('api/charger/<uuid:charger_id>/charge-history/', views.charger_charge_history, name='charger_charge_history'),
    
    #OCPP-logs latest
    path('api/charger/<uuid:charger_id>/ocpp-logs/', views.charger_ocpp_logs_latest, name='charger_ocpp_logs_latest'),
]