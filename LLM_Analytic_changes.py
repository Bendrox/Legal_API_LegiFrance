import getpass
import os
import tiktoken
import sys
import pandas as pd 
from credentials import *

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# LLM definition co
llm = AzureChatOpenAI(
    azure_endpoint= Azure_OpenAI_OB_Endpoint ,
    openai_api_version="2024-02-15-preview",
    model_name="gpt-4o",
    openai_api_key= Azure_OpenAI_OB_Key,
    openai_api_type="azure",
    temperature=0,
    deployment_name="gpt-4o-deploy",
    #streaming=True,
)

#Token counter: 
def count_tokens(text, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text) # texte to tokens
    return len(tokens)

# Function to get legal comment from the LLM about the change in each article:   
def llm_legal_change_com_v1(old_version, new_version): 
    prompt = ChatPromptTemplate.from_messages([("system",
            """
            Tu es un avocat et analyste juridique très expérimenté, tu as pour but d'analyser et de commenter les changements 
            réglementaires de chaque article , tu trouveras ici l'ancienne et la nouvelle version de l'article que l on te donne. 
            Tu adopteras un language juridique précis. Tu n'inventeras rien et tu te baseras uniquement sur les données fournies.
            Si tu ne sais pas ou tu ne comprends pas , dis le. 
            Inutile de reciter les textes fournis, tu ne retourneras que ton analyse.
            """),
        ("human", 
            "Voici l'ancienne version de l'article a analyser {old_version} et voici la nouvelle version du meme article {new_version}")])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "old_version": old_version,
        "new_version": new_version})
    
    return llm_output

# Function to get legal comment from the LLM about the change in each article:  
## Inhencing the prompt  
def llm_legal_change_com_v2(old_version, new_version): 
    prompt = ChatPromptTemplate.from_messages([("system",                                  
        """
	Tu es un avocat et analyste juridique très expérimenté. 
    Ta mission consiste à examiner et commenter les évolutions réglementaires d’un article de loi en comparant sa version 
    antérieure avec sa version révisée.

	Consignes :
	1.	Utilise un langage juridique précis.
	2.	Base-toi uniquement sur les informations fournies, sans inventer ni extrapoler.
	3.	Si tu ne comprends pas un point ou si les informations sont insuffisantes, signale-le clairement.
	4.	Ne récite pas le texte en intégralité : concentre-toi sur l’analyse et la comparaison.

	Contenu à analyser :
	•	Ancienne version : {old_version}
	•	Nouvelle version : {new_version}

	Objectif :
    Produis un commentaire juridique concis, en mettant en évidence les principaux changements, leur portée et leurs éventuelles conséquences. N’inclus dans ta réponse que l’analyse finale.

            """)])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "old_version": old_version,
        "new_version": new_version})
    
    return llm_output


# Function to get legal comment from the LLM about the change in each article:  
## Inhencing the prompt  
def llm_legal_change_com_v3(old_version, new_version): 
    prompt = ChatPromptTemplate.from_messages([("system",                                  
        """
	Tu es un avocat et analyste juridique très expérimenté. 
    Ta mission consiste à examiner et commenter les évolutions réglementaires d’un article de loi en comparant sa version 
    antérieure avec sa version révisée.

	Consignes :
	1.	Utilise un langage juridique précis.
	2.	Base-toi uniquement sur les informations fournies, sans inventer ni extrapoler.
	3.	Si tu ne comprends pas un point ou si les informations sont insuffisantes, signale-le clairement.
	4.	Ne récite pas le texte en intégralité : concentre-toi sur l’analyse et la comparaison.

	Contenu à analyser :
	•	Ancienne version : {old_version}
	•	Nouvelle version : {new_version}

	Objectif :
    Produis un commentaire juridique concis, en mettant en évidence les principaux changements, leur portée et leurs éventuelles conséquences. N’inclus dans ta réponse que l’analyse finale.

            """)])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "old_version": old_version,
        "new_version": new_version})
    
    return llm_output

#importing a file : 
def import_xlsx_to_pandas(path :str): #"/Users/oussa/Desktop/Github_perso/Legal_FR_Tracker/data_output/Legifrance_DB_TrackChange.xlsx"
    imported_DB= pd.read_excel(path)
    return imported_DB

#Filter on Titre Article Modificateur - pd
def filter_titre_art_modificat_pd(pd_db_file, terme_filtre_1 :str, terme_filtre_2:str ): 
    #"/Users/oussa/Desktop/Github_perso/Legal_FR_Tracker/data_output/Legifrance_DB_TrackChange.xlsx"
    pd_db_file =  pd_db_file[pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_1)| pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_2) ]
    return pd_db_file

#Filter on Titre Article Modificateur - Excel
def filter_titre_art_modificat_xl(xl_file, terme_filtre_1 :str, terme_filtre_2:str ): 
    #"/Users/oussa/Desktop/Github_perso/Legal_FR_Tracker/data_output/Legifrance_DB_TrackChange.xlsx"
    pd_db_file = pd.DataFrame(xl_file)
    pd_db_file =  pd_db_file[pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_1)| pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_2) ]
    return pd_db_file

# Applying LLM on each row :
def llm_apply_row(pd_db_file):
    pd_db_file['LLM_Change_Analysis_1'] = pd_db_file.apply(
    lambda row: llm_legal_change_com_v1(row['Contenu_Ancien_Article'], row['Contenu_Nouv_Vers_Article']), 
    axis=1)
    return pd_db_file


