# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 14:07:49 2022

@author: jstreeck
"""
import pymrio
import numpy as np
import pandas as pd
import os
import sys
import numpy as np
import pandas as pd

main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
data_path = os.path.join(main_path, 'input_data/')
exio_path = 'C:/Users/jstreeck/Desktop/EndUse_shortTermSave/Exiobase/' #insert your system path to Exiobase zip files here


year = 2000
region = 'US'
import pickle
#with open(os.path.join( 'exio3_2000'), 'wb') as handle:
#    pickle.dump(exio3, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(exio_path + 'exio3_2000','rb') as f:
        exio3 = pickle.load(f)


'''check how relation of Exiobase elements works'''
# load Y and A
Y_full = exio3.Y 
Y_full_regions = Y_full.T.groupby('region').sum().T
Y_full_sum = Y_full.sum(axis=1)
A_full = exio3.A

#re-calculate x
I = np.eye(A_full.shape[0])
L_full = np.linalg.inv(I-A_full)
x = np.dot(L_full,Y_full_regions).sum(axis=1)

#calc Z
x_diag = np.zeros_like(A_full)
np.fill_diagonal(x_diag, x)
Z = np.dot(A_full,x_diag)

## compare Z loaded from exiobase to new Z
Z_full = exio3.Z
Z.sum().sum() - Z_full.sum().sum()



'''check difference of technology A matrices between different appraoches'''
    
## 1 just take A matrix from Exiobase
A_mrio = exio3.A.xs(region,level='region',axis=1) # filter regional A matrix from MRIO
A_srio = A_mrio.groupby('sector').sum()

## 2 calculate A matrix from Z and Y in full resolution
Z_full = exio3.Z
Y_full = exio3.Y #.xs(region ,level='region',axis=1) # filter regional Y matrix from MRIO
x= Z_full.sum(axis=1) + Y_full.sum(axis=1)

x_inv_raw = np.divide(np.ones(len(x)), x.to_numpy())
x_inv = np.where(x_inv_raw == np.inf, 0, x_inv_raw)
x_inv_diag = np.zeros_like(Z_full)
np.fill_diagonal(x_inv_diag, x_inv)

A_complete = pd.DataFrame(np.dot(Z_full,x_inv_diag), index = Z_full.index, columns = Z_full.columns)
A_complete_srio = A_complete.xs(region,level='region',axis=1)
A_complete_srio_sum = A_complete_srio.groupby('sector').sum() 


## 3 calculate A matrix from Z and Y aggregated to one region
Z_mrio = exio3.Z.xs(region,level='region',axis=1) # filter regional A matrix from MRIO
Z_srio = Z_mrio.groupby('sector').sum()
Y_mrio = exio3.Y.xs(region ,level='region',axis=1) # filter regional Y matrix from MRIO
Y_srio = Y_mrio.groupby('sector').sum()

Y_only_region = Y_mrio.xs(region) 

x = Z_srio.sum(axis=1) + Y_only_region.sum(axis=1)
x_diag = np.zeros_like(Z_srio)
np.fill_diagonal(x_diag, x)
A = pd.DataFrame(np.dot(Z_srio,np.linalg.pinv(x_diag)), index = Y_only_region.index, columns = Y_only_region.index)


#check difference
A_complete_srio_sum.sum(axis=0)
A_srio.sum(axis=0)
A.sum(axis=0)
