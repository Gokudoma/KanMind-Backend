KanMind Backend

    A robust RESTful API for a Kanban board application, built with Django and Django REST Framework (DRF). This backend serves as the data layer for the KanMind frontend, managing users, boards, tasks, and comments.



🚀 Features

    User Authentication: Secure registration, login (Token-based), and email verification check.

    Board Management: Create, read, update, and delete Kanban boards.

    Task Management: Full CRUD operations for tasks with status (To-do, In-progress, Await-feedback, Done) and priority levels.

    Collaboration: Add members to boards and assign tasks to specific users.

    Comments: Nested comments on tasks for team communication.

    Permissions: Granular permission system (e.g., only board owners can delete boards; only members can view/edit tasks).



🛠️ Tech Stack

    Language: Python 3.10+

    Framework: Django 5.x

    API Toolkit: Django REST Framework (DRF)

    Authentication: DRF Token Authentication

    Database: SQLite (Development)

    Utilities: django-cors-headers, drf-nested-routers



⚙️ Installation & Setup

    Follow these steps to get the backend running locally:

1. Clone the repository

    git clone <YOUR_REPOSITORY_URL>
    cd KanMind-Backend


2. Create and activate a virtual environment

Windows:

    python -m venv venv
    .\venv\Scripts\Activate


Mac/Linux:

    python3 -m venv venv
    source venv/bin/activate


3. Install dependencies

    pip install -r requirements.txt


4. Apply database migrations

    python manage.py migrate


5. Create a Superuser (Admin)

    To access the Django Admin panel:

    python manage.py createsuperuser


6. Run the server

    python manage.py runserver


    The API will be available at http://127.0.0.1:8000/.



📡 API Endpoints

    The API provides the following main endpoints. All endpoints (except auth) require a valid token in the header (Authorization: Token <your_token>).

Authentication

    POST /api/registration/ - Register a new user

    POST /api/login/ - Login and retrieve auth token

    GET /api/email-check/ - Check if an email is already taken

Boards

    GET /api/boards/ - List all boards you are a member of

    POST /api/boards/ - Create a new board

    GET /api/boards/{id}/ - Retrieve board details (including nested tasks)

    PATCH /api/boards/{id}/ - Update board (e.g., title or members)

    DELETE /api/boards/{id}/ - Delete a board (Owner only)

Tasks

    GET /api/tasks/assigned-to-me/ - List tasks assigned to the current user

    POST /api/tasks/ - Create a new task

    PATCH /api/tasks/{id}/ - Update a task status, priority, etc.

    DELETE /api/tasks/{id}/ - Delete a task

Comments

    GET /api/tasks/{task_id}/comments/ - List comments for a task

    POST /api/tasks/{task_id}/comments/ - Add a comment to a task



📄 License

    This project is developed as part of the Developer Akademie educational curriculum. It is intended for non-commercial, educational purposes only.

    "Developed as part of the Developer Akademie GmbH advanced training program."