from django.shortcuts import render
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import subprocess
# Create your views here.

@csrf_exempt
def changesYears( request ) :
    data = json.loads(request.body)
    publicacionesInicio = data.get("publicaciones").get("inicio")
    publicacionesFin = data.get("publicaciones").get("fin")
    citacionesInicio = data.get("citaciones").get("inicio")
    citacionesFin = data.get("citaciones").get("fin")
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
    data = json.loads(request.body)
    pesoPublicaciones = data.get("peso publicaciones")
    pesoCitaciones = data.get("peso citaciones")
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
    data = json.loads(request.body)
    email = data.get("email")
    password = data.get("password")
    print(email,password)
    if email == None or password == None:
        return HttpResponse(json.dumps({ "response": "bad requeste", "menssage": "Debe enviar correo y contraseña"} , ensure_ascii=False).encode("utf-8"),
                        content_type="application/json")
    try:
        file = open("PY's/correoScopus.txt", "w")
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
        
