# -*- coding: utf-8 -*-
"""
Created on Fri May  3 18:28:30 2019

@author: Any
"""

import pomegranate as pg
import pandas as pd
import numpy as np
from scipy.special import erfinv
import matplotlib.pyplot as plt

def probparam(dfent,typ,hdeb,hfin,mot):
    #Pourquoi pas rajouter un nom en paramètre et le dico pour ajouter au dico le modèle
    print("on va copier la df entree")
    df=dfent.copy()
    print("copie faite")

    print("on a reussi a mettre en timedeltas")
    df=df[(df['V2_MORIHDEP']<=pd.to_timedelta(hfin,unit='h')) 
        & (df['V2_MORIHDEP']>=pd.to_timedelta(hdeb,unit='h')) 
        & (np.floor(df['V2_MMOTIFDES'])==mot)
        & (df['TYPE_JOUR'] ==typ)]
    
    prob_dist = pg.LogNormalDistribution(0, 1)
    prob_dist.fit(df['V2_MDISTTOT'].values.flatten(),
            weights=df['POIDS_JOUR'].values.flatten())
    pg_mu, pg_sigma = prob_dist.parameters
    
    Q = [np.exp(pg_mu + np.sqrt(2*pg_sigma)*erfinv(2*x-1)) for x in [0.25, 0.5, 0.75]]
    Q.append(100)
    Q.insert(0, 0)
    
    prob_quartdist = []
    for i in range(0, len(Q)-1):
        df_dist = df[(df['V2_MDISTTOT'] <= Q[i+1])
                & (df['V2_MDISTTOT'] > Q[i])]
        print("attention à la copie")
        df_dur = df_dist.copy()
        print("copie nice")
        df_dur['V2_DUREE']=pd.to_timedelta(df_dur['V2_DUREE'],
                unit='Min').dt.round('1Min').dt.total_seconds()//60
        prob_dist_dur = pg.LogNormalDistribution.from_samples(
                df_dur['V2_DUREE'].values.flatten(),
                weights=df_dur['POIDS_JOUR'].values.
                flatten())
        print("oupsiii")
#        df_dur=df_dur.groupby(by=['V2_DUREE'], as_index=False)['POIDS_JOUR'].sum()
#        plt.plot(df_dur['V2_DUREE'].values.flatten(),df_dur['POIDS_JOUR'].values.flatten()/(df_dur['POIDS_JOUR'].sum()),df_dur['V2_DUREE'].values.flatten(),prob_dist_dur.probability(df_dur['V2_DUREE'].values.flatten()))
#        plt.show()
        del df_dur
        df_hdep = df_dist.copy()
        print("t'arrives à copier ?")
        df_hdep['V2_MORIHDEP']=df_hdep['V2_MORIHDEP'].dt.round('15Min')
        df_hdep=df_hdep.groupby(by=['V2_MORIHDEP'],as_index=False)['POIDS_JOUR'].sum()
        df_hdep = df_hdep.sort_values(['V2_MORIHDEP'])
        prob_dist_hdep = pg.DiscreteDistribution(dict(zip(df_hdep['V2_MORIHDEP'],df_hdep['POIDS_JOUR'].values.flatten()/(df_hdep['POIDS_JOUR'].sum()))))
        print("erreur ici")
#        prob_test = pg.GaussianKernelDensity()
#        prob_test.fit(df_dist['V2_MORIHDEP'].dt.total_seconds()/60)
#        n =plt.hist(df_dist['V2_MORIHDEP'].dt.total_seconds()/60, density = True , bins = (hfin - hdeb)*4)
#        plt.plot(n[1],prob_test.probability(n[1]))
#        plt.show()
#        print(df_dist['V2_MORIHDEP'].count())
        prob_quartdist.append((prob_dist_dur,prob_dist_hdep))
        print("ba alors on arrive pas a append")
    return (prob_dist,prob_quartdist)