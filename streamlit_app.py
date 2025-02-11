# imports standards 
import os
import io
from dotenv import load_dotenv

#imports tiers 
import streamlit as st
import pandas as pd

from langchain_community.callbacks.manager import get_openai_callback

# Import des modules locaux
from modules_tracker.LegiFR_call_sandbox_funct import *
from modules_tracker.LegiFR_call_prod_funct import *
from modules_tracker.dataprep_funct import *
from modules_LLM.LLM_Analytic_changes import *
from modules_tracker.get_token import *

load_dotenv()

st.markdown(
    """
    <h1 style='text-align: center; color: navy;'>Legal French Tracker</h1>
    """,
    unsafe_allow_html=True
)

# Étape 1 : Sélection du Code Juridique
codes = {
    "Code monétaire et financier": "LEGITEXT000006072026",
    "Code civil": "LEGITEXT000006070721",
    "Code de commerce": "LEGITEXT000005634379",
    "Code des assurances": "LEGITEXT000006073984",
    "Code pénal": "LEGITEXT000006070719",
    "Code du travail": "LEGITEXT000006072050",
    "Code de la consommation": "LEGITEXT000006069565",
    "Code de la sécurité sociale": "LEGITEXT000006073189",
    "Code de procédure civile": "LEGITEXT000006070716",
    "Code de procédure pénale": "LEGITEXT000006071154",
    "Code de l'environnement": "LEGITEXT000006074220",
    "Code général des impôts": "LEGITEXT000006069574"
}


selected_code = st.selectbox("Sélectionnez un code juridique :", options=list(codes.keys()))
textCid = codes[selected_code]

# Étape 2 : Intervalle d'années
annee_debut = st.text_input("Entrez la date de début (année ou format JJ-MM-AAAA) :", value="2020")
annee_fin = st.text_input("Entrez la date de fin (année ou format JJ-MM-AAAA) :", value="2021")

# Filtrage sur N° de décret / ordonnance / loi
filtrer_numero = st.radio("Voulez-vous filtrer sur un N° de décret / ordonnance / loi ?", ("Non", "Oui"))

numero_1 = ""

if filtrer_numero == "Oui":
    numero_1 = st.text_input("Entrez un numéro de décret / ordonnance / loi ou mot clé :",
                             value="").strip()
    #numero_2 = st.text_input("Entrez un 2d numéro de décret / ordonnance / loi ou mot clé :", value="").strip()

# Activation brique LLM
active_llm = st.radio("Voulez vous avoir une analyse des changements de chaque article suivi d'un résumé global des changements ?  ", ("Non", "Oui"))

if active_llm == "Oui":
    llm_limit = st.selectbox("LLM limite (nbr de lignes):", options=[10,20,30])
    audience = st.selectbox("Sélectionnez le type d'audience pour l'analyse juridique:", options=["Tout Public", "Professionnel"])
    detail = st.selectbox("Sélectionnez le niveau de détail :", options= ["Succinct", "Détaillé"])

# Bouton exécution
if st.button("Lancer le tracker"):
    try:
        #access_token = get_token() sandbox API call functions
        access_token_prod = get_token_prod()

        st.success("Étape 0 - Récupération du token réussie")
    except Exception as e:
        st.error(f"Erreur lors de la récupération du token : {e}")

    # Test Ping Pong
    try:
        if ping_pong_test(access_token) == 'pong':
            st.success("Test Ping Pong : connexion réussie")
        else:
            st.error("Test Ping Pong : échec de connexion")
            st.stop()
    except Exception as e:
        st.error(f"Erreur lors du test Ping Pong : {e}")

    # Récupération des données
    try:
        json_output = get_text_modif_byDateslot_textCid_extract_content_prod(
            access_token_prod, textCid, annee_debut, annee_fin
        )
        st.success("Étape 1 - Requête API LégiFrance effectuée avec succès")
    except Exception as e:
        st.error(f"Étape 1 - Échec : {e}")

    
    try:
        # Formatage  données
        panda_output = transform_json_to_dataframe(json_output)
        
        # DataFrame Cleaning + prepare  
        panda_output.drop(['Version du', 
                           'Année',
                           'Est la dernière version',
                           'Nature Article Modificateur', 
                           'ID Parent', 'Nom Parent', 
                           'Date de fin (Article Cible)',
                           'Date de début cible Article Modificateur',
                           'CID Parent'
                           ], axis=1, inplace = True)
        panda_output.rename(columns={"Date de début cible d'entrée en vigueur": "Date de début cible",
                                     "Action Article Modificateur":"Action" }, inplace= True)
        panda_output.reset_index(drop=True, inplace=True)
        st.success(f"Étape 2 - Formatage des données réussi : {len(panda_output)} lignes créées")
    
    except Exception as e:
        st.error(f"Étape 2 - Échec : {e}")
        
    #  Filtrage par N° de décret / ordonnance / loi

    try:
        if numero_1 :
            panda_output = panda_output[panda_output["Titre Article Modificateur"].astype(str).str.contains(numero_1, na=False, case=False)]
            st.success(f"Filtrage appliqué : {len(panda_output)} lignes gardées")
        else:
            st.success(" Aucun filtrage appliqué, toutes les données sont affichées.")

    except Exception as e:
        # En cas d'erreur, affiche un message pour l'utilisateur
        st.error(f"Erreur lors du filtrage : {e}")

    # Ajout l'ancien contenu
    try:
        ajout_col_AV_prod(panda_output)
        st.success("Étape 4 - Ajout de l'ancienne version des articles réussi")
    except Exception as e:
        st.error(f"Étape 4 - Échec : {e}")

    # Ajout nouveau contenu
    try:
        ajout_col_coutenu_NV_prod(panda_output)
        st.success("Étape 5 - Ajout de la nouvelle version des articles réussi")
    except Exception as e:
        st.error(f"Étape 5 - Échec : {e}")

    # Ajout colonne comparative
    try:
        compare_AV_vs_NV(panda_output)
        st.success("Étape 6 - Ajout de la colonne de comparaison réussi")
    except Exception as e:
        st.error(f"Étape 6 - Échec : {e}")
        
    # LLM analysis /com
    try:
        if active_llm == "Oui":
            st.success(f"Étape 7 - Lancement de l'analyse des textes juridiques par le LLM ({llm_limit} premiers changements) ")
            
            # Applying LLM function:
            panda_output = llm_apply_row(panda_output.iloc[0:llm_limit,:])
            
            # Concate all LLM commentaries 
            text_variable = panda_output['LLM_Change_Analysis_1'].str.cat()
            
            # WapUp LLM analysis 
            summary = wrap_up_multi(text_variable, audience, detail)
            
            st.success("Étape 7 - Analyse juridique réussie")
        
            st.success("Étape 7 - Analyse juridique exportée")
            st.write(f""" {summary}""")
        else :  
            st.success("Étape 7 - Absence de comparaison")
        
    except Exception as e:
        st.error(f"Étape 7 - Échec : {e}")

    # Export en mémoire et téléchargement
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            panda_output.to_excel(writer, index=False, sheet_name='Données')
        st.success("Étape 8 - Fichier Excel préparé pour téléchargement")

        st.write(f"Aperçu du tableau des modifications du {selected_code} de {annee_debut} a/au {annee_fin}")
        
        st.dataframe(panda_output.head(15))
        

        st.download_button(
            label="Télécharger le fichier Excel",
            data=buffer.getvalue(),
            file_name="DB_Legifrance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Étape 8 - Échec : {e}")