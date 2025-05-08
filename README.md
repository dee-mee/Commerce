# E-Commerce Website

A modern, responsive e-commerce platform built with Django and Bootstrap, featuring a sleek design similar to Amazon.

## Features

- User authentication and profile management
- Product catalog with categories, brands, and variants
- Shopping cart and wishlist functionality
- Secure checkout and payment processing
- Order tracking and history
- Vendor management for multi-vendor marketplace
- Admin dashboard for site management
- Responsive design for all devices
- Search and filtering capabilities
- Reviews and ratings system

## Technology Stack

- Django 5.2+
- Bootstrap 5
- PostgreSQL (recommended for production)
- Pillow for image processing
- Django Crispy Forms for form styling
- Django Allauth for authentication
- Stripe for payment processing

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

## Project Structure

- `core`: Base templates and static files
- `accounts`: User authentication and profiles
- `store`: Products, categories, and brands
- `cart`: Shopping cart functionality
- `orders`: Order processing and tracking
- `payment`: Payment processing
- `dashboard`: Admin and vendor dashboards
