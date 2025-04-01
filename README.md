# Untitled

# Customer Support Ticketing System

## Overview

This repository contains a Django-based API designed for a customer support platform where agents handle support tickets. The system efficiently assigns unassigned tickets to agents, ensuring that each ticket is exclusively assigned to one agent. It supports high concurrency, allowing thousands of agents to fetch tickets simultaneously without blocking others.

## Features

**Admin Functionalities:**

- Create, update, and delete tickets.

**Agent Functionalities:**

- Retrieve and assign up to 15 tickets exclusively assigned to them.
- Fetch additional tickets if fewer than 15 are assigned, ensuring a maximum of 15 assigned tickets at any time.

## Technical Details

- **Backend Framework:** Django
- **API Framework:** Django REST Framework
- **Database:** MySQL
- **Concurrency Handling:** Utilizes row-level locking with `SELECT ... FOR UPDATE` to prevent race conditions and ensure non-blocking ticket assignment.
- **Scalability:** Optimized to handle thousands of concurrent agents fetching tickets simultaneously.
- **Security:** Agents can only access tickets assigned to them, while admins have permissions to manage all tickets.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL Database Server
- Docker (optional, for containerization)

### Installation Steps

1. **Clone the Repository:**
    
    ```bash
    git clone <https://github.com/yourusername/support-ticketing-system.git>
    cd support-ticketing-system
    
    ```
    
2. **Create and activate a virtual environment**
python3 -m venv env
source env/bin/activate # On Windows, use 'env\Scripts\activate'
3. **Install dependencies**
pip install -r requirements.txt
4. **Set up the database**

# Ensure MySQL is running and create a new database

mysql -u root -p
CREATE DATABASE tickets;
EXIT;

# Configure the database settings in tickets/settings.py if you changed the name

# Update the DATABASES setting with your MySQL credentials

4. **Setting Up Redis and Celery**

# To enable asynchronous task processing in your Django application, follow these steps to install and configure Redis and Celery:

**For Ubuntu:**

``bash
   sudo apt update
   sudo apt install redis-server``
``bash
    sudo apt install celery``
7.**run redis and celery workers and sql**
``sudo systemctl start mysql
  redis-server
``
###make sure to run the clery worker in a termial
``celery -A base worker --loglevel=info
``

8. **Apply migrations**
python manage.py makemigrations
python manage.py migrate

9. **Create a admin user.
python manage.py create_default_users
# Follow the prompts to set up the admin user

10. **Run the development server**
python manage.py runserver
# The API will be accessible at <http://127.0.0.1:8000/>

```
