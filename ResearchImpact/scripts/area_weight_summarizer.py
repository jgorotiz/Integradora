import pandas as pd
import json

with open('../Config/config.json') as json_data_file:
    data = json.load(json_data_file)

for ranking in ['QS','ASJC']:
	dfPubCit = pd.read_excel("Productividad Ecuador " + ranking + " .xlsx")

	for productivity in data['rangos'].keys():
		regex = 'area|' + productivity
		publicados = dfPubCit.filter(regex=regex)
		
		year_min = str(data['rangos'][productivity]['desde'])
		year_max = str(data['rangos'][productivity]['hasta'])
		productivity = productivity+"_"
		
		dfPubCit['total_' + productivity] = publicados.apply(lambda x : sum(x[productivity + year_min: productivity + year_max]), axis = 1)

	total_publicaciones = dfPubCit['total_publicados_'].iloc[0]
	total_citaciones = dfPubCit['total_citaciones_'].iloc[0]
	dfPubCit = dfPubCit.iloc[1:]

	dfPubCit['Wp'] = dfPubCit['total_publicados_'].apply(lambda x: total_publicaciones/(x*len(dfPubCit)))
	dfPubCit['Wc'] = dfPubCit['total_citaciones_'].apply(lambda x: total_citaciones/(x*len(dfPubCit)))
	dfPubCit.filter(regex='area|Wp|Wc')[['area','Wp','Wc']].to_excel("Pesos Scopus " + ranking + ".xlsx",index=False)