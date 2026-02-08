# B2B Service Marketplace (Flask)

A production-ready Flask web application where businesses can:

- Register an account
- Create a business profile
- List services they offer
- Browse services from other companies
- Request/purchase services
- Manage orders, messages, and reviews (messages implemented, reviews stub-ready)
- Admin can delete users and services

---

## Features

- Flask + SQLAlchemy + Flask-Login + Flask-WTF
- User authentication (register, login, logout)
- Password hashing
- Business profiles
- Service listings
- Orders with statuses
- Order-based messaging (simple chat)
- Admin panel (delete users, services)
- CSRF protection
- Secure session settings
- Template inheritance
- Responsive HTML/CSS UI
- SQLite by default (easy to switch to PostgreSQL)
- Flask-Migrate for database migrations

---

## Project Structure

```text
service-marketplace/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── utils.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── service_list.html
│       ├── service_detail.html
│       ├── create_service.html
│       ├── messages.html
│       ├── orders.html
│       └── profile.html
├── venv/ (ignored)
├── run.py
├── requirements.txt
└── README.md