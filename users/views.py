
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
import core.settings
import asyncio
from django.core.mail import send_mail
from dotenv import load_dotenv
import time
from .tasks import send_email_task
load_dotenv()
 
class UserViewSet(ModelViewSet):
    
    serializer_class = UserSerializer    
    queryset = User.objects.all()

    #metodo asincrono para enviar un correo con asyncio
    async def send_email_async(self, subject, message):
        
        email_from = core.settings.EMAIL_HOST_USER
        recipient_list = [core.settings.EMAIL_HOST_USER]
        
        # Ejecuta el envío de correo de manera asincrónica alojando el mismo un hilo a parte del proceso inicial que corre django
        loop = asyncio.get_event_loop()
        
        #ejecuta la tarea de enviar el correo
        await loop.run_in_executor( None, send_mail,subject,message,email_from,recipient_list)
        
        

    #funcion que handlea la creacion de un nuevo usuario
    def create(self, request, *args, **kwargs):
        
        # se obtiene el serializador para instanciar la data que no esta llegando para crear el usuario
        serializer = self.get_serializer(data=request.data)
        #Se ejecuta la validacion del serializador y lanzamos cualquier excepcion que ocurra
        serializer.is_valid(raise_exception=True)

        # al ser valido llegara aqui por lo que se guarda el usuario creado 
        self.perform_create(serializer)

        # Enviar un correo despues de que creamos el usuario
        subject = 'Correo desde python utilizando asyncio'
        message = f'Se ha creado un nuevo Usuario dentro del sistema de prueba'
        
        start_time_sync = time.time()
        
        #enviamos el correo de manera sincronica
        send_mail(subject,message,core.settings.EMAIL_HOST_USER, [core.settings.EMAIL_HOST_USER])
        
        end_time_sync = time.time()
        
        final_time_sync = end_time_sync- start_time_sync
        
        print(f"Se demoro en enviar el correo de manera sincronica {final_time_sync} \n")
        

        start_time_asyncio = time.time()

        #Enviamos el email con los datos que obtuvimos y los parametros necesarios en un hilo a parte del inicial 
        asyncio.run(self.send_email_async(subject, message,))
        
        end_time_asyncio = time.time()
        
        execution_time = end_time_asyncio - start_time_asyncio

        print(f"Se demoro en enviar el correo utilizando asyncio {execution_time} \n")
        
        start_time_rabbit =  time.time()
        
        #se ejecuta la funcion que celery alojara en la cola de Celery y se recibira en el broker
        send_email_task.delay(message)
        
        end_time_rabbit = time.time()
        
        final_time_rabbit = end_time_rabbit - start_time_rabbit
        
        print(f"Se demoro en enviar el correo de manera asincronica con rabbitMQ la tarea ha durado {final_time_rabbit} \n")
        # Devolver la respuesta de éxito
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # Sobreescribir para personalizar el guardado del objeto
        serializer.save()



class UserSyncApiView(APIView):
    
    def post (self,request,format=None):
                    
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            
            serializer.save()
            send_mail("System Register User","Usuario creado de manera sincronica con django",core.settings.EMAIL_HOST_USER,[core.settings.EMAIL_HOST_USER])
            return Response({"Response":"User created succesfully"},status=status.HTTP_201_CREATED)
        
        return Response({"error":serializer.errors})
    
class UserCeleryApiView(APIView):
    def post (self,request,format=None):
                    
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            send_email_task.delay("Usuario registrado via Celery trabajando con rabbitMQ como worker")
            return Response({"Response":"User created succesfully"},status=status.HTTP_201_CREATED)
        
        return Response({"error":serializer.errors})