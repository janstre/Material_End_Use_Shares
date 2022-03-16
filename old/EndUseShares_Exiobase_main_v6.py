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
import numpy as np
import pandas as pd

main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
data_path = os.path.join(main_path, 'input_data/')
exio_path = 'C:/Users/jstreeck/Desktop/EndUse_shortTermSave/Exiobase/' #insert your system path to Exiobase zip files here

from EndUseShares_functions_v4 import hypothetical_transfer_exio, calc_WIO_noYieldCorr_exio, hypothetical_transfer, calc_WIO_noYieldCorr, \
     save_to_excel, create_WIOMassFilter_plain, create_WIOMassFilter_withServiceRawMatInput, calc_CBA, match_multiIndex


'''

  #1 LOAD DATA AND DERIVE OVERARCHING VARIABLES 

'''
### 1 - general variables
years = list(range(1995,2012))
regions = ['AT',  'AU', 'BE', 'BG', 'BR', 'CA', 'CH', 'CN', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'ID', 'IE', 'IN', 'IT', 'JP',\
           'KR', 'LT', 'LU', 'LV', 'MT', 'MX', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE', 'SI', 'SK', 'TR', 'TW', 'US', 'WA', 'WE', 'WF', 'WL', 'WM', 'ZA']

filter_matrix = pd.read_excel(data_path + 'Filter_Exiobase_Base_v2.xlsx',index_col=[0],header=[0,1],sheet_name='mass_&_aggreg') # (mass) filter and aggregation matrix 
aggregation_matrix = filter_matrix.iloc[:,4:-2].T # select aggregation matrix from filter matrix
extension_products = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list() # the sectors that are considered for distributing material extensions

yield_filter_single = pd.read_excel(data_path + 'Filter_Exiobase_Base_v2.xlsx',index_col=[1],header=[1],sheet_name='yield').iloc[1:,1:].replace(0,1)
yield_filter_all =  pd.concat([pd.concat([yield_filter_single]*49, axis=1)]*49, axis=0)


year = 2000
region = 'US'
import pickle
#with open(os.path.join( 'exio3_2000'), 'wb') as handle:
#    pickle.dump(exio3, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(exio_path + 'exio3_2000','rb') as f:
        exio3 = pickle.load(f)


'''## neeed to make sure that the sequence of sectors is correct?'''
      
  
### 2 - derive items required for WIO-MFA filters and Hypothetical Transfer
# items for WIO filter
raw_materials = filter_matrix.loc[:,(['All'],['Not_stockbuilding'])]
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products = filter_matrix.loc[:,(['All'],['Products'])]
non_service = materials.to_numpy() + intermediates.to_numpy() + products.to_numpy() + raw_materials.to_numpy() 


# define transfer filter for Hypothetical Transfer (ones for transactions that shall be transferred from Z to Y)
filt_prod2service = pd.DataFrame(data=np.ones_like(yield_filter_single), index= yield_filter_single.index, columns=yield_filter_single.columns)
filt_prod2service = (filt_prod2service  * non_service.T).replace(1,2).replace(0,1).replace(2,0) * non_service #non-service are the items not identified as material, intermediate or product in filter_matrix; NOT as defined in aggregation column
filter_transf_single = filt_prod2service.replace(2,1)
filter_transf_all =  pd.concat([pd.concat([filter_transf_single]*49, axis=1 ,ignore_index=False)]*49, axis=0 ,ignore_index=False) 


#check if transfer filters correct (only transferring for inputs to services in this case)
filter_transf_all_dim0 = filter_transf_all.iloc[:201,:].sum(axis=0)  
filter_transf_all_dim1 = filter_transf_all.iloc[:,:201].sum(axis=1)                                                                                                                            # define transfer filter for Hypothetical Transfer (ones for transactions that shall be transferred from Z to Y)


#create filter matrices and repeat to match dimension of Exiobase A matrix
filt_Amp, filt_App, filt_Amp_label, filt_App_label = create_WIOMassFilter_plain(filter_transf_single,raw_materials, materials,products,intermediates, non_service)
filt_Amp_label_all = pd.concat([pd.concat([filt_Amp_label]*49, axis=1 ,ignore_index=False)]*49, axis=0 ,ignore_index=False) 
filt_App_label_all = pd.concat([pd.concat([filt_App_label]*49, axis=1 ,ignore_index=False)]*49, axis=0 ,ignore_index=False) 

###--> again check if these are correct
                 

                  
# loop over years to conduct hypothetical transfer, afterwards loop over regions to calculate D per region and year                                                                                
for year in years:
    exio3 = pymrio.parse_exiobase3(path= exio_path + str(year) +'_pxp.zip')
    
    # load Y, drop three Y elements and sum per region, remove negatives from Z, Y and replace with 0
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
    (Z_full < 0).any().any()
    #compare to original Z from exiobase
    exio3.Z.sum().sum() - Z_full.sum().sum()

    
    #align index of filters to Z/Y
    yield_filter_all = match_multiIndex(yield_filter_all, Z_full)
    filter_transf_all = match_multiIndex(filter_transf_all, Z_full)
    filt_Amp_label_all = match_multiIndex(filt_Amp_label_all, filter_transf_all)
    filt_App_label_all = match_multiIndex(filt_App_label_all, filter_transf_all)
    
    # calculate hypothetical transfer
    Y_transferred, Z_transferred, A_ht = hypothetical_transfer_exio(Z_full, Y_full_regions, filter_transf_all, yield_filter_all)
    

    ##next: 
      #-->check if A_ht from this is equivalent to calculating for one region with domestic tech fron loop above    
    for region in regions:
        Y_region = Y_transferred.xs(region,axis=1)
        #A_ht_srio = A_ht.groupby('sector').sum()
        
        D_wio_region,D_wio_region_aggregated,WIO_split_region,check_wio_region = calc_WIO_noYieldCorr_exio(A_ht, Y_region , filt_Amp_label_all , filt_App_label_all , filter_matrix, aggregation_matrix, extension_products)


        ##define filter matrices --> already done above
        
        '''transfer to own function calc_WIO_noYield'''
        ####calc_WIO_noYieldCorr --> needs to be adjusted
        # filter technology matrix A according to WIO-MFA mass filters and partition into Amp (materials --> products), App (products --> products)
        Amp_filt = A_ht * filt_Amp_label_all 
        App_filt = A_ht * filt_App_label_all                  
        
        # calculate material composition matrix C from Amp, App
        I = np.eye(A_ht.shape[0])
        C = np.dot(Amp_filt,np.linalg.inv(I-App_filt))
        C_label = pd.DataFrame(data = (C), index = A_ht.index, columns = A_ht.index)
        C_label_srio = C_label.groupby('sector').sum()
        
        # calculate the absolute material deliveries to final demand (C*diag(Y))
        Y_diag = np.zeros_like(C_label)
        np.fill_diagonal(Y_diag, Y_region)
        WIO_split_raw = pd.DataFrame(np.dot(C_label_srio,Y_diag),index=C_label_srio.index, columns=C_label_srio.columns)
        WIO_split_raw_srio = WIO_split_raw.T.groupby('sector').sum().T
        
        # filter for materials of interest (extension_products) and calculate end-use share matrix D_wio by dividing WIO_split_raw by row-sum
        WIO_split = WIO_split_raw_srio.loc[extension_products]
        D_wio = WIO_split.divide(WIO_split.sum(axis=1),axis=0).transpose()*100
            
        # aggregate to product-groups specified in aggregation_matrix
        D_wio_aggregated = aggregation_matrix.dot(D_wio)
        check_wio = D_wio_aggregated.sum(axis=0) # check if all shares sum up to 100%
        
    


    Z_yield = Z_full * yield_filter_all
    waste = Z_full - Z_yield
    # apply the pre-definied transfer filter to Z and Y, indicating the values that shall be transferred from Z to Y
    Z_transfer = Z_yield * filter_transf_all
    Z_transfer =  Z_transfer.T.groupby('region').sum().T
    Y_transferred = Y_full_regions + Z_transfer
    Z_transferred = Z_yield * filter_transf_all.replace(1,2).replace(0,1).replace(2,0).to_numpy() #delete transferred items in Z_yield
    
    #check if transferred item sum equal to original
    Y_transferred.sum().sum() + Z_transferred.sum().sum() + waste.sum().sum() -  x.sum().sum()
    #--> alter so that it throws wARNING when not close to 0
    
    # calculate new A; use original x as it does not change by transfer
    
    
    x_inv_raw = np.divide(np.ones(len(x)), x.to_numpy())
    x_inv = np.where(x_inv_raw == np.inf, 0, x_inv_raw)
    x_inv_diag = np.zeros_like(Z_full)
    np.fill_diagonal(x_inv_diag, x_inv )
    
    A_ht = pd.DataFrame(np.dot(Z_transferred,x_inv_diag), index = Y_full.index, columns = Y_full.index)
    

    #Z_sector = Z_full.groupby('sector').sum()
    .reindex(sector_order) 
    #I_full = np.eye(Z_full.shape[0])
    #L_full = np.linalg.inv((I_full -A_full ))
    #L_full_label = pd.DataFrame(data = L_full, index = Z_full.index, columns = Z_full.columns)
    #A_sector = A.groupby('sector').sum().reindex(sector_order) 
    #A_sector_region = A_sector.xs(region,level='region',axis=1)

    #L_full_sector = L_full_label.groupby('sector').sum().reindex(sector_order) 
    #L_full_sector_region = L_full_sector.xs(region,level='region',axis=1)


    #Y_full_region = Y_full_regions.T.xs(region,axis=0).T

    Y_full_regions_diag = np.multiply(np.eye(200),Y_full_regions[:,np.newaxis])

    Y_full_region_diag = np.zeros_like(A_full)
    np.fill_diagonal(Y_full_region_diag, Y_full_region)
    

    ##--> one line has to be changed in function
    #-->     Z_transfer = pd.DataFrame(data = Z_transfer.sum(axis=1), columns = Y.columns), needs to be a groupby
    #          not a sum()
    
    
    for region in regions: 
        
        


D = np.dot(L_full_sector.to_numpy(),Y_full_region_diag)
D_label = pd.DataFrame(D, index = L_full_sector.index, columns = Y_full_region.index)
D_label_region = D_label.T.groupby('sector').sum().reindex(sector_order) 
D_label_region_shares = D_label_region.divide(D_label_region.sum(axis=0),axis=1)*100

D_label = pd.DataFrame(D, index = L_full_sector.index, columns = Y_full_regions.columns)
D_label_shares = D_label.divide(D_label.sum(axis=0),axis=1)*100

# filter for materials of interest (extension_products) and calculate end-use share matrix D_CBA by dividing CBA_split_raw by row-sum
D_label_region_shares_ext = D_label_region_shares.T.loc[extension_products].replace(np.nan,0)
D_label_region_shares_ext_agg =  aggregation_matrix.dot(D_label_region_shares_ext.T)

D_cba = CBA_split.divide(CBA_split.sum(axis=1),axis=0).transpose()*100

    # aggregate to product-groups specified in aggregation_matrix
    D_cba_aggregated = aggregation_matrix.dot(D_cba)
    check_cba = D_cba_aggregated.sum(axis=0) # che


'''idea: no need of any loops:
 - use full Z matrix, duplicate yield filter to 9800(regions, sectors) x 9800(regions, sectors) and substract
 - transfer Z matrix elements in HT method to 9800 (regions, sectors) x 49 regions
 - from full Y matrix, kick exports inventory changes, etc and group per regions so that one demand vector per region
   in form 9800(regions, sectors) x 49 regions
 - use the HT vector from step 2 and add to Y matrix in shape 9800 x 49
 - delete transferred elements in fill Z matrix 9800 x 9800
 - calculate x in 9800 x 49
 - from Z_transferred, calculate A_ht (Z_transferred*inv(x))
 - duplicate WIO mass filter to 9800 x 9800 and apply to A to get Amp, App
 - calculate C
 - aggregate C to 200 sectors x 9800 (regions, sectors)
 - diagonalize Y to 9800 x 9800 (so that C x diagY gives absolute end-use distribution)
 - calc aggregate C (200x9800) x diagY (9800x9800) = D_WIO_abs 200x9800
 - group D_WIO_abs by region and calculate shares
 '''

#D = np.dot(L_full_sector.to_numpy(),Y_full_regions.to_numpy())
#D_label = pd.DataFrame(D, index = L_full_sector.index, columns = Y_full_regions.columns)
#D_label_shares = D_label.divide(D_label.sum(axis=0),axis=1)*100

#before alteration  A-->Z
# A_full = exio3.A
# I_full = np.eye(A_full.shape[0])
# L_full = np.linalg.inv((I_full -A_full ))
# L_full_label = pd.DataFrame(data = L_full, index = A_full.index, columns = A_full.columns)
# #A_sector = A.groupby('sector').sum().reindex(sector_order) 
# #A_sector_region = A_sector.xs(region,level='region',axis=1)

# L_full_sector = L_full_label.groupby('sector').sum().reindex(sector_order) 
# L_full_sector_region = L_full_sector.xs(region,level='region',axis=1)

# Y_full = exio3.Y #.xs(region ,level='region',axis=1) # filter regional Y matrix from MRIO
# Y_full_dom = Y_full.drop(['Changes in inventories', 'Changes in valuables','Exports: Total (fob)'], level = 'category',axis=1) #only keep items for domestic use for indicated year
# Y_full_regions = Y_full_dom.T.groupby('region').sum()
# Y_full_region = Y_full_regions.T.xs(region,axis=0).T

# Y_full_region_diag = np.zeros_like(A_full)
# np.fill_diagonal(Y_full_region_diag, Y_full_region)

# D = np.dot(L_full_sector.to_numpy(),Y_full_region_diag)
# D_label = pd.DataFrame(D, index = L_full_sector.index, columns = Y_full_region.index)
# D_label_region = D_label.T.groupby('sector').sum().reindex(sector_order) 
# D_label_region_shares = D_label_region.divide(D_label_region.sum(axis=0),axis=1)*100

# D_label = pd.DataFrame(D, index = L_full_sector.index, columns = Y_full_regions.columns)
# D_label_shares = D_label.divide(D_label.sum(axis=0),axis=1)*100

# # filter for materials of interest (extension_products) and calculate end-use share matrix D_CBA by dividing CBA_split_raw by row-sum
# D_label_region_shares_ext = D_label_region_shares.T.loc[extension_products].replace(np.nan,0)
# D_label_region_shares_ext_agg =  aggregation_matrix.dot(D_label_region_shares_ext.T)

# D_cba = CBA_split.divide(CBA_split.sum(axis=1),axis=0).transpose()*100

yield_filter = pd.read_excel(data_path + 'Filter_Exiobase_Base_v2.xlsx',index_col=[1],header=[1],sheet_name='yield').iloc[1:,1:].replace(0,1)

def exio_domestic_techn():
    for year in years:
        exio3 = pymrio.parse_exiobase3(path= exio_path + 'IOT_str' + (year) +'_pxp.zip')
        for region in regions:
            
            ### 1 - derive basic MIOT items
            # retrieve regional A matrix with positive values only
            A_mrio = exio3.A.xs(region,level='region',axis=1) # filter regional A matrix from MRIO
            sector_order = A_mrio.columns.to_list()
            A_srio = A_mrio.groupby('sector').sum().reindex(sector_order) 
            
            # remove negative values from A matrix
            A_srio_pos = np.where(A_srio<0,0,A_srio) #use clip instead
            
            
            ### 1 - derive basic MIOT items
            # retrieve regional A matrix with positive values only
            Z_mrio = exio3.Z.xs(region,level='region',axis=1) # filter regional A matrix from MRIO
            sector_order = Z_mrio.columns.to_list()
            Z_srio = Z_mrio.groupby('sector').sum().reindex(sector_order) 

            
            # remove negative values from A matrix
            Z_srio_pos = Z_srio.clip(lower=0) #remove negative values
            
            
            # retrieve domestic final demand Y with positive values only
            Y_mrio = exio3.Y.xs(region ,level='region',axis=1) # filter regional Y matrix from MRIO
            Y_srio = Y_mrio.groupby('sector').sum().reindex(sector_order)
            Y_srio_dom = Y_srio.drop(['Changes in inventories', 'Changes in valuables','Exports: Total (fob)'],axis=1) #only keep items for domestic use for indicated year
            Y_srio_dom_sum = Y_srio_dom.sum(axis=1)
            Y_srio_dom_sum_pos = np.where(Y_srio_dom_sum<0,0,Y_srio_dom_sum)
            
            # from A and Y derive Z
            I = np.eye(A_srio.shape[0])
            L = np.linalg.inv((I-A_srio_pos))
            x = np.dot(L,Y_srio_dom_sum) 
            x_diag  = np.zeros_like(L)
            np.fill_diagonal(x_diag, x)
            #Z = pd.DataFrame(data = np.dot(A_srio_pos,x_diag), index = A_srio.index, columns = A_srio.columns)
            A = pd.DataFrame(data = A_srio_pos, index = A_srio.index, columns = A_srio.columns) #define as A
            Y = pd.DataFrame(data =  Y_srio_dom_sum , index = A_srio.index) #define as Z
            
            #D_cba, D_cba_aggregated, CBA_split, check_cba = calc_CBA(L, Y, filter_matrix, aggregation_matrix, extension_products)
            
            ### 2 - derive items required for WIO-MFA filters and Hypothetical Transfer
            # items for WIO filter
            raw_materials = filter_matrix.loc[:,(['All'],['Not_stockbuilding'])]
            materials  = filter_matrix.loc[:,(['All'],['Materials'])]
            intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
            products = filter_matrix.loc[:,(['All'],['Products'])]
            non_service = materials.to_numpy() + intermediates.to_numpy() + products.to_numpy() + raw_materials.to_numpy() 
            
            # define transfer filter for Hypothetical Transfer (ones for transactions that shall be transferred from Z to Y)
            filt_prod2service = pd.DataFrame(data=np.ones_like(A), index= A.index, columns=A.columns)
            filt_prod2service = (filt_prod2service  * non_service.T).replace(1,2).replace(0,1).replace(2,0) * non_service #non-service are the items not identified as material, intermediate or product in filter_matrix; NOT as defined in aggregation column
            filter_transf = filt_prod2service.replace(2,1)
            
            ### 3 - implement Hypothetical Transfer (HT) and WIO-MFA (yield correction in HT, not WIO-MFA for this ombination)
            Y_transferred, Z_transferred, A_ht = hypothetical_transfer(Z_srio_pos, Y, A, x, filter_transf, yield_filter)
           ## Y_transferred, Z_transferred, A_ht = hypothetical_transfer(Z, Y, A, x, filter_transf, yield_filter)
            filt_Amp, filt_App, filt_Amp_label, filt_App_label = create_WIOMassFilter_plain(A_ht ,raw_materials, materials, products, intermediates, non_service)    
            D_ht_WIO, D_ht_WIO_aggregated, HT_WIO_split, check_ht_WIO  = calc_WIO_noYieldCorr(A_ht, Y_transferred, filt_Amp, filt_App, filter_matrix, aggregation_matrix, extension_products)
            
            ### 4 - save results
            fileNameHT_WIOMF = 'Exio_HT_WIOMF_' + str(year) + '_' + region 
            save_to_excel(fileNameHT_WIOMF,D=D_ht_WIO,D_aggregated=D_ht_WIO_aggregated,total_split = HT_WIO_split, \
                          massFilterName=filter_matrix,   Ztransferred=pd.DataFrame(), Ytransferred=pd.DataFrame(), 
                          filter_transf=filter_transf, check = check_ht_WIO)
            
            ### 5 - delete variables for year and region before next loop iteration
            del fileNameHT_WIOMF ,  D_ht_WIO, D_ht_WIO_aggregated, HT_WIO_split, check_ht_WIO, filt_Amp, filt_App, filt_Amp_label, filt_App_label, \
                Y_transferred, Z_transferred, A_ht, filter_transf, filt_prod2service, raw_materials, materials, products, intermediates, non_service, \
                Z, Y, A, x, yield_filter, x_diag, L, I, Y_srio_dom_sum_pos, Y_srio_dom_sum, Y_srio_dom, Y_srio, A_srio_pos, A_srio, sector_order, A_mrio,\
                region, year, exio3
                
                
    zala = Z_transferred.groupby('sector').sum().T.groupby('region').sum().T
    zalla = Y_transferred.groupby('sector').sum()
    waste = (Z_full - (Z_full * yield_filter_all)).groupby('sector').sum().T.groupby('region').sum().T
    rala = Z_full.groupby('sector').sum().T.groupby('region').sum().T
    ralla = Y_full_regions.groupby('sector').sum()
    
    zara = zalla + zala + waste - ( rala + ralla) 
    lala = zara.max()
    
    
    

