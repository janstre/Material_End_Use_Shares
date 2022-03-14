# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 08:53:52 2020

@author: jstreeck
"""


import numpy as np
import pandas as pd


'''
# APPLICATION OF METHODS TO DERIVE END-USE SHARES



  # 1) WASTE INPUT OUTPUT APPROACH TO MATERIAL FLOW ANALYSIS
'''

# create mass filter matrices plain: removal of outputs of service sectors + inputs of raw material and service sectors (for classifiction of raw materials & services see filter_matrix in main)
def create_WIOMassFilter_plain(A, raw_materials, materials, products, intermediates, non_service):
    
    # from mass filter settings create mass filter matrix filt_Amp (ɸ_Mass) for materials going to products
    filt_Amp = np.ones_like(A)
    filt_Amp = filt_Amp * materials.to_numpy() #only transactions of material products remain
    filt_Amp = (filt_Amp.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T #set inputs of raw materials to zero; e.g. sawmills --> logging (as specified in filter)
    filt_Amp = (filt_Amp.T * non_service).T
    np.fill_diagonal(filt_Amp, 0) #set material-material transactions to zero
    filt_Amp_label = pd.DataFrame(data=filt_Amp, index= A.index, columns=A.columns) #assign labels
    
    # from mass filter settings create mass filter matrix filt_App (ɸ_Mass) for products going to products
    filt_App = np.ones_like(A)
    filt_App = filt_App  * (products.to_numpy() + intermediates.to_numpy())
    filt_App = (filt_App.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T #set inputs of raw materials to zero; e.g. sawmills --> logging (as specified in filter)
    filt_App = (filt_App.T * (np.ones_like(materials) - materials.to_numpy())).T #set product->material transactions to zero
    filt_App = (filt_App.T * (np.ones_like(intermediates) - intermediates.to_numpy())).T #set product->intermediate transactions to zero e.g. sawmills --> paper mills (as specified in filter)
    filt_App = (filt_App.T * non_service).T #sets inputs of service products to zero 
    filt_App_label = pd.DataFrame(data=filt_App, index= A.index, columns=A.columns) #assign labels

    return filt_Amp, filt_App, filt_Amp_label, filt_App_label


# create mass filter matrices withServiceRawMatInput: removal of outputs of service sectors BUT keeping inputs of raw material and service sectors (for classifiction of raw materials & services see filter_matrix in main)
def create_WIOMassFilter_withServiceRawMatInput(A, raw_materials, materials, products, intermediates, non_service):
    
    # from filter settings create mass filter matrix filt_Amp (ɸ_Mass) for materials going to products
    filt_Amp = np.ones_like(A)
    filt_Amp = filt_Amp * materials.to_numpy() #only transactions of material products remain
    np.fill_diagonal(filt_Amp, 0) #set material-material transactions to zero
    filt_Amp_label = pd.DataFrame(data=filt_Amp, index= A.index, columns=A.columns) #assign labels
    
    # from filter settings create mass filter matrix filt_App (ɸ_Mass) for products going to products
    filt_App = np.ones_like(A)
    filt_App = filt_App  * (products.to_numpy() + intermediates.to_numpy())
    filt_App = (filt_App.T * (np.ones_like(materials) - materials.to_numpy())).T #set product->material transactions to zero
    filt_App = (filt_App.T * (np.ones_like(intermediates) - intermediates.to_numpy())).T #set product->intermediate transactions to zero e.g. sawmills --> paper mills (as specified in filter)
    filt_App_label = pd.DataFrame(data=filt_App, index= A.index, columns=A.columns) #assign labels

    return filt_Amp, filt_App, filt_Amp_label, filt_App_label


# calculate WIO-MFA end-use share matrix D_wio using mass filter matrices defined in prior functions (equ. 1-3 in Streeck et al. 2022, part I)
def calc_WIO(A, Y, yield_filter, filt_Amp, filt_App, filter_matrix, aggregation_matrix, extension_products):

    # filter technology matrix A according to WIO-MFA mass and yield filters and partition into Amp (materials --> products), App (products --> products)
    Amp_filt = A * filt_Amp * yield_filter
    App_filt = A * filt_App * yield_filter                    
    
    # calculate material composition matrix C from Amp, App
    I = np.eye(A.shape[0])
    C = np.dot(Amp_filt,np.linalg.inv(I-App_filt))
    #C_label = pd.DataFrame(data = (C), index = A.index, columns = A.index)

    # calculate the absolute material deliveries to final demand (C*diag(Y))
    Y_diag = np.zeros_like(A)
    np.fill_diagonal(Y_diag, Y)
    WIO_split_raw = pd.DataFrame(np.dot(C,Y_diag),index=A.index, columns=A.columns)
        
    # filter for materials of interest (extension_products) and calculate end-use share matrix D_wio by dividing WIO_split_raw by row-sum
    WIO_split = WIO_split_raw.loc[extension_products]
    D_wio = WIO_split.divide(WIO_split.sum(axis=1),axis=0).transpose()*100
        
    # aggregate to product-groups specified in aggregation_matrix
    D_wio_aggregated = aggregation_matrix.dot(D_wio)
    check_wio = D_wio_aggregated.sum(axis=0) # check if all shares sum up to 100%
    
    return D_wio, D_wio_aggregated, WIO_split, check_wio



'''
  # 2) CONSUMPTION BASED APPROACH (CBA)
'''

# calculate consumption-based (CBA) end-use share matrix D_cba (equ. 6 in Streeck et al. 2022, part I)
def calc_CBA(L, Y, filter_matrix, aggregation_matrix, extension_products):

    # diagonalize Y and multiply L*Y to obtain absolute deliveries to final demand CBA_split_raw
    Y_diag = np.zeros_like(L)
    np.fill_diagonal(Y_diag, Y)
    CBA_split_raw = pd.DataFrame(np.dot(L,Y_diag),index=L.index, columns=L.columns)

    # filter for materials of interest (extension_products) and calculate end-use share matrix D_CBA by dividing CBA_split_raw by row-sum
    CBA_split = CBA_split_raw.loc[extension_products]
    D_cba = CBA_split.divide(CBA_split.sum(axis=1),axis=0).transpose()*100

    # aggregate to product-groups specified in aggregation_matrix
    D_cba_aggregated = aggregation_matrix.dot(D_cba)
    check_cba = D_cba_aggregated.sum(axis=0) # check if all shares sum up to 100%
    
    return D_cba, D_cba_aggregated, CBA_split, check_cba 



''' 
3) GHOSH-IO ABSORBING MARKOV CHAINS (Ghosh-IO AMC)
'''

# create mass filter matrices plain: no transactions from products --> materials, final demand of materials == 0 (for classifiction of raw materials & services see filter_matrix in main)
def create_GhoshIoAmcMassFilter_plain(Z, Y, materials, non_service):     
    
    # from mass filter settings create mass filter matrix
    filt_Ghosh_Z = (np.ones_like(Z).T * (np.ones_like(materials) - materials.to_numpy())).T #set transactions from products to materials to zero
    filt_Ghosh_Y = (np.ones_like(Y) * (np.ones_like(materials) - materials.to_numpy())) #set final demand of materials to zero
    filt_Ghosh_Z_label = pd.DataFrame(filt_Ghosh_Z,index=Z.index, columns=Z.columns)
    filt_Ghosh_Y_label = pd.DataFrame(filt_Ghosh_Y,index=Z.index)
    
    return filt_Ghosh_Z,filt_Ghosh_Y, filt_Ghosh_Z_label, filt_Ghosh_Y_label


# create mass filter matrices delServiceOutput: no transactions from products --> materials, final demand of materials == 0, outputs of service sectors == 0 (for classifiction of raw materials & services see filter_matrix in main)
def create_GhoshIoAmcMassFilter_delServiceOutput(Z, Y, materials, non_service):   
    
    # from mass filter settings create mass filter matrix
    filt_Ghosh_Z = (np.ones_like(Z).T * (np.ones_like(materials) - materials.to_numpy())).T #set transactions from products to materials to zero
    filt_Ghosh_Z = (filt_Ghosh_Z * non_service) # set outputs of service products to zero 
    filt_Ghosh_Y = (np.ones_like(Y) * (np.ones_like(materials) - materials.to_numpy())) #set final demand of materials to zero
    filt_Ghosh_Z_label = pd.DataFrame(filt_Ghosh_Z,index=Z.index, columns=Z.columns)
    filt_Ghosh_Y_label = pd.DataFrame(filt_Ghosh_Y,index=Z.index)
    
    return filt_Ghosh_Z,filt_Ghosh_Y, filt_Ghosh_Z_label, filt_Ghosh_Y_label


# create mass filter matrices delServiceOutput: no transactions from products --> materials, final demand of materials == 0, in/outputs of raw material and service sectors == 0 (for classifiction of raw materials & services see filter_matrix in main)
def create_GhoshIoAmcMassFilter_delServiceRawMat(Z, Y, raw_materials, materials, non_service):   
    
    # from mass filter settings create mass filter matrix
    filt_Ghosh_Z = (np.ones_like(Z).T * (np.ones_like(materials) - materials.to_numpy())).T #set transactions from products to materials to zero
    filt_Ghosh_Z = ((filt_Ghosh_Z * non_service).T * non_service).T # set in/outputs of service products to zero (only removing outputs leads to mass loss, as service products not absorbing)
    filt_Ghosh_Z = (filt_Ghosh_Z.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T* (np.ones_like(raw_materials) - raw_materials.to_numpy()) #set in/outputs of raw material products to zero
    filt_Ghosh_Y = (np.ones_like(Y) * (np.ones_like(materials) - materials.to_numpy())) #set final demand of materials to zero
    filt_Ghosh_Z_label = pd.DataFrame(filt_Ghosh_Z,index=Z.index, columns=Z.columns)
    filt_Ghosh_Y_label = pd.DataFrame(filt_Ghosh_Y,index=Z.index)
    
    return filt_Ghosh_Z,filt_Ghosh_Y, filt_Ghosh_Z_label, filt_Ghosh_Y_label


# calculate Ghosh-IO AMC end-use share matrix D_Ghosh (equ. 7-9 in Streeck et al. 2022, part I; slightly different conduct)
def calc_GhoshIO_AMC(Z, Y, x, filter_matrix, filt_Ghosh_Z, filt_Ghosh_Y, aggregation_matrix, extension_products):       
    
    
    # apply pre-defined mass filter matrices to transaction matrix Z and final demand Y
    Z_filt = Z.copy() * filt_Ghosh_Z
    Y_filt = Y.copy() * filt_Ghosh_Y
    
    #check if there is sector output (rows) which are zero both in interindustry Z and final demand Y
      # in that case, a quasi-absorbing state that does not supply materials or products downstream to neither industries nor final demand exists,
      # and thus leads to 'vanishing' of material/product mass or value in the Ghosh-IO AMC, which introduces errors to calculations
      # --> these sectors are removed from rows and columns of Z_filt and Y_filt here
    check_zeros = Z_filt.sum(axis=1) + Y_filt.sum(axis=1)
    indices_zero = check_zeros[check_zeros == 0].index
    Z_filt_drop = Z_filt.drop(indices_zero, axis=0).T.drop(indices_zero, axis=0).T
    Y_filt_drop = Y_filt.drop(indices_zero, axis=0)
    
    # recalculate total sector output with filtered matrices and check if smaller than original x
    x_Ghosh = Z_filt_drop.sum(axis=1) + Y_filt_drop.sum(axis=1)
    if x.sum() > x_Ghosh.sum():
        print('sum of x_Ghosh is smaller than sum of initital x')
    
    # calculate output coefficient matrix Q and final-demand absorbing vector R, and check if Q + R = 1
    Q = Z_filt_drop.divide(x_Ghosh.values,axis=0).replace(np.nan,0.0)
    Q = Q.replace(np.inf,0)
    R = Y_filt_drop.divide(x_Ghosh.values,axis=0).replace(np.nan,0.0)
    R_diag = np.zeros_like(Z_filt_drop)
    np.fill_diagonal(R_diag, R)
    QR_check_unity = Q.sum(axis=1) + R.sum(axis=1) # all entries must be one (except 0 for empty rows and deleted by filter_matrix)
    
    # calculate supply chain distribution Ghosh-type matrix G by calculating inverse of I-Q
    I = np.eye(Q.shape[0])
    G = np.linalg.inv(I - Q)
     
    # calculate distribution of materials and products to absorbing states = end-use share matrix D_Ghosh_raw
    D_Ghosh_raw = np.dot(G,R_diag)*100
    D_Ghosh_raw_label = pd.DataFrame(D_Ghosh_raw,index=Z_filt_drop.index, columns=Z_filt_drop.columns)
    
    # filter for only materials of interest (extension_products) to obtain end-use share matrix D_Ghosh
    D_Ghosh = D_Ghosh_raw_label.loc[extension_products]
    
    # aggregate to product-groups specified in aggregation_matrix
    aggregation_matrix_ghosh = aggregation_matrix.copy()
    aggregation_matrix_ghosh.drop(indices_zero, axis=1, inplace=True) #drop the rows/columns that were removed in second calc step above
    D_Ghosh_aggregated = aggregation_matrix_ghosh.dot(D_Ghosh.T) 
    check_Ghosh = D_Ghosh_aggregated.sum(axis=0) #check if all shares sum up to 100%

    return D_Ghosh,D_Ghosh_aggregated, QR_check_unity, check_Ghosh 

    

'''
  # 4) PARTIAL GHOSH-IO
'''

# create filter matrices plain: define intermediate (materials, intermediates, products_p1) and end-use products (products_p2), (for classifiction of raw materials & services see filter_matrix in main)
def create_PartialGhoshIO_filter_plain(Z, materials, intermediates, products_p1):
    # partition products as intermediate (p1) or end-use (p2) as specified in filter_matrix
    filt_ParGhosh = np.ones_like(Z)
    intermediate_ParGhosh = materials.to_numpy() + intermediates.to_numpy() + products_p1.to_numpy() 
    filt_ParGhosh = filt_ParGhosh * intermediate_ParGhosh #only intermediate product rows remain with value 1; all others 0
    np.fill_diagonal(filt_ParGhosh, 0) #materials not made out of materials
    filt_ParGhosh_label = pd.DataFrame(data=filt_ParGhosh, index= Z.index, columns=Z.columns)
    
    return filt_ParGhosh, filt_ParGhosh_label 


# create filter matrices plain: define intermediate (materials, intermediates, products_p1) and end-use products (products_p2) and delete sector output of service sectors (for classifiction of raw materials & services see filter_matrix in main)
def create_PartialGhoshIO_filter_noServiceInput(Z, materials, intermediates, products_p1, non_service):
    # partition products as intermediate (p1) or end-use (p2) as specified in filter_matrix
    filt_ParGhosh = np.ones_like(Z)
    intermediate_ParGhosh = materials.to_numpy() + intermediates.to_numpy() + products_p1.to_numpy() 
    filt_ParGhosh = filt_ParGhosh * intermediate_ParGhosh #only intermediate product rows remain with value 1; all others 0
    filt_ParGhosh= (filt_ParGhosh.T * non_service).T # set outputs of service sectors to zero 
    np.fill_diagonal(filt_ParGhosh, 0) #materials not made out of materials
    filt_ParGhosh_label = pd.DataFrame(data=filt_ParGhosh, index= Z.index, columns=Z.columns)
    
    return filt_ParGhosh, filt_ParGhosh_label 


# calculate Partial Ghosh-IO end-use share matrix D_ParGhosh (equ. 10-12 in Streeck et al. 2022, part I; slightly different conduct)
def calc_PartialGhoshIO(Z, filter_matrix, filt_ParGhosh, filt_ParGhosh_label, aggregation_matrix, extension_products):
    
    # partition Z into products p1 & p2, calculate market share matrix Q_interm
    Z_filt = Z.copy()  * filt_ParGhosh
    Q_interm = Z_filt.divide(Z_filt.sum(axis=1),axis=0).replace(np.nan,0.0) 
    # Q_interm_sum = Q_interm.sum(axis=1) #check if column sum of Q_interm == 1 for intermediate commodities
    Q_interm = Q_interm.replace(np.inf,0)

    # calculate supply chain distribution matrix G_interm by calculating inverse of (I-Q_interm)
    I = np.eye(Q_interm.shape[0])
    G_interm = np.linalg.inv(I - Q_interm)

    # to derive end-use shares, delete columns of products classified as intermediate (p1) in matrix G
    # thus only keeping products classified as end-use (p2) - these end-use products 'absorbed' upstream inputs
    # the next three lines create a filter matrix that specifies that only end-use products can receive input;
    filt_EndUse = filt_ParGhosh_label.T.replace(1,2).replace(0,1).replace(2,0) #create filter matrix that specifies that only end-use products can receive input
    np.fill_diagonal(filt_EndUse.values, 0)
    D_ParGhosh_raw = G_interm * filt_EndUse *100 #apply filter
    #D_ParGhosh_raw_rowSum = D_ParGhosh_raw.sum(axis=1) # check if columns of end-uses sum up to 100%

    # filter for only materials of interest (extension_products) to obtain end-use share matrix D_ParGhosh
    D_ParGhosh = D_ParGhosh_raw.loc[extension_products,:].T

    #aggregate to materials of interest specified in aggregation_matrix
    D_ParGhosh_agg = aggregation_matrix.dot(D_ParGhosh)
    check_ParGhosh = D_ParGhosh_agg.sum(axis=0)

    return D_ParGhosh, D_ParGhosh_agg, Q_interm, check_ParGhosh



''' 
  # 5)  HYPOTHETICAL TRANSFER (HT) 
'''

# calculate new Z and Y matrices by transferring intermediate to final demand for selected sectoral output that is intermediate in MIOTs but end-use in MFA (e.g. packaging)
def hypothetical_transfer(Z, Y, A, filter_transf, yield_filter):
    
    #apply the pre-definied yield filter to Z so that no waste flows transferred to final demand
    Z_yield = Z * yield_filter
    
    # apply the pre-definied transfer filter to Z and Y, indicating the values that shall be transferred from Z to Y
    Z_transfer = Z_yield * filter_transf
    Z_transfer = pd.DataFrame(data = Z_transfer.sum(axis=1), columns = Y.columns)
    Y_transferred = Y + Z_transfer
    Z_transferred = Z_yield * filter_transf.replace(1,2).replace(0,1).replace(2,0) #delete transferred items in Z_yield
    
    # calculate new x (yield correction) and A
    x = pd.DataFrame(data = Z_transferred.sum(axis=1), columns = Y.columns) + Y_transferred
    
    x_diag = np.zeros_like(Z)
    np.fill_diagonal(x_diag, x)
    A_ht = pd.DataFrame(np.dot(Z_transferred,np.linalg.pinv(x_diag)), index = Y.index, columns = Y.index)
    print((A - A_ht).sum().sum()) #only difference here should be the yield substraction and transferred items

    return Y_transferred, Z_transferred, A_ht

# calculate new Z and Y matrices by transferring intermediate to final demand for selected sectoral output that is intermediate in MIOTs but end-use in MFA (e.g. packaging)
def hypothetical_transfer_exio(Z, Y, filter_transf, yield_filter):
    
    #apply the pre-definied yield filter to Z so that no waste flows transferred to final demand
    Z_yield = Z * yield_filter
    waste = Z - Z_yield
    # apply the pre-definied transfer filter to Z and Y, indicating the values that shall be transferred from Z to Y
    Z_transfer = Z_yield * filter_transf
    Z_transfer =  Z_transfer.T.groupby('region').sum().T
    Y_transferred = Y + Z_transfer
    Z_transferred = Z_yield * filter_transf.replace(1,2).replace(0,1).replace(2,0) #delete transferred items in Z_yield
    
    #check if transferred item sum equal to original per sector x region
    maxDiff_full_transf = Z_transferred.groupby('sector').sum().T.groupby('region').sum().T + Y_transferred.groupby('sector').sum()\
        + waste.groupby('sector').sum().T.groupby('region').sum().T - \
        (Z.groupby('sector').sum().T.groupby('region').sum().T + Y.groupby('sector').sum())
                
    if maxDiff_full_transf.max().sum() > 0.01:
        print ('WARNING: the sum of Y/Z_transferred per sector x region does not match the original Y/Z')
    else:
        print('The sum of Y/Z_transferred matches the original Y/Z')
    
    # calculate new x (yield correction) and A
    x = Z_transferred.sum(axis=1) + Y_transferred.sum(axis=1)
    # calculate inverse of x, but here not via matrix inverse due non-existent inverse and computing time for pseudoinverse
    x_inv_raw = np.divide(np.ones(len(x)), x.to_numpy())
    x_inv = np.where(x_inv_raw == np.inf, 0, x_inv_raw)
    x_inv_diag = np.zeros_like(Z_transferred)
    np.fill_diagonal(x_inv_diag, x_inv)
    
    # calculate new A; use original x as it does not change by transfer
    A_ht = pd.DataFrame(np.dot(Z_transferred,x_inv_diag), index = Z_transferred.index, columns = Z_transferred.columns)

    return Y_transferred, Z_transferred, A_ht


# calculate WIO-MFA end-use share matrix D_wio INCLUDING HYPOTHETICAL TRANSFER using mass filter matrices defined in prior functions (equ. 1-3 in Streeck et al. 2022, part I)
# no yield correction here, as this already occured during function hypothetical_transfer
def calc_WIO_noYieldCorr(A, Y, filt_Amp, filt_App, filter_matrix, aggregation_matrix, extension_products):
    
    # filter technology matrix A according to WIO-MFA mass filters and partition into Amp (materials --> products), App (products --> products)
    Amp_filt = A * filt_Amp 
    App_filt = A * filt_App                    
    
    # calculate material composition matrix C from Amp, App
    I = np.eye(A.shape[0])
    C = np.dot(Amp_filt,np.linalg.inv(I-App_filt))
    #C_label = pd.DataFrame(data = (C), index = A.index, columns = A.index)

    # calculate the absolute material deliveries to final demand (C*diag(Y))
    Y_diag = np.zeros_like(A)
    np.fill_diagonal(Y_diag, Y)
    WIO_split_raw = pd.DataFrame(np.dot(C,Y_diag),index=Y.index, columns=Y.index)
        
    # filter for materials of interest (extension_products) and calculate end-use share matrix D_wio by dividing WIO_split_raw by row-sum
    WIO_split = WIO_split_raw.loc[extension_products]
    D_wio = WIO_split.divide(WIO_split.sum(axis=1),axis=0).transpose()*100
        
    # aggregate to product-groups specified in aggregation_matrix
    D_wio_aggregated = aggregation_matrix.dot(D_wio)
    check_wio = D_wio_aggregated.sum(axis=0) # check if all shares sum up to 100%
    
    return D_wio,D_wio_aggregated,WIO_split,check_wio   


# calculate WIO-MFA end-use share matrix D_wio INCLUDING HYPOTHETICAL TRANSFER using mass filter matrices defined in prior functions (equ. 1-3 in Streeck et al. 2022, part I)
# no yield correction here, as this already occured during function hypothetical_transfer
def calc_WIO_noYieldCorr_exio(A, Y, filt_Amp, filt_App, filter_matrix, aggregation_matrix, extension_products):
    
    # filter technology matrix A according to WIO-MFA mass filters and partition into Amp (materials --> products), App (products --> products)
    Amp_filt = A * filt_Amp 
    App_filt = A * filt_App                    
    
    # calculate material composition matrix C from Amp, App
    I = np.eye(A.shape[0])
    C = np.dot(Amp_filt,np.linalg.inv(I-App_filt))
    C_label = pd.DataFrame(data = (C), index = A.index, columns = A.index)
    C_label_sectors = C_label.groupby('sector').sum()
    
    # calculate the absolute material deliveries to final demand (C*diag(Y))
    Y_diag = np.zeros_like(C_label)
    np.fill_diagonal(Y_diag, Y)
    WIO_split_raw = pd.DataFrame(np.dot(C_label_sectors,Y_diag),index=C_label_sectors.index, columns=C_label_sectors.columns)
    WIO_split_raw_srio = WIO_split_raw.T.groupby('sector').sum().T
        
    # filter for materials of interest (extension_products) and calculate end-use share matrix D_wio by dividing WIO_split_raw by row-sum
    WIO_split_region = WIO_split_raw_srio.loc[extension_products]
    D_wio_region = WIO_split_region.divide(WIO_split_region.sum(axis=1),axis=0).transpose()*100
        
    # aggregate to product-groups specified in aggregation_matrix
    D_wio_region_aggregated = aggregation_matrix.dot(D_wio_region)
    check_wio_region = D_wio_region_aggregated.sum(axis=0) # check if all shares sum up to 100%
    
    return D_wio_region,D_wio_region_aggregated,WIO_split_region,check_wio_region   


''' 
  # 5  MATCH MULTIINDEX EXIOBASE DFs
'''

def match_multiIndex(target_df, index_source):
    # convert index to dataframe
    old_idx = target_df.index.to_frame()
    old_col = target_df.columns.to_frame().rename(columns={0:'sector'})
    # insert new level to index
    old_idx.insert(0, 'region', index_source.index.get_level_values('region'))
    old_col.insert(0, 'region', index_source.columns.get_level_values('region'))
    # convert to .ultiIndex
    target_df.index = pd.MultiIndex.from_frame(old_idx)
    target_df.columns = pd.MultiIndex.from_frame(old_col)
    return target_df

''' 
  # 7  SAVE RESULTS
'''

# save function for pandas dataframes with options for important variables of all methods
def save_to_excel(fileName, D, D_aggregated, check, total_split=pd.DataFrame(), massFilterName=pd.DataFrame(),\
    yieldFilterName=pd.DataFrame(), filt_Amp=pd.DataFrame(), filt_App=pd.DataFrame(), GhoshZfilter=pd.DataFrame(),\
    GhoshYfilter=pd.DataFrame(),MarketShares=pd.DataFrame(), Ztransferred=pd.DataFrame(), Ytransferred=pd.DataFrame(),\
    filter_transf=pd.DataFrame(),filt_ParGhosh=pd.DataFrame()):
    writer = pd.ExcelWriter('./output/' + fileName + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    D_aggregated.to_excel(writer,'EndUse_shares_agg')
    D.to_excel(writer,'EndUse_shares')
    check.to_excel(writer,'check_100%')
    massFilterName.to_excel(writer,'Aggregator_Mass_Filter')
    total_split.to_excel(writer,'EndUse_abs')
    yieldFilterName.to_excel(writer,'Yield_Filter')
    filt_Amp.to_excel(writer,'Filter_A_mp')
    filt_App.to_excel(writer,'Filter_A_pp')
    GhoshZfilter.to_excel(writer,'filt_Ghosh_Z')
    GhoshYfilter.to_excel(writer,'filt_Ghosh_Y')
    filt_ParGhosh.to_excel(writer,'filter_ParGhosh')
    MarketShares.to_excel(writer,'Direct_market_shares')
    filter_transf.to_excel(writer,'filter_HypothTransfer')
    Ztransferred.to_excel(writer,'Z_afterHypothTransfer')
    Ytransferred.to_excel(writer,'Y_afterHypothTransfer')
    writer.save()