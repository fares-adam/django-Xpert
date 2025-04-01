from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User 
from .serializers import  UserSerializer , CustomerSerializer
from .permissions import IsAdmin, IsAgent
from .tasks import assign_tickets_to_agent


    

@api_view(['POST'])
@permission_classes([IsAdmin])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdmin])
def create_customer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        customer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdmin])
def manage_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAgent])
def fetch_tickets(request):
    agent = request.user
    # call the celery task and wait for its result
    task = assign_tickets_to_agent.apply_async(args=[agent.id])  
    assigned_tickets = task.get(timeout=10)  # blocks execution until celery is done

    if isinstance(assigned_tickets, list):  # make sure it's valid serialized data
        return Response(assigned_tickets, status=200)
    else:
        return Response({"error": "Invalid data returned"}, status=500)