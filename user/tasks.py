from celery import shared_task
from django.db import transaction, connections
from django.contrib.auth import get_user_model
from ticket.models import Ticket
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def assign_tickets_to_agent(self, agent_id, test_db=None):
    if test_db:
        connections.close_all()
    
    try:
        User = get_user_model()
        agent = User.objects.get(id=agent_id)

        with transaction.atomic():
            # fetch assigned tickets inside transaction to prevent race conditions
            assigned_count = Ticket.objects.filter(assigned_to=agent, status='assigned').select_for_update(skip_locked=True).count()
            needed_tickets = max(15 - assigned_count, 0)

            if needed_tickets > 0:
                new_tickets = Ticket.objects.filter(
                    status__isnull=True  # this will fetch tickets where the status is null (unassigned)
                ).select_for_update(skip_locked=True)[:needed_tickets]
                
                for ticket in new_tickets:
                    ticket.status = 'assigned'
                    ticket.assigned_to = agent
                    ticket.save()

            # fetch the updated list of assigned tickets
            assigned = list(Ticket.objects.filter(assigned_to=agent, status='assigned').values('id', 'title', 'description', 'created_at'))
            return assigned

    except User.DoesNotExist:
        if test_db:
            connections.close_all()
            return assign_tickets_to_agent(self, agent_id, test_db)
        raise
    except Exception as exc:
        logger.error(f"Error assigning tickets to agent {agent_id}: {exc}")
        self.retry(exc=exc, countdown=2)
