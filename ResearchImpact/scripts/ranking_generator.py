import pandas as pd
import json
from datetime import date

pesos = pd.read_excel('Pesos Scopus ASJC.xlsx')
datos_scival = pd.read_excel('output.xlsx')[['nombre_scival','NOMBREUNIDAD']]
df_rankings = []
today = str(date.today())

with open('../Config/config.json') as json_data_file:
    data = json.load(json_data_file)

for key in data["terminologia"].keys():
    terminologia = data["terminologia"][key]
    df_variable = pd.read_excel(data["finalfiles"]["ASJC"][key])
    
    cols = ['autor']
    ranking_variable = pd.DataFrame(columns=cols)
    ranking_variable['autor'] =  df_variable['autor'].unique()
    
    for autor in df_variable['autor'].unique():
        autor_df = df_variable.loc[df_variable['autor'] == autor]
        autor_df = pd.merge(left=autor_df, right=pesos, left_on='area', right_on='area')
        autor_df['valores'] = autor_df.apply(lambda x: x['suma'] * x[data["pesos"][key]["termino"]], axis=1)

        ranking_variable.loc[ranking_variable['autor']==autor, terminologia+'_n'] = autor_df['valores'].sum()
        ranking_variable.loc[ranking_variable['autor']==autor, key + '_por_area'] = autor_df['suma'].sum()

    ranking_variable[terminologia+'_d'] = ranking_variable[terminologia+'_n'].sum()
    ranking_variable[terminologia] = ranking_variable.apply(lambda x: x[terminologia+'_n']/x[terminologia+'_d'], axis=1)
    ranking_variable.to_excel("ranking_" + terminologia + ".xlsx",index=False)
    
    df_rankings.append(ranking_variable)

ranking_final = pd.merge(left=df_rankings[0], right=df_rankings[1], left_on='autor', right_on='autor')
ranking_final = pd.merge(left=ranking_final, right=datos_scival, left_on='autor', right_on='nombre_scival')
col_facultad = ranking_final['NOMBREUNIDAD']
ranking_final = ranking_final.drop(['nombre_scival','NOMBREUNIDAD'], axis=1)
ranking_final.insert(1, 'NOMBREUNIDAD', col_facultad)

key = list(data["terminologia"].keys())
ranking_final['ranking_profesor'] = ranking_final.apply(lambda x: (x[data["terminologia"][key[0]]]* data["pesos"][key[0]]["porcentaje"]) + (x[data["terminologia"][key[1]]]* data["pesos"][key[1]]["porcentaje"]), axis=1)


ranking_final = ranking_final[['autor','NOMBREUNIDAD','ranking_profesor']]
# ranking_final.to_excel("../Ranking/ranking_institucional_" + today + ".xlsx",index=False)
ranking_final.to_json("../Ranking/ranking_institucional_" + today + ".json",orient='index')