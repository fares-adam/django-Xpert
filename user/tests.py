from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from django.test import TransactionTestCase
from django.db import transaction
from rest_framework import status
from user.models import Customer
from ticket.models import Ticket
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor
from rest_framework.test import APIClient
from user.tasks import assign_tickets_to_agent

User = get_user_model()

class SupportSystemTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPOGATES = True

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', role='admin')
        self.agent_user = User.objects.create_user(username='agent', password='agentpass', role='agent')
        self.agent_user2 = User.objects.create_user(username='agent2', password='agentpass', role='agent')

        # auth users using API login to get real tokens
        self.admin_token = self.get_token('admin', 'adminpass')
        self.agent_token = self.get_token('agent', 'agentpass')
        self.agent2_token = self.get_token('agent2', 'agentpass')
        
    def get_token(self, username, password):
        response = self.client.post('/api/auth/token/', {'username': username, 'password': password})
        if response.status_code == 200 and 'access' in response.data:
            return response.data['access']
        print(f"Failed to get token for {username}: {response.data}")
        return None
    
    def authenticate(self, token):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        else:
            print("Failed to obtain token!")
    
    def test_admin_create_ticket(self):
        self.authenticate(self.admin_token)
        url = '/api/admin/tickets/'
        data = {'title': 'Issue A', 'description': 'Fix bug A'}
        response = self.client.post(url, data)
        print("Response Status Code:", response.status_code)  # debug output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
    
    def test_agent_fetch_tickets(self):
        """Test if an agent can fetch tickets correctly."""
        
        # auth agent
        print("Agent Token:", self.agent_token)  # debug
        self.authenticate(self.agent_token)
        assert self.agent_token is not None, "Failed to obtain agent token!"

        # create tickets
        Ticket.objects.bulk_create([Ticket(title=f'Ticket {i}', description='Some issue') for i in range(20)])
        print("Total Tickets in DB:", Ticket.objects.count())  # debug

        # fetch etch tickets
        url = '/api/agent/fetch-tickets/'
        response = self.client.get(url)

        # debug output
        print("Response Status:", response.status_code)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # make sure response contains 15 tickets (modify if necessary)
        response_data = response.json()
        if isinstance(response_data, dict) and "data" in response_data:
            response_data = response_data["data"]

        print("Fetched Ticket Count:", len(response_data))  # debug
        self.assertEqual(len(response_data), 15)

    
    def test_agent_cannot_fetch_more_than_15_tickets(self):
        self.authenticate(self.agent_token)
        Ticket.objects.bulk_create([Ticket(title=f'Ticket {i}', description='Some issue', assigned_to=self.agent_user) for i in range(15)])
        
        url = '/api/agent/fetch-tickets/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 15)
    
    def test_agent_selling_ticket(self):
        self.authenticate(self.admin_token)
        customer = Customer.objects.create(name='Customer B', email='customerB@example.com')
        ticket = Ticket.objects.create(title='Ticket X', description='Sellable')
        
        self.authenticate(self.agent_token)
        fetch_url = '/api/agent/fetch-tickets/'
        fetch_response = self.client.get(fetch_url)
        self.authenticate(self.agent_token)
        url = '/api/agent/sell-ticket/'
        data = {'ticket_id': ticket.id, 'customer_id': customer.id}
        response = self.client.post(url, data)
        
        print("Sell Ticket Response Status:", response.status_code)  # debug
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertIsNotNone(ticket.assigned_to)

    
    def test_authentication(self):
        url = '/api/auth/token/'
        data = {'username': 'agent', 'password': 'agentpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        refresh_url = '/api/auth/token/refresh/'
        refresh_data = {'refresh': response.data['refresh']}
        refresh_response = self.client.post(refresh_url, refresh_data)
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
    


class TicketAssignmentRaceConditionTest(TransactionTestCase):
    def setUp(self):
        #make sure we're using the test database
        self._pre_setup()
        
        # create test agents and tickets
        User = get_user_model()
        with transaction.atomic():
            self.agent1 = User.objects.create_user(
                username="agent1",
                password="test123",
                role= "agent"
            )
            self.agent2 = User.objects.create_user(
                username="agent2",
                password="test123",
                role= "agent"
            )
            
            Ticket.objects.bulk_create([
                Ticket(
                    title=f"Ticket {i}",
                    description=f"Description {i}",
                    status="unassigned"
                ) for i in range(30)
            ])
        
        # commit test data
        transaction.commit()
        
    def trigger_task(self, agent):
        """Wrapper that ensures test DB visibility"""
        from django.db import connections
        connections.close_all()
        
        try:
            result = assign_tickets_to_agent.apply_async(
                args=[agent.id],
                kwargs={'test_db': True}  # Pass test DB flag
            )
            return result.get(timeout=10)
        except Exception as e:
            print(f"Task failed for {agent.username}: {str(e)}")
            return []

    def test_race_condition(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.trigger_task, self.agent1),
                executor.submit(self.trigger_task, self.agent2)
            ]
            results = [f.result() for f in futures]
        
        # verification logic
        assigned = [t['id'] for r in results for t in r]
        self.assertEqual(len(set(assigned)), len(assigned))
        self.assertEqual(len(assigned), 30)