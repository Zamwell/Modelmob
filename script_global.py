# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 12:07:26 2019

@author: Utilisateur
"""

import pandas as pd
from scipy.special import erfinv
import numpy as np
import pomegranate as pg
import matplotlib.pyplot as plt
import fonction_bool as fb
import probmodel as pm

TYPE_JOUR = 1
MOY_TRANS = [3.30, 3.31]
DISTANCE_MAX = 100

data = pd.read_csv("K_deploc.csv", sep=";", encoding="ISO-8859-1")

data_filt_inter = data[(data['V2_TYPJOUR'] == TYPE_JOUR) &
                       (data['V2_MORIDOM'] == 1) &
                       (data['V2_MDISTTOT'] > 0) &
                       (data['V2_VAC_SCOL'] == 0) &
                       (data['V2_MDISTTOT'] < DISTANCE_MAX) &
                       (data['V2_MNBMOD'] == 1) &
                       (data['V2_MTP'].isin(MOY_TRANS))]

data_filt = data_filt_inter[['POIDS_JOUR', 'V2_TYPJOUR', 'V2_MORIHDEP',
                             'V2_MMOTIFDES', 'V2_DUREE', 'V2_MDISTTOT',
                             'IDENT_IND']]

del data_filt_inter

dic_modele_trajet = {}
dic_type_de_journee = {}


