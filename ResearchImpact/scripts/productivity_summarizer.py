import pandas as pd
import json
from datetime import datetime

with open('../Config/config.json') as json_data_file:
    data = json.load(json_data_file)

for ranking,file in data['filenames'].items():
    df = pd.read_excel(file)
    for productivity in data['rangos'].keys():
        regex = 'autor|area|' + productivity
        publicados = df.filter(regex=regex)
        year_min = str(data['rangos'][productivity]['desde'])
        year_max = str(data['rangos'][productivity]['hasta'])
        productivity = productivity+"_"
        
        publicados['suma'] = publicados.apply(lambda x : sum(x[productivity + year_min: productivity + year_max]), axis = 1)
        
        publicados.filter(regex='autor|area|suma')[['area','autor','suma']].to_excel(productivity + "Scopus " + ranking + ".xlsx",index=False)