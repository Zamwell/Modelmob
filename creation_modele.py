# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 10:48:29 2019

@author: Utilisateur
"""

import pandas as pd
#from scipy.stats import lognorm, kstest, shapiro
from scipy.special import erfinv
import numpy as np
import pomegranate as pg
import matplotlib.pyplot as plt
import fonction_bool as fb

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

#Compter nb trajets

data_nbtraj = data_filt.copy()
data_nbtraj['NB_TRAJ'] = data_nbtraj.groupby(by='IDENT_IND')['V2_MORIHDEP'].transform('count')
data_nbtraj = data_nbtraj.groupby(by='NB_TRAJ', as_index=False)['POIDS_JOUR'].sum()
pg_nbtraj = pg.DiscreteDistribution.from_samples(
        data_nbtraj['NB_TRAJ'].values.flatten(),
        weights=data_nbtraj['POIDS_JOUR'].values.flatten())


del data_filt_inter
del data


#Evaluer la journée type
data_journee = data_filt.copy()
data_journee.loc[:,'V2_MORIHDEP'] = pd.to_timedelta(data_journee['V2_MORIHDEP'],errors='coerce')
data_journee['MOTIF_HDEP']=list(zip(data_journee['V2_MMOTIFDES'],data_journee['V2_MORIHDEP']))
data_journee = data_journee.sort_values(['IDENT_IND','V2_MORIHDEP']).groupby(['IDENT_IND'])['MOTIF_HDEP'].apply(lambda x:list(x)).reset_index()
#stat_journee_type=data_journee.groupby(['V2_MMOTIFDES'],as_index=False)['IDENT_IND'].count()

#Evaluer les journees types avec map filter
nb_profil_mob = [len(data_journee[data_journee['MOTIF_HDEP'].map(f)]['MOTIF_HDEP'].values) for name,f in fb.__dict__.items() if callable(f)]
nb_profil_mob = [x/sum(nb_profil_mob) for x in nb_profil_mob]
profil_mob=pg.DiscreteDistribution(dict(zip([name for name,f in fb.__dict__.items() if callable(f)],nb_profil_mob)))

#(sigma, loc, mu_exp)= lognorm.fit(data_filt['V2_MDISTTOT'].values.flatten(),floc=0);
#mu=np.log(mu_exp);
#del loc;
#del mu_exp;
#print('mu = ', mu);
#print('sigma = ',sigma);

#On détermine les paramètres de la loi lognormale de la distance

pg_dist = pg.LogNormalDistribution(0, 1)
pg_dist.fit(data_filt['V2_MDISTTOT'].values.flatten(),
            weights=data_filt['POIDS_JOUR'].values.flatten())
pg_mu, pg_sigma = pg_dist.parameters
print(pg_mu)
print(pg_sigma)

#On fait une liste des quartiles de la distance

Q = [np.exp(pg_mu + np.sqrt(2*pg_sigma)*erfinv(2*x-1)) for x in [0.25, 0.5, 0.75]]
Q.append(100)
Q.insert(0, 0)

discret_tempo_hdep = pd.to_timedelta(["{}:{}:00".format((x*5)//60,
                                      (x*5)%60) for x in range(0, 12*24)])
prob_hdep = []

#On créée les probas de l'heure de départ pour chaque quartile de distance
for i in range(0, len(Q)-1):
    prob_hdep.append([[x, 0] for x in discret_tempo_hdep])
    #On filtre la bdd sur le quartile de distance et on met en forme la colonne de temps (regroupement des valeurs de temps à un intervalle de temps donné)
    data_filt_dist = data_filt[(data_filt['V2_MDISTTOT'] <= Q[i+1])
                & (data_filt['V2_MDISTTOT'] > Q[i])].copy()
    data_filt_dist.loc[:, 'V2_MORIHDEP'] = pd.to_timedelta(data_filt_dist['V2_MORIHDEP'], errors='coerce')
    data_filt_dist = data_filt_dist.dropna()
    data_filt_dist.loc[:, 'V2_MORIHDEP'] = data_filt_dist['V2_MORIHDEP'].dt.round('15Min')
    data_filt_dist = data_filt_dist[data_filt_dist['V2_MORIHDEP'].dt.components.days < 1]
     #On calcule le poids total de la pondération
    poids_tot = data_filt_dist['POIDS_JOUR'].sum()

    #On regroupe les entrées avec la même heure de départ et on somme le poids de jour
    data_filt_dist_grp = data_filt_dist.groupby(by=['V2_MORIHDEP'],
                                                as_index=False)['POIDS_JOUR'].sum()

    #pg_hdep=pg.GaussianKernelDensity.from_samples(data_filt_dist_grp['V2_MORIHDEP'].dt.total_seconds()//60,weights=data_filt_dist_grp['POIDS_JOUR'])

    #On remplit ensuite le tableau de proba de l'heure de départ avec leur fréquence d'apparition
    row_iterator = data_filt_dist_grp.iterrows()
    for j, row in row_iterator:
        for x in prob_hdep[-1]:
            if row['V2_MORIHDEP'] == x[0]:
                x[1] = x[1]+row['POIDS_JOUR']
                x[1] = x[1]/poids_tot

    #On refait la même chose pour la durée
    data_dur = data_filt_dist.sort_values(by=['V2_DUREE']).round({'V2_DUREE':0})[['POIDS_JOUR', 'V2_DUREE']]
    data_dur = data_dur[data_dur['V2_DUREE'] < 200]
    data_dur.loc[:, 'V2_DUREE'] = pd.to_timedelta(data_dur['V2_DUREE'],
                unit='Min').dt.round('1Min').dt.total_seconds()//60
    data_dur = data_dur.groupby('V2_DUREE', as_index=False).count()
    pg_dist_dur = pg.GaussianKernelDensity.from_samples(
            data_dur['V2_DUREE'].values.flatten(),
            weights=data_dur['POIDS_JOUR'].values.
            flatten()/(data_dur['POIDS_JOUR'].sum()))
    theta = pg_dist_dur.parameters
    #(sigma, loc, mu_exp)= lognorm.fit(data_dur['V2_DUREE'].values.flatten(),floc=0);
    #mu=np.log(mu_exp);
    print(data_dur.size)
#    print("mu :",theta)
    #print("sigma :",sig)
    plt.plot(data_dur['V2_DUREE'].values.flatten(),
             data_dur['POIDS_JOUR'].values.flatten()/(data_dur['POIDS_JOUR'].sum())
             #,
             #data_dur['V2_DUREE'].values.flatten(),
             #pg_dist_dur.probability(data_dur['V2_DUREE'].values.flatten())
             )
    plt.show()
    
    
#vbulle pour lognormal

#modéliser proba seulement pour domicile-travail

#faire la probablité de la journée d'un individu

#conditionner la distance en fonction du nombre de trajet journalier
