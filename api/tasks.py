from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_confirmation_email(order_id, user_email):
    subject = f"Order Confirmation - {order_id}"
    message = f"Thank you for your order {order_id}. We are processing it and will notify you once it's shipped."
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])