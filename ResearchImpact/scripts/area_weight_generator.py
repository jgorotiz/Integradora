import pandas as pd
import selenium.webdriver as webdriver
from time import sleep

def iniciarSesion(browser):
	file = open("correoDecanato.txt","r")
	correo = browser.find_element_by_id("bdd-email")
	correo.send_keys(file.readline().strip())
	browser.find_element_by_id("bdd-elsPrimaryBtn").click()
	sleep(4)
	password = browser.find_element_by_id("bdd-password")
	password.send_keys(file.readline().strip())
	browser.find_element_by_id("bdd-elsPrimaryBtn").click()
	file.close()

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

options = webdriver.ChromeOptions()

options.binary_location = "/Users/shippify/Desktop/Google Chrome.app/Contents/MacOS/Google Chrome"

chrome_driver_binary = "./chromedriver"

browser = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
browser.maximize_window()
browser.get("https://www.scival.com/overview/summary")
iniciarSesion(browser)

browser.find_element_by_css_selector('.link.country').click()
try:
	browser.find_element_by_class_name('empty-section-text')
	browser.find_element_by_id('addMoreText_country'.send_keys("Ecuador\n"))
except Exception:
	pass

browser.find_element_by_css_selector('label[for="selectEntity_Country_218"]').click()
sleep(3)
encontrarAño(browser)
sleep(2)

for ranking in ['QS','ASJC']:
	subjectPreference = browser.find_element_by_id('subjectAreaPreferenceLink')
	if subjectPreference.text != ranking:
		subjectPreference.click()
		sleep(3)
		browser.find_element_by_css_selector('label.radio-label[for=journalCategory_'+ranking+']').click()
		browser.find_element_by_id('selSubjectAreaPreference').click()
	sleep(2)

	dfPubCit = inicializarDf(browser)
	areaData = []
	browser.find_element_by_xpath('//*[@id="subNavScroll"]/ul/li[3]/a').click()

	#Published Page
	browser.find_element_by_id('journalCategoryDropdown').click()
	sleep(2)
	studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
	while len(studyAreas) == 0:
		browser.find_element_by_id('journalCategoryDropdown').click()
		esperarUpdate(browser)
		studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
	studyAreas = browser.find_element_by_css_selector('.menu.transition.visible')
	numAreas = len(studyAreas.find_elements_by_css_selector('div.item'))
	browser.find_element_by_id('journalCategoryDropdown').click()
	sleep(2)

	for i in range(numAreas):
		authorRow = inicializarDict(dfPubCit)
		authorRow['autor'] = browser.find_element_by_xpath('//*[@id="contentPanel"]/div/header/section[1]/div/h1').text
		browser.find_element_by_id('journalCategoryDropdown').click()
		esperarUpdate(browser)
		studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
		while len(studyAreas) == 0:
			browser.find_element_by_id('journalCategoryDropdown').click()
			esperarUpdate(browser)
			studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
		studyAreas = browser.find_element_by_css_selector('.menu.transition.visible')
		authorRow['area'] = studyAreas.find_elements_by_css_selector('div.item')[i].text
		studyAreas.find_elements_by_css_selector('div.item')[i].click()
		esperarUpdate(browser)
		years = browser.find_elements_by_css_selector('.highcharts-point.highcharts-color-0')
			
		for year in years:
			data_year = year.get_attribute('aria-label').split(' ')
			authorRow['publicados_'+data_year[1][:-1]] = int(data_year[2][:-1].replace(',',''))
		areaData.append(authorRow)
	browser.find_element_by_xpath('//*[@id="subNavScroll"]/ul/li[5]/a').click()
	#Cited Page
	for i in range(numAreas):
		browser.find_element_by_id('journalCategoryDropdown').click()
		esperarUpdate(browser)
		studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
		while len(studyAreas) == 0:
			browser.find_element_by_id('journalCategoryDropdown').click()
			esperarUpdate(browser)
			studyAreas = browser.find_elements_by_css_selector('.menu.transition.visible')
		studyAreas = browser.find_element_by_css_selector('.menu.transition.visible')
		studyAreas.find_elements_by_css_selector('div.item')[i].click()
		esperarUpdate(browser)
		citationsChart = browser.find_elements_by_class_name('highcharts-root')
		noInfoDiv = browser.find_element_by_id('citations_zeroPublicationInfo')
		
		citationsChart = browser.find_elements_by_class_name('highcharts-root')
		years = citationsChart[0].find_elements_by_css_selector('.highcharts-point.highcharts-color-0')
		for year in years:
			data_year = year.get_attribute('aria-label').split(' ')
			areaData[i]['citaciones_'+data_year[1][:-1]] = int(data_year[2][:-1].replace(',',''))
	for row in areaData:
		dfPubCit = dfPubCit.append(row, ignore_index=True)

	dfPubCit.to_excel("Productividad Ecuador " + ranking +" .xlsx",index=False)
	
browser.close()