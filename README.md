Airbnb Clone Project
Overview
The Airbnb Clone is a backend for managing user profiles, property listings, bookings, payments, and reviews, mimicking Airbnb's core features using Django, PostgreSQL, and Docker.
Team Roles

Backend Developer: Builds APIs and business logic.
Database Admin: Designs and optimizes PostgreSQL schema.
DevOps Engineer: Manages Docker and CI/CD pipelines.
QA Engineer: Tests functionality and APIs.

Technology Stack

Django/DRF: RESTful APIs.
PostgreSQL: Data storage.
GraphQL: Flexible queries.
Celery/Redis: Async tasks and caching.
Docker: Containerization.
GitHub Actions: CI/CD.

Database Design

User: email, is_host; has many Properties, Bookings.
Property: title, price_per_night; has many Bookings, Reviews.
Booking: check_in, total_price; belongs to User, Property.
Payment: amount, status; belongs to Booking.
Review: rating, comment; belongs to User, Property, Booking.

Feature Breakdown

User Management: Secure registration and profiles.
Property Management: Listing creation and search.
Booking System: Reservations with validation.
Payment Processing: Stripe transactions.
Review System: Post-stay feedback.

API Security

Authentication: Token-based access control.
Authorization: Role-based permissions.
CORS: Trusted origins only.
Rate Limiting: Prevents abuse.

CI/CD Pipeline
CI/CD with GitHub Actions and Docker automates testing and deployment, ensuring code quality and rapid delivery to cloud platforms like AWS ECS.
