# -*- coding: utf-8 -*-
"""
Created on Sat May  4 17:10:01 2019

@author: Any
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

#Compter nb trajets (pas utile ?)
"""
data_nbtraj = data_filt.copy()
data_nbtraj['NB_TRAJ'] = data_nbtraj.groupby(by='IDENT_IND')['V2_MORIHDEP'].transform('count')
data_nbtraj = data_nbtraj.groupby(by='NB_TRAJ', as_index=False)['POIDS_JOUR'].sum()
pg_nbtraj = pg.DiscreteDistribution.from_samples(
        data_nbtraj['NB_TRAJ'].values.flatten(),
        weights=data_nbtraj['POIDS_JOUR'].values.flatten())
"""

del data_filt_inter
del data


#Evaluer la journée type avec map filter
data_journee = data_filt.copy()
data_journee.loc[:,'V2_MORIHDEP'] = pd.to_timedelta(data_journee['V2_MORIHDEP'],errors='coerce')
data_journee['MOTIF_HDEP']=list(zip(data_journee['V2_MMOTIFDES'],data_journee['V2_MORIHDEP']))
data_journee = data_journee.sort_values(['IDENT_IND','V2_MORIHDEP']).groupby(['IDENT_IND'])['MOTIF_HDEP'].apply(lambda x:list(x)).reset_index()
nb_profil_mob = [len(data_journee[data_journee['MOTIF_HDEP'].map(f)]['MOTIF_HDEP'].values) for name,f in fb.__dict__.items() if callable(f)]
nb_profil_mob = [x/sum(nb_profil_mob) for x in nb_profil_mob]
profil_mob=pg.DiscreteDistribution(dict(zip([name for name,f in fb.__dict__.items() if callable(f)],nb_profil_mob)))

li_prob=[]

(trav_matin_dist, trav_matin_quartdist) = pm.probparam(data_filt,5,11,9)
(dom_midi_dist, dom_midi_quartdist) = pm.probparam(data_filt,11,14,1)
(trav_aprem_dist, trav_aprem_quartdist) = pm.probparam(data_filt,12,15,9)
(dom_soir_dist, dom_soir_quartdist) = pm.probparam(data_filt,15,21,1)

li_prob.append(pm.probparam(data_filt,5,11,9))
li_prob.append(pm.probparam(data_filt,11,14,1))
li_prob.append(pm.probparam(data_filt,12,15,9))
li_prob.append(pm.probparam(data_filt,15,21,1))

