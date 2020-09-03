from django.shortcuts import render
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
import requests
from django.conf import settings
from django.http import HttpResponse, Http404
from .forms import *
# Create your views here.

@csrf_exempt
def changesYears( request ) :
    if request.method == "GET":
        form = AniosForm()
        return render(request, 'researchimpactweb/cambioAnios.html', {'form': form})
    else:
        publicacionesInicio = request.POST.get("aniosPublicacionesInicio")
        publicacionesFin = request.POST.get("aniosPublicacionesFin")
        citacionesInicio = request.POST.get("aniosCitacionesInicio")
        citacionesFin = request.POST.get("aniosPCitacionesFin")
        with open('config/config.json', 'r') as file:
            config = json.load(file)
            config["rangos"]["publicados"]["desde"] = publicacionesInicio
            config["rangos"]["publicados"]["hasta"] = publicacionesFin
            config["rangos"]["citaciones"]["desde"] = citacionesInicio
            config["rangos"]["citaciones"]["hasta"] = citacionesFin
        with open('config/config.json', 'w') as file:
            json.dump(config, file, indent=4)
        return HttpResponse(json.dumps({ "response": "exitoso"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")


@csrf_exempt
def changesWeigths( request ) :
    if request.method == "GET":
        form = PesosForm()
        return render(request, 'researchimpactweb/cambioPesos.html', {'form': form})
    else:
        pesoPublicaciones = request.POST.get("pesoPublicaciones")
        pesoCitaciones = request.POST.get("pesoCitaciones")
        if pesoPublicaciones + pesoCitaciones != 1:
            return HttpResponse(json.dumps({ "response": "error!", "mensage": "los pesos no pueden sumar mas de 1"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")
        with open('config/config.json', 'r') as file:
            config = json.load(file)
            config["pesos"]["publicados"]["porcentaje"] = pesoPublicaciones
            config["pesos"]["citaciones"]["porcentaje"] = pesoCitaciones
        with open('config/config.json', 'w') as file:
            json.dump(config, file, indent=4)
        return HttpResponse(json.dumps({ "response": "exitoso"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")

@csrf_exempt
def scopusCredentials (request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'researchimpactweb/credenciales.html', {'form': form})
    else:
        
        email = request.POST.get("usuario")
        password = request.POST.get("password")
        print(email,password)
        input()
        if email == None or password == None:
            return HttpResponse(json.dumps({ "response": "bad requeste", "menssage": "Debe enviar correo y contraseña"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")
        try:
            file = open("scripts/correoScopus.txt", "w")
            file.write(email+"\n"+password)
            return HttpResponse(json.dumps({ "response": "exitoso"} , ensure_ascii=False).encode("utf-8"),
                                content_type="application/json")
        except:
            return HttpResponse(json.dumps({ "response": "error"} , ensure_ascii=False).encode("utf-8"),
                                content_type="application/json")


@csrf_exempt
def instalarDependencias(request):
    a = subprocess.call("pip3 install selenium & pip3 install openpyxl & pip3 install pandas & pip3 install xlrd & sudo apt-get install python3-tk", shell=True)
    if a != 0:
        return HttpResponse(json.dumps({ "response": "error"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")
    return HttpResponse(json.dumps({ "response": "exitoso"} , ensure_ascii=False).encode("utf-8"),
                        content_type="application/json")

@csrf_exempt
def registerAuthors(request):
    a = subprocess.call("python3 scripts/author_register.py ", shell=True)
    if a != 0:
        return HttpResponse(json.dumps({ "response": "error"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")
    return HttpResponse(json.dumps({ "response": "exitoso"} , ensure_ascii=False).encode("utf-8"),
                        content_type="application/json")


@csrf_exempt
def executeScrapper(request):
    a = subprocess.call('python3  ', shell=True)
    if a != 0:
        return HttpResponse(json.dumps({ "response": "error"} , ensure_ascii=False).encode("utf-8"),
                            content_type="application/json")
    return HttpResponse(json.dumps({ "response": "exitoso"} , ensure_ascii=False).encode("utf-8"),
                        content_type="application/json")
        
def mostrar_indice(request):
    return render(request, 'researchimpactweb/index.html')


def datasetInvestigadores(request):
    response = requests.get('http://192.168.253.6:8080/api/Investigacion/GetCargaAcademica/2020')
    respuesta = json.loads(response.text)
    archivo = open("NuevosInvestigadores.csv", "w")
    claves = ','.join(list(respuesta[0].keys()))
    archivo.write(claves+'\n')
    for element in respuesta:
        linea = str(element.get('identificacion')) + ','
        linea += str(element.get('docente'))+ ','
        linea += str(element.get('idactividad'))+ ','
        linea += str(element.get('actividad'))+ ','
        linea += str(element.get('descripcion'))+ ','
        linea += str(element.get('idtipoactividad'))+ ','
        linea += str(element.get('idunidadcargo'))+ ','
        linea += element.get('unidadcargo')+ ','
        linea += element.get('unidadplanifica')+ ','
        linea += element.get('txdescripcion').replace('\r',' ').replace('\n', ' ').replace(',',' ')+ ','
        linea += str(element.get('tipohora'))+ ','
        linea += str(element.get('horatotal'))+ ','
        linea += element.get('nivelestudio')+ ','
        linea += str(element.get('tipocalcula'))+ ','
        linea += str(element.get('anio'))+ ','
        linea += str(element.get('termino1'))+ ','
        linea += str(element.get('termino2'))+ ','
        linea += str(element.get('termino3'))+ ','
        archivo.write(linea+'\n')
    archivo.close()
    path = "NuevosInvestigadores.csv"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-Excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
    


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-Excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


