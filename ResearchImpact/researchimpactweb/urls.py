from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^changesYears$', views.changesYears, name='changesYears'),
    url(r'^changesWeigths$', views.changesWeigths, name='changesWeigths'),
    url(r'^scopusCredentials$', views.scopusCredentials, name='scopusCredentials'),
    url(r'^instalarDependencias$', views.instalarDependencias, name='instalarDependencias'),
    url(r'^registerAuthors$', views.registerAuthors, name='registerAuthors'),
    url(r'^prueba$', views.executeScrapper, name='executeScrapper'),
    
]
