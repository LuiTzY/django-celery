from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#Registramos el router para agrear vistas basadas en ViewSets
router = DefaultRouter()
router.register("user",UserViewSet, basename="user")

urlpatterns = [
    #incluimos las urls registradas en el router 
    path("",include(router.urls)),
    #vista que creara el usuario pero enviara el correo por medio de un shared task de celery
    path("user-celery/", UserCeleryApiView.as_view(), name="user-celery"),
    #vista que creara un usuario pero enviara el correo de manera sincronica directamente desde el codigo
    path("user-sync/", UserSyncApiView.as_view(), name="user-sync")
]