# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

#Creamos una instancia de nuestro proyecto en celery
app = Celery('core')

# leera la configuracion de django 
app.config_from_object('django.conf:settings', namespace='CELERY')

#automaticamente va a buscar en las apps creadas archivos .tasks para las tareas de celery
app.autodiscover_tasks()
