#!/usr/bin/python
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

with open('../Config/config.json') as json_data_file:
    data = json.load(json_data_file)

sendFrom = admin_data('correoScopus,txt')
sendTo = get_contact(data,"receptor")

# set up the SMTP server
s = smtplib.SMTP('smtp.office365.com:587')
s.ehlo()
s.starttls()
s.login(sendFrom[0], sendFrom[1])

message_template = read_template('template.txt')
msg = MIMEMultipart()

# setup the parameters of the message
msg['From']=sendFrom[0]
msg['To']=sendTo[1]
msg['Subject']="Ranking ESPOL"
message = message_template.substitute(NOMBRE_PROCESO=sys.argv[1])

# add in the message body
msg.attach(MIMEText(message, 'plain'))

# send the message via the server set up earlier.
s.send_message(msg)

del msg