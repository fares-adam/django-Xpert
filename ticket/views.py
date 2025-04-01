
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ticket.models import Ticket
from user.models import Customer, User
from .serializers import  TicketSerializer
from user.permissions import IsAdmin, IsAgent
from django.db import transaction


@api_view(['POST'])
@permission_classes([IsAdmin])
def create_ticket(request):
    serializer = TicketSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdmin])
def update_delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'PUT':
        serializer = TicketSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    

@api_view(['POST'])
@permission_classes([IsAgent])
def sell_ticket(request):
    agent = request.user.pk
    ticket_id = request.data.get('ticket_id')
    customer_id = request.data.get('customer_id')
    
    try:
        with transaction.atomic():
            ticket = Ticket.objects.get(id=ticket_id, assigned_to=agent, status='assigned')
            customer = Customer.objects.get(id=customer_id)
            
            ticket.status = 'sold'
            ticket.sold_to = customer
            # ticket.assigned_to = None
            ticket.save()
            
            return Response({'status': 'Ticket sold successfully'}, status=status.HTTP_200_OK)
    
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)