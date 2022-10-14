# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 13:28:46 2020

@author: jstreeck
"""

import pymrio
import numpy as np
import pandas as pd
import os
import sys

main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
data_path = os.path.join(main_path, 'input_data/')
exio_path = 'C:/Users/jstreeck/Desktop/EndUse_shortTermSave/Exiobase/' #insert your system path to Exiobase zip files here

from EndUseShares_functions_v1 import end_use_transfer_exio, create_WIOMassFilter_plain, match_multiIndex,\
     calc_WIO_noYieldCorr_exio, save_to_excel


'''

  #1 LOAD DATA AND DERIVE OVERARCHING VARIABLES 

'''
### 1 - define general variables
years = list(range(1995,2012))
regions = ['AT',  'AU', 'BE', 'BG', 'BR', 'CA', 'CH', 'CN', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'ID', 'IE', 'IN', 'IT', 'JP',\
             'KR', 'LT', 'LU', 'LV', 'MT', 'MX', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE', 'SI', 'SK', 'TR', 'TW', 'US', 'WA', 'WE', 'WF', 'WL', 'WM', 'ZA']

filter_matrix = pd.read_excel(data_path + 'Filter_Exiobase_Base_v2.xlsx',index_col=[0],header=[0,1],sheet_name='mass_&_aggreg') # (mass) filter and aggregation matrix 
aggregation_matrix = filter_matrix.iloc[:,4:-2].T # select aggregation matrix from filter matrix
extension_products = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list() # the sectors that are considered for distributing material extensions

yield_filter_single = pd.read_excel(data_path + 'Filter_Exiobase_Base_v2.xlsx',index_col=[1],header=[1],sheet_name='yield').iloc[1:,1:].replace(0,1)
yield_filter_all =  pd.concat([pd.concat([yield_filter_single]*49, axis=1)]*49, axis=0)


# option to pickle EXIOBASE MIOT for single year
#year = 2000
#region = 'US'
#import pickle
#with open(os.path.join( 'exio3_2000'), 'wb') as handle:
#    pickle.dump(exio3, handle, protocol=pickle.HIGHEST_PROTOCOL)
#with open(exio_path + 'exio3_2000','rb') as f:
#       exio3 = pickle.load(f)
    
  
### 2 - derive items required for WIO-MFA filters and End-Use Transfer
# items for WIO filter
raw_materials = filter_matrix.loc[:,(['All'],['Not_stockbuilding'])]
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products = filter_matrix.loc[:,(['All'],['Products'])]
non_service = materials.to_numpy() + intermediates.to_numpy() + products.to_numpy() + raw_materials.to_numpy() 


# define transfer filter for End-Use Transfer (ones for transactions that shall be transferred from Z to Y)
filt_prod2service = pd.DataFrame(data=np.ones_like(yield_filter_single), index= yield_filter_single.index, columns=yield_filter_single.columns)
filt_prod2service = (filt_prod2service  * non_service.T).replace(1,2).replace(0,1).replace(2,0) * non_service #non-service are the items not identified as material, intermediate or product in filter_matrix; NOT as defined in aggregation column
filter_transf_single = filt_prod2service.replace(2,1)
filter_transf_all =  pd.concat([pd.concat([filter_transf_single]*49, axis=1 ,ignore_index=False)]*49, axis=0 ,ignore_index=False) 

#check if transfer filters correct (only transferring for inputs to services in this case)
filter_transf_all_dim0 = filter_transf_all.iloc[:201,:].sum(axis=0)  
filter_transf_all_dim1 = filter_transf_all.iloc[:,:201].sum(axis=1)                                                                                                                            # define transfer filter for End-Use Transfer (ones for transactions that shall be transferred from Z to Y)

#create filter matrices and repeat to match dimension of Exiobase A matrix
filt_Amp, filt_App, filt_Amp_label_single, filt_App_label_single = create_WIOMassFilter_plain(filter_transf_single,raw_materials, materials,products,intermediates, non_service)
filt_Amp_label_all = pd.concat([pd.concat([filt_Amp_label_single]*49, axis=1 ,ignore_index=False)]*49, axis=0 ,ignore_index=False) 
filt_App_label_all = pd.concat([pd.concat([filt_App_label_single]*49, axis=1 ,ignore_index=False)]*49, axis=0 ,ignore_index=False) 


'''

  #2 CALCULATE D_EUT_WIO per region/country and year (and save as Excel)

'''            

# loop over years to conduct end-use transfer, afterwards loop over regions to calculate D_WIO per region and year                                                                                
for year in years:
    exio3 = pymrio.parse_exiobase3(path = exio_path + 'IOT_' + str(year) +'_pxp.zip')
    
    # load Y, drop three Y elements (CII,CIV,exports) and sum per region, remove negatives from Z, Y and replace with 0
    Y_full = exio3.Y 
    Y_full_dom = Y_full.drop(['Changes in inventories', 'Changes in valuables','Exports: Total (fob)'], level = 'category',axis=1) #only keep items for domestic use for indicated year
    Y_full_regions = Y_full_dom.T.groupby('region').sum().T
    Y_full_regions.clip(lower=0, inplace=True) #remove negative values
    
    A_full = exio3.A
    A_full.clip(lower=0, inplace=True) #remove negative value
    
    #re-calculate x with changed Y, then Z
    I = np.eye(A_full.shape[0])
    L_full = np.linalg.inv(I-A_full)
    x = np.dot(L_full,Y_full_regions).sum(axis=1)

    #calc Z
    x_diag = np.zeros_like(A_full)
    np.fill_diagonal(x_diag, x)
    Z_full = pd.DataFrame(np.dot(A_full,x_diag), index = A_full.index, columns = A_full.columns)
   
    #check for negatives in Z_full and compare to original Z from exiobase
    (Z_full < 0).any().any()
    exio3.Z.sum().sum() - Z_full.sum().sum()

    
    #align index of filters to Z/Y
    yield_filter = match_multiIndex(yield_filter_all, Z_full)
    filter_transf = match_multiIndex(filter_transf_all, Z_full)
    filt_Amp_label = match_multiIndex(filt_Amp_label_all, filter_transf)
    filt_App_label = match_multiIndex(filt_App_label_all, filter_transf)

    # calculate end-use transfer
    Y_transferred, Z_transferred, A_eut = end_use_transfer_exio(Z_full, Y_full_regions, filter_transf, yield_filter)
      
    for region in regions:
        
        # select Y specific for single region
        Y_region = Y_transferred.xs(region,axis=1)
        
        # with A_eut (= region-specific technology matrix)
        D_eut_wio_region, D_eut_wio_region_aggregated, EUTWIO_split_region, check_wio_eut_region = calc_WIO_noYieldCorr_exio(A_eut, Y_region , filt_Amp_label , filt_App_label , filter_matrix, aggregation_matrix, extension_products)

        # save
        fileName_EUTWIOMF= 'Exiobase/Exio_EUT_WIOMF_' + str(year) + '_' + region
        save_to_excel(fileName_EUTWIOMF,D=D_eut_wio_region,D_aggregated=D_eut_wio_region_aggregated,total_split = EUTWIO_split_region, \
                      massFilterName=filter_matrix, filter_transf= filter_transf_single, yieldFilterName=yield_filter_single,\
                      filt_Amp=filt_Amp_label_single, filt_App=filt_App_label_single, check = check_wio_eut_region)
                        
        del Y_region, D_eut_wio_region, D_eut_wio_region_aggregated, EUTWIO_split_region, check_wio_eut_region, fileName_EUTWIOMF
            
    del exio3, Y_full, Y_full_dom, Y_full_regions, A_full, I, L_full, x, x_diag, Z_full, yield_filter, filter_transf,\
        filt_Amp_label, filt_App_label, Y_transferred, Z_transferred, A_eut


