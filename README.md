## KanMind – Backend API

KanMind is a lightweight Kanban backend built with Django and Django REST Framework.  
It provides user authentication, board management, tasks, and comments through a clean REST API.



## Features

- User registration & login (Token Authentication)
- Create and manage boards
- Create, update, and delete tasks
- Assign users and reviewers
- Add and remove comments
- CORS enabled for frontend integration



## Tech Stack

- Python 3.13
- Django 6
- Django REST Framework
- SQLite (development)



## Installation

```bash
git clone https://github.com/El7as/kanmind.git
cd kanmind/Backend
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver



## API Base URL

/api/



## Auth Endpoints

POST /api/register/
POST /api/login/



## Board Endpoints

GET  /api/boards/
POST /api/boards/
GET  /api/boards/<id>/
PATCH /api/boards/<id>/
DELETE /api/boards/<id>/



## Task Endpoints

GET /api/tasks-assigned-to-me/
GET /api/tasks-reviewing/



## Comment Endpoints

GET    /api/tasks/<id>/comments/
POST   /api/tasks/<id>/comments/
DELETE /api/comments/<id>/




