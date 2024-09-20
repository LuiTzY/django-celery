from celery import shared_task
from core import settings
from django.core.mail import send_mail
import core

#Tarea de celery que se ejecutara en segundo plano luego de que rabbitMQ la reciba
@shared_task
def send_email_task( message):
    #Lista de recipientes a la que llegara el correo
    recipient_list = [core.settings.EMAIL_HOST_USER]
    #subject del correo
    subject = "Correo desde celery utilizando el broker de RabbitMQ"
    #desde donde se enviara el correo
    email_from = settings.EMAIL_HOST_USER
    #funcion de django que nos permite enviar el correo
    send_mail(subject, message, email_from, recipient_list)