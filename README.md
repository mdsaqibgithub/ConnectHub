# ConnectHub

ConnectHub is a social networking application built using Django Rest Framework. It allows users to register, log in, search for other users, send friend requests, and manage their friend lists.

## Features

- User Registration: Sign up using an email address (no OTP verification required).
- User Login: Authenticate using email and password (case insensitive).
- User Search: Search other users by email or name, with pagination (up to 10 records per page).
- Friend Requests: Send, accept, and reject friend requests.
- Friend List: View a list of accepted friends.
- Pending Friend Requests: View a list of received friend requests.
- Throttling: Limit sending friend requests to 3 requests per minute.

## API Documentation

You can test the API endpoints using the Postman collection provided below:

[Postman Collection Link](<https://documenter.getpostman.com/view/30524059/2sAXqv3fYw>)


## Requirements

- Python 3.x
- Django 5.1.1
- Django REST Framework 3.15.2
- Django CORS Headers 4.4.0
- djangorestframework-simplejwt 5.3.1
- PyJWT 2.9.0

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ConnectHub.git
   cd ConnectHub
2. Create a virtual environment:
    python -m venv env
   
4. Activate the virtual environment:
    .\env\Scripts\activate
   
5. Install the required packages:
    pip install -r requirements.txt

6. Apply migrations:
    python manage.py migrate

7. Run the server:
    python manage.py runserver


