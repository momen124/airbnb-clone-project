from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import Booking, User

@shared_task
def send_booking_confirmation(booking_id):
    """
    Send a booking confirmation email to the user
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        send_mail(
            subject=f'Booking Confirmation - {booking.property.title}',
            message=f'''
            Dear {booking.user.first_name},
            
            Your booking for {booking.property.title} has been confirmed.
            
            Check-in: {booking.check_in}
            Check-out: {booking.check_out}
            Total Price: ${booking.total_price}
            
            Thank you for booking with us!
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
    except Booking.DoesNotExist:
        pass

@shared_task
def send_booking_reminder():
    """
    Send a reminder email to users with upcoming bookings (1 day before check-in)
    """
    tomorrow = datetime.now().date() + timedelta(days=1)
    bookings = Booking.objects.filter(check_in=tomorrow, status='confirmed')
    
    for booking in bookings:
        send_mail(
            subject=f'Reminder: Your stay at {booking.property.title} is tomorrow',
            message=f'''
            Dear {booking.user.first_name},
            
            This is a reminder that your stay at {booking.property.title} begins tomorrow.
            
            Check-in: {booking.check_in}
            Check-out: {booking.check_out}
            
            Safe travels!
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )

@shared_task
def update_booking_statuses():
    """
    Update booking statuses based on dates
    """
    today = datetime.now().date()
    
    # Mark bookings as completed if check-out date has passed
    Booking.objects.filter(
        check_out__lt=today,
        status='confirmed'
    ).update(status='completed')
