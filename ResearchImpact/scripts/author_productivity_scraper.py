import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import numpy as np

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
	
def getAutores(browser):
	linkList = []
	
	browser.find_element_by_css_selector('#iconPanel li[data-entitytype=researcher]').click()
	sleep(2)
	authorList = browser.find_element_by_css_selector('.entity-list.selected')
	#entityListPanel > div > div.others-section > ul
	for author in authorList.find_elements_by_tag_name('li'):
		linkList.append(author.find_element_by_tag_name('input').get_attribute('value'))
	return linkList

def inicializarDf(browser):
	columns = ['autor','area']
	years = browser.find_element_by_xpath('//*[@id="yearRangeDropdown-button"]/span[2]').text.split(" ")
	for i in range (int(years[0]),int(years[2])+1):
		columns.append('publicados_'+str(i))
		columns.append('citaciones_'+str(i))
	df = pd.DataFrame(columns=columns)
	return df
	
def inicializarDict(df):
	row = {}
	for col in df.columns:
		row[col] = 0
	return row

def encontrarAño(browser):
	browser.find_element_by_id('yearRangeDropdown-button').click()
	options = browser.find_elements_by_class_name('ui-menu-item')
	rangoMax = 0
	for option in options:
		rango = option.find_element_by_class_name('ui-menu-item-wrapper').text
		if (">" not in rango):
			rango = rango.split(" ")
			rango = int(rango[2]) - int(rango[0])
			if (rango > rangoMax):
				rangoMax = rango
				opcionCorrecta = option
	opcionCorrecta.click()

def esperarUpdate(browser):
	sleep(2)
	while len(browser.find_elements_by_xpath('//*[text()="Updating..."]')) > 0:
		sleep(2)

def soloEspol(browser):
	institutionsBtn = browser.find_element_by_css_selector('label[for=homeInstFilterCheckbox]')
	background_color = browser.execute_script("return window.getComputedStyle(document.querySelector('label[for=homeInstFilterCheckbox]'),':after').getPropertyValue('background-color')")
	if (background_color.split(', ')[1] == '170'):
		institutionsBtn.click()
		print('entro')

browser = webdriver.Chrome("chromedriver.exe")
browser.maximize_window()
browser.get("https://www.scival.com/overview/summary?uri=Institution%2F701420")
iniciarSesion(browser)
sleep(2)
linkList = getAutores(browser)
esperarUpdate(browser)
first = True
for ranking in ['QS','ASJC']:
	dfAuthors = inicializarDf(browser)

	subjectPreference = browser.find_element_by_id('subjectAreaPreferenceLink')
	if subjectPreference.text != ranking:
		subjectPreference.click()
		sleep(3)
		browser.find_element_by_css_selector('label.radio-label[for=journalCategory_'+ranking+']').click()
		browser.find_element_by_id('selSubjectAreaPreference').click()
		esperarUpdate(browser)
	
	if first:
		browser.find_element_by_xpath('//*[@id="home-institution-filter"]/div/label').click()
		sleep(2)
		encontrarAño(browser)
		esperarUpdate(browser)
			
	for link in linkList:
		#Summary Page
		browser.get("https://www.scival.com/overview/summary?uri=" + link)
		
		authorData = []
		sleep(2)
		
		if first:
			soloEspol(browser)
			esperarUpdate(browser)
			first = False
		browser.find_element_by_xpath('//*[@id="subNavScroll"]/ul/li[4]/a').click()
		#Published Page
		browser.find_element_by_id('journalCategoryDropdown').click()
		esperarUpdate(browser)
		studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
		while len(studyAreas) == 0:
			browser.find_element_by_id('journalCategoryDropdown').click()
			esperarUpdate(browser)
			studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
		studyAreas = browser.find_element_by_css_selector('.menu.transition.visible')
		numAreas = len(studyAreas.find_elements_by_css_selector('div.item')[1:])
		browser.find_element_by_id('journalCategoryDropdown').click()
		esperarUpdate(browser)
		
		for i in range(numAreas):
			authorRow = inicializarDict(dfAuthors)
			authorRow['autor'] = browser.find_element_by_xpath('//*[@id="contentPanel"]/div/header/section[1]/div/h1').text
			browser.find_element_by_id('journalCategoryDropdown').click()
			esperarUpdate(browser)
			studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
			while len(studyAreas) == 0:
				browser.find_element_by_id('journalCategoryDropdown').click()
				esperarUpdate(browser)
				studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
			studyAreas = browser.find_element_by_css_selector('.menu.transition.visible')
			authorRow['area'] = studyAreas.find_elements_by_css_selector('div.item')[1:][i].text
			studyAreas.find_elements_by_css_selector('div.item')[1:][i].click()
			esperarUpdate(browser)
			noInfoDiv = browser.find_element_by_id('publicationSummary_zeroPublicationInfo')
			if (noInfoDiv.get_attribute('style') == 'display: none;'):
				years = browser.find_elements_by_css_selector('.highcharts-point.highcharts-color-0')
				
				for year in years:
					data = year.get_attribute('aria-label').split(' ')
					authorRow['publicados_'+data[1][:-1]] = int(data[2][:-1])
			authorData.append(authorRow)
		browser.find_element_by_xpath('//*[@id="subNavScroll"]/ul/li[6]/a').click()
		#Cited Page
		for i in range(numAreas):
			esperarUpdate(browser)
			browser.find_element_by_id('journalCategoryDropdown').click()
			esperarUpdate(browser)
			studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
			while len(studyAreas) == 0:
				browser.find_element_by_id('journalCategoryDropdown').click()
				esperarUpdate(browser)
				studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
			studyAreas = browser.find_element_by_css_selector('.menu.transition.visible')
			studyAreas.find_elements_by_css_selector('div.item')[1:][i].click()
			esperarUpdate(browser)
			citationsChart = browser.find_elements_by_class_name('highcharts-root')
			noInfoDiv = browser.find_element_by_id('citations_zeroPublicationInfo')
			if (len(citationsChart) > 0 and noInfoDiv.get_attribute('style') == 'display: none;'):
				years = citationsChart[0].find_elements_by_css_selector('.highcharts-point.highcharts-color-0')
				
				for year in years:
					data = year.get_attribute('aria-label').split(' ')
					authorData[i]['citaciones_'+data[1][:-1]] = int(data[2][:-1])
		for row in authorData:
			dfAuthors = dfAuthors.append(row, ignore_index=True)
		sleep(2)

	dfAuthors.to_excel("productividad" + ranking + ".xlsx",index=False)
browser.close()