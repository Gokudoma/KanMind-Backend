# KanMind Backend

This is the RESTful API backend for the KanMind Kanban application. It provides authentication, board management, task tracking, and commenting features.

> **Note:** This repository contains only the backend code.
> **Important:** Do NOT commit the `db.sqlite3` file or `.env` files to GitHub.

## Technologies
* **Python 3.10+**
* **Django 5.x**
* **Django REST Framework (DRF)**
* **SQLite** (Development Database)

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <REPOSITORY_URL>
    cd KanMind-Backend
    ```

2.  **Create and activate virtual environment:**
    * Windows: `python -m venv venv` then `.\venv\Scripts\activate`
    * Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create Admin User:**
    To access the Django Admin Panel at `/admin/`, create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run Server:**
    ```bash
    python manage.py runserver
    ```
    The API is now accessible at `http://127.0.0.1:8000/api/`.

## Features
* **Authentication:** Token-based login, registration, and email checks.
* **Boards:** Create and manage kanban boards with multiple members.
* **Tasks:** Full CRUD for tasks including status, priority, and assignment.
* **Comments:** Discussion threads per task.
* **Permissions:** Granular access control (e.g., only owners can delete boards).

## Project Structure
The project follows a strict modular structure:
* **`core/`**: Main settings and routing.
* **`user_auth_app/`**: Handles user logic.
    * `api/`: Contains Serializers, Views, and URLs.
* **`kanban_board_app/`**: Handles boards, tasks, and comments.
    * `api/`: Contains Serializers, Views, Permissions, and URLs.

## API Documentation
The API is resource-oriented. Examples:
* `GET /api/boards/` - List boards
* `POST /api/login/` - Authenticate user