# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 12:25:11 2019

@author: Utilisateur
"""

#Ici on va trouver les journées types

import pandas as pd
from scipy.special import erfinv
import numpy as np
import pomegranate as pg
import matplotlib.pyplot as plt
import fonction_bool as fb
import probmodel as pm
import math
import module_modele_jour as mmj
import sys
import time

TYPE_JOUR = 1
MOY_TRANS = [3.30, 3.31]
DISTANCE_MAX = 100

data = pd.read_csv("K_deploc.csv", sep=";", encoding="ISO-8859-1", low_memory = False)
data_indiv = pd.read_csv("Q_individu.csv", sep=";", encoding="ISO-8859-1", low_memory = False)

data_indiv.loc[:,'IDENT_IND'] = data_indiv['idENT_MEN']*100 + data_indiv['NOI']
data_filt_inter = data[(data['V2_TYPJOUR'] == TYPE_JOUR) &
                       (data['V2_MORIDOM'] == 1) &
                       (data['V2_MDISTTOT'] > 0) &
                       (data['V2_VAC_SCOL'] == 0) &
                       (data['V2_MDISTTOT'] < DISTANCE_MAX) &
                       (data['V2_MNBMOD'] == 1) &
                       (data['V2_MTP'].isin(MOY_TRANS))]

data_indiv = data_indiv[['IDENT_IND','V1_BTRAVT','V1_BTRAVHS','SITUA']].copy()

def changer_categorie_motifs(x):
    #On transforme motifs personnels en 5 (catégorie la moins utile) + on transforme les loisirs en deux catégories qui nous intéressent ici : grand et petit parking
    if x == 8.89:
        x = 3
    elif (x == 2.2 or x == 7.72 or x == 7.74 or x == 7.75):
        #ce sont les grands parking
        x = 2
    elif x==2.21 or (x >= 3 and x<=6) or (math.floor(x)==7 and not(x == 7.72 or x == 7.74 or x == 7.75)):
        #ce sont les petits parkings
        x = 3
    return x


data_filt = data_filt_inter[['POIDS_JOUR', 'V2_TYPJOUR', 'V2_MORIHDEP',
                             'V2_MMOTIFDES', 'V2_DUREE', 'V2_MDISTTOT',
                             'IDENT_IND', 'V2_DURACT']].copy()

data_filt.loc[:,'V2_MMOTIFDES'] = data_filt['V2_MMOTIFDES'].apply(changer_categorie_motifs)

#data_join = data_filt.merge(data_indiv[['IDENT_IND','V1_BTRAVT','V1_BTRAVHS','SITUA']], left_on='IDENT_IND', right_on='IDENT_IND', how='left')



import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


del data_filt_inter, data

(profil_mob, dic_nblois, dic_tranchlois, dic_parklois, dic_dureelois, df) = mmj.modele_jours_type(data_filt, data_indiv)
del data_indiv, data_filt

df['V2_MORIHDEP'] = pd.to_timedelta(df['V2_MORIHDEP'], errors = 'coerce')

taille=0
dic_param_trajets={}
dic_param_trajets['domtravail'] = [pm.probparam(df, 'domtravail', 5, 10.5, 9)]
dic_param_trajets['domtravail'].append(pm.probparam(df, 'domtravail', 15, 21, 1))
dic_param_trajets['domtravailmidi'] = [pm.probparam(df, 'domtravailmidi', 5, 10.5, 9)]
dic_param_trajets['domtravailmidi'].append(pm.probparam(df, 'domtravailmidi', 11, 14, 1))
dic_param_trajets['domtravailmidi'].append(pm.probparam(df, 'domtravailmidi', 12, 15, 9))
dic_param_trajets['domtravailmidi'].append(pm.probparam(df, 'domtravailmidi', 15, 21, 1))
print("coucou")
dic_param_trajets['domtravailloisirs'] = [pm.probparam(df, 'domtravailloisirs', 5, 10.5, 2)]
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 5, 10.5, 3))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 5, 10.5, 9))
print("on arrive là ou pas ?")
print(getsize(dic_param_trajets))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 5, 10.5, 1))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 11, 14, 2))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 11, 14, 3))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 11, 15, 9))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 15, 23, 3))
print("et là ?")
time.sleep(10)
print(getsize(dic_param_trajets))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 15, 23, 2))
print(getsize(dic_param_trajets))
dic_param_trajets['domtravailloisirs'].append(pm.probparam(df, 'domtravailloisirs', 15, 23, 1))
print(getsize(dic_param_trajets))
print("on passe aux gros")
time.sleep(3)
print("et c'est parti")
dic_param_trajets['domtravailmidiloisirs'] = [pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 2)]
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 3))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 9))
taille+= getsize(dic_param_trajets['domtravailmidiloisirs'])
print(taille)
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 5, 10.5, 1))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 11, 14, 2))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 11, 14, 1))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 11, 14, 3))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 11, 15, 9))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 15, 23, 3))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 15, 23, 2))
dic_param_trajets['domtravailmidiloisirs'].append(pm.probparam(df, 'domtravailmidiloisirs', 15, 23, 1))



dic_param_trajets['domloisirs'] = [pm.probparam(df, 'domloisirs', 5, 10.5, 2)]
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 5, 10.5, 3))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 5, 11, 1))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 11, 14.5, 2))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 11, 15, 1))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 11, 14.5, 3))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 11, 15, 9))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 15, 23, 3))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 15, 23, 2))
dic_param_trajets['domloisirs'].append(pm.probparam(df, 'domloisirs', 15, 23, 1))







