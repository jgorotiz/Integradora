import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
#!/usr/bin/python
import numpy as np
import tkinter as tk
from tkinter import filedialog
import sys
import json
from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_contact(file_content,key):
	name = file_content['contactos'][key]['nombre']
	email = file_content['contactos'][key]['mail']
	return [name, email]

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def admin_data(filename):
	file = open(filename,"r")
	correo = file.readline().strip()
	password = file.readline().strip()
	file.close()
	return [correo, password]
	
def enviar_correo():
	with open('../Config/config.json') as json_data_file:
		data = json.load(json_data_file)

	sendFrom = admin_data('CorreoDecanato.txt')
	sendTo = get_contact(data,"receptor")

	# set up the SMTP server
	s = smtplib.SMTP('smtp.office365.com:587')
	s.ehlo()
	s.starttls()
	s.login(sendFrom[0], sendFrom[1])

	message_template = read_template('template2.txt')
	msg = MIMEMultipart()

	# setup the parameters of the message
	msg['From']=sendFrom[0]
	msg['To']=sendTo[1]
	msg['Subject']="Ingreso investigadores"
	message = message_template.substitute(NOMBRE_PROCESO="Ingreso de investigadores")

	# add in the message body
	msg.attach(MIMEText(message, 'plain'))

	# send the message via the server set up earlier.
	s.send_message(msg)
	del msg

def iniciarSesion(browser):
	file = open("correoScopus.txt","r")
	correo = browser.find_element_by_id("bdd-email")
	correo.send_keys(file.readline().strip())
	browser.find_element_by_id("bdd-elsPrimaryBtn").click()
	sleep(2)
	password = browser.find_element_by_id("bdd-password")
	password.send_keys(file.readline().strip())
	browser.find_element_by_id("bdd-elsPrimaryBtn").click()
	file.close()

def sendInput(browser, row):
	input_ids = ["lastName","firstName","affiliation"]
	input_keys = [row["APELLIDOS_BASE"].split(" ")[0],row["NOMBRES_BASE"].split(" ")[0],"Escuela Superior Politecnica del Litoral"]
	input_divs = browser.find_elements_by_css_selector(".input.field")
	for i in range(len(input_ids)):
		element = browser.find_element_by_id(input_ids[i])
		element.send_keys(input_keys[i])

def clearInput(browser):
	input_ids = ["lastName","firstName","affiliation"]
	input_divs = browser.find_elements_by_css_selector(".input.field")
	for i in range(len(input_ids)):
		browser.find_element_by_id(input_ids[i]).clear()

def esperarLoad(browser):
	sleep(5)
	while len(browser.find_elements_by_class_name('loadingOverlay')) > 0:
		sleep(5)

def esperarSave(browser):
	sleep(5)
	while len(browser.find_elements_by_xpath('//*[text()="Your Researcher is being computed"]')) > 0:
		sleep(5)

def errorModal(browser):
	if (len(browser.find_elements_by_css_selector('.modal-msg.error')) > 0):
		return True
	return False

def eliminarInvestigadores(browser):
    browser.find_element_by_css_selector('label[for=selectAllCheckbox]').click()
    browser.find_element_by_id('deleteButton').click()
    sleep(5)
    browser.find_element_by_id('confirmDelete').click()

def getScivalName(browser):
	try:
		registerName = browser.find_element_by_id('resName-button')
		registerName = registerName.find_element_by_class_name('ui-selectmenu-text').text
	except:
		registerName = browser.find_element_by_id('resName').get_attribute('value')
	return registerName

def agregarInvestigador(browser, row):
	print('Registrando a ' + row["APELLIDOS_BASE"] + ' ' +row["NOMBRES_BASE"] + '...')
	sendInput(browser, row)
	browser.find_element_by_id("searchButton").click()
	esperarLoad(browser)
	if (browser.find_element_by_css_selector('.error.hidden').value_of_css_property('display') == 'none'):
		tablaAutor = browser.find_element_by_id('selectAuthorTable')
		if len(tablaAutor.find_elements_by_class_name('multiRow')) > 2:
			browser.find_element_by_css_selector('label[for=selectAllAuthorsCheckbox]').click()
			browser.find_element_by_id('skipToSaveButton').click()
			browser.find_element_by_id('skipToSaveModalButton').click()
		else:
			browser.find_element_by_id('skipToSaveButton').click()
		esperarLoad(browser)
		#errorModal(browser)
		registerName = getScivalName(browser)
		browser.find_element_by_id('saveAndDefineRes').click()
		esperarSave(browser)
		alreadySavedDiv = browser.find_element_by_id('defineEntityWrapper').find_elements_by_xpath('*')
		if (len(alreadySavedDiv) > 5):
			alreadySavedDiv[-2].find_element_by_css_selector('.btn.secondary').click()
			browser.find_element_by_xpath('//*[@id="defineEntityWrapper"]/nav/ol/li[1]').click()
			clearInput(browser)
			print('Docente ya se encuentra registrado')
			row["Ingresado"] == True
			row["nombre_scival"] = registerName
			return row
		print('Docente registrado')
		row["Ingresado"] == True
		row["nombre_scival"] = registerName
		return row
	clearInput(browser)
	print('Profesor no se encuentra en Scopus')
	row["Ingresado"] == False
	return row

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
investigadores = pd.read_excel(file_path)
investigadores["nombre_scival"] = ""
investigadores["Ingresado"] = False
sleep(2)

browser = webdriver.Chrome("chromedriver.exe")
browser.maximize_window()
browser.get("https://www.scival.com/mySciVal/ResearcherGroups")
iniciarSesion(browser)

try:
    eliminarInvestigadores(browser)
    sleep(5)
except:
    print('Sin investigadores registrados')

try:
    browser.find_element_by_xpath('//*[@id="actionControls"]/div[2]/div/div').click()
    browser.find_element_by_class_name('createResearcherLink').click()
except:
    browser.find_element_by_css_selector('.createResearcherLink.primary.btn').click()
esperarLoad(browser)
investigadores = investigadores.apply(lambda x: agregarInvestigador(browser,x), axis=1)
investigadores.to_excel('output.xlsx',index=False)

browser.close()
enviar_correo()