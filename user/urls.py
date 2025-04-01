from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.views import (
    create_customer,
    create_user,
    fetch_tickets, manage_user, 
)


urlpatterns = [
    path('admin/users/', create_user, name='admin-user-create'),
    path('admin/users/<int:pk>/', manage_user, name='admin-user-manage'),
    path('admin/customer/create/', create_customer, name='admin-create-customer'),
    path('agent/fetch-tickets/', fetch_tickets, name='agent-fetch-tickets'),
    
    

]