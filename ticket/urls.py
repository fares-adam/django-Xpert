from django.urls import path
from ticket.views import create_ticket , update_delete_ticket  , sell_ticket


urlpatterns = [
    # Admin API endpoints
    path('admin/tickets/', create_ticket, name='admin-ticket-create'),
    path('admin/tickets/<int:pk>/', update_delete_ticket, name='admin-ticket-update-delete'),
 
    
    # Agent endpoints
    path('agent/sell-ticket/', sell_ticket, name='agent-sell-ticket'),


]