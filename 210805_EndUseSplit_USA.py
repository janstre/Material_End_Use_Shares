# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 08:53:52 2020

@author: jstreeck
"""

import numpy as np
import pandas as pd

'''
#1 LOAD DATA AND DERIVE OVERARCHING VARIABLES 

 --> set the year you want to look at; choose a split scenario; read required files for matrices Z, A, 
 final demand and the filter matrix; remove negatives in final demand by setting them to zero

'''

year = '2002' #year has to be a string
# split_scenarios = ['_Base','_ExtAgg'] --> list of scenario configurations of the IO matrices and filter matrix
scenario = '_Base' #specify the configuration of the IO matrices and filter matrix you want to look at
                   #_Base = Matrix as derived from Information of US BEA, _ExtAgg = certain extension sectors have been aggregated (e.g. paper mills + paperboard mills)
                   #_

Z = pd.read_excel('Z_' + year + '_ImpNoExpNoCII' + scenario + '.xlsx',index_col=[0,1],header=[0,1]) #commodity x commodity transaction matrix
A_label = pd.read_excel('A_' + year + '_ImpNoExpNoCII' + scenario + '.xlsx',index_col=[0,1],header=[0,1]) # technology matrix: commodity x commodity with industry technology
Y = pd.read_excel('Y_' + year + '_ImpNoExpNoCII' + scenario + '.xlsx',index_col=[0,1]) # final demand vector (treatment of imports, exports and CII as specified in file name)
filter_matrix = pd.read_excel('Filter_' + year  + scenario + '_extensionSeparate.xlsx',index_col=[0,1],header=[0,1],sheet_name='filter')

#calculate total requirements L and total commodity output x
A = A_label.to_numpy()
I = np.eye(A.shape[0])
L = np.linalg.inv(I-A)
x = Z.sum(axis=1) + Y.sum(axis=1)
if x.sum() == np.dot(L, Y).sum():
    print('x and calculated x (from L and final demand) are identical')

#set negatives in final demand to zero and calculate new x
Y.clip(lower=0, inplace=True)
x = Z.sum(axis=1) + Y.sum(axis=1)



'''
#2 APPLICATION OF METHODS TO DERIVE END-USE SPLITS

 #A Leontief-type:
    
  A.1) CONSUMPTION BASED APPROACH'''

# calculate dummy material intensities to check later if all extension-material is delivered to final demand (mass balance)
x_cons = x.copy().to_numpy().reshape(-1,1)
mass_dummy = np.arange(1000,(np.shape(x_cons)[0]+1)*1000,1000,dtype=float).reshape(-1,1)
material_intens = mass_dummy/x_cons
material_intens[material_intens == np.inf] = 0

# diagonalize material intensities and calculate multiplier (material_intens_diag x L)
material_intens_diag = pd.DataFrame(np.zeros_like(Z), index=Z.index, columns=Z.columns)
np.fill_diagonal(material_intens_diag.values, material_intens)
multiplier = np.dot(material_intens_diag,L)

#calculate material deliveries to final demand (multiplier x Y_diag)
Y_diag = np.zeros_like(Z)
np.fill_diagonal(Y_diag, Y)
Consumption_split_raw = pd.DataFrame(np.dot(multiplier,Y_diag),index=Z.index, columns=Z.columns)
Consumption_split_raw_rowSum = Consumption_split_raw.sum(axis=1) # check if all of extension's 'mass' delivered to final demand

#filter for only the material sectors we are interested in and calculate end-use shares
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()
Consumption_split = Consumption_split_raw.loc[extension_sectors]
Consumption_split_sum = Consumption_split.sum(axis=1)
Consumption_split_shares = Consumption_split.divide(Consumption_split_sum,axis=0).transpose()*100
Consumption_split_shares.sum(axis=0) # check if all shares sum up to 100%

#aggregate to product-groups specified in filter_matrix
aggregation_matrix = filter_matrix.iloc[:,5:-1].T #get only the end-use aggregation categories from the filter_matrix and remove row sum
Consumption_split_shares_aggregated = aggregation_matrix.dot(Consumption_split_shares)
Consumption_split_shares_aggregated.sum(axis=0) # check if all shares sum up to 100%

#save results and input data with time stamp to eneable reproduction of results
#writer = pd.ExcelWriter('./output/ConsumptionBased_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
#filter_matrix.to_excel(writer,'Filter_Settings')
#Consumption_split.to_excel(writer,'Cons_split_abs')
#Consumption_split_shares.to_excel(writer,'Cons_split_shares')
#Consumption_split_shares_aggregated.to_excel(writer,'Cons_split_shares_agg')
#writer.save()

del  x_cons, mass_dummy, material_intens, material_intens_diag, multiplier, Y_diag, Consumption_split_raw, Consumption_split_raw_rowSum,\
     extension_sectors, Consumption_split, Consumption_split_sum, Consumption_split_shares, aggregation_matrix, Consumption_split_shares_aggregated
     
     
     
'''
  A.2) WASTE INPUT OUTPUT APPROACH TO MFA

   A.2.1) create filter matrices A_mp (materials to products) and A_pp (products to products) from filter_matrix settings'''

#define the filter settings for different materials/product groups
raw_materials = filter_matrix.loc[:,(['All'],['Raw_materials'])]
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products_p1 = filter_matrix.loc[:,(['All'],['Products_p1'])]
products_p2 = filter_matrix.loc[:,(['All'],['Products_p2'])]
products = products_p1.to_numpy() + products_p2.to_numpy()
non_service = materials.to_numpy() + intermediates.to_numpy() + products + raw_materials.to_numpy() 

#from filter settings create filter matrix A_mp for materials going to products
filt_Amp = np.ones_like(Z)
filt_Amp = filt_Amp * materials.to_numpy() #only materials sectors remain
filt_Amp = (filt_Amp.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T #removes reverse flows of materials; e.g. sawmills --> pulp production (as specified in filter)
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of materials to service sectors if specified ('Yes') in filter matrix
    filt_Amp = (filt_Amp.T * non_service).T
np.fill_diagonal(filt_Amp, 0) #materials not made out of materials
filt_Amp_label = pd.DataFrame(data=filt_Amp, index= A_label.index, columns=A_label.columns) #assign labels

#from filter settings create filter matrix A_pp for products going to products
filt_App = np.ones_like(Z)
filt_App = filt_App  * (products + intermediates.to_numpy())
filt_App = (filt_App.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T#removes reverse product flows --> products cannot go back to raw materials
filt_App = (filt_App.T * (np.ones_like(materials) - materials.to_numpy())).T #removes reverse product flows --> products cannot go back to materials
filt_App = (filt_App.T * (np.ones_like(intermediates) - intermediates.to_numpy())).T #remove deliveries to intermediate --> products cannot go back to intermediate sectors
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of materials to service sectors if specified ('Yes') in filter matrix
    filt_App = (filt_App.T * non_service).T 
filt_App_label = pd.DataFrame(data=filt_App, index= A_label.index, columns=A_label.columns) #assign labels


'''
  A.2.2) create material composition matrix C multipliers for extension sectors and calculate deliveries to final demand (multiplier x C x Y)
    '''
    
#filter technology matrix A according WIO-MFA filter settings as specified in A.2.1
Amp_filt = A * filt_Amp
App_filt = A * filt_App
                              
#calculate material composition matrix C with filtered A
I = np.eye(A.shape[0])
C = np.dot(Amp_filt,np.linalg.inv(I-App_filt))
C_label = pd.DataFrame(data = (C), index = Z.index, columns = Z.index)
   
#recalculate total commodity output (x_WIO) with C and calculate a dummy multiplier to check later if all extension-material is delivered to final demand (mass balance)
x_WIO = np.dot(C, Y).reshape(-1,1)
if x.sum() > x_WIO.sum():
    print('sum of x_WIO is smaller than sum of initital x')
    
#calculate dummy material intensities to check later if all extension-material is delivered to final demand (mass balance)
mass_dummy_WIO = np.arange(1000,(np.shape(x_WIO)[0]+1)*1000,1000,dtype=float).reshape(-1,1)
mass_dummy_WIO.reshape(-1,1)
material_intens  = mass_dummy_WIO/x_WIO
material_intens[material_intens  == np.inf] = 0

material_intens_diag = pd.DataFrame(np.zeros_like(Z), index=Z.index, columns=Z.columns)
np.fill_diagonal(material_intens_diag.values, material_intens)
Y_diag = np.zeros_like(Z)
np.fill_diagonal(Y_diag, Y)
multiplier = np.dot(material_intens_diag ,C) 

#calculate the material deliveries for final demand
WIO_split_raw = pd.DataFrame(np.dot(multiplier,Y_diag),index=Z.index, columns=Z.columns)
WIO_split_raw_rowSum = WIO_split_raw.sum(axis=1)

#filter for only the material sectors we are interested in and calculate end-use shares
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()
WIO_split = WIO_split_raw.loc[extension_sectors]
WIO_split_sum = WIO_split.sum(axis=1)
WIO_split_shares = WIO_split.divide(WIO_split_sum,axis=0).transpose()*100

#aggregate to product-groups specified in filter_matrix
aggregation_matrix = filter_matrix.iloc[:,5:-1].T #get only the end-use aggregation categories from the filter_matrix and remove row sum
WIO_split_shares_aggregated = aggregation_matrix.dot(WIO_split_shares)
WIO_split_shares_aggregated.sum(axis=0) # check if all shares sum up to 100%

#save run to Excel, together with filter matrices used
#writer = pd.ExcelWriter('./output/WIOMF_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
#filter_matrix.to_excel(writer,'Filter_Settings')
#filt_Amp_label.to_excel(writer,'Filter_A_mp')
#filt_App_label.to_excel(writer,'Filter_A_pp')
#WIO_split.to_excel(writer,'WIO_split_abs')
#WIO_split_shares.to_excel(writer,'WIO_split_shares')
#WIO_split_shares_aggregated.to_excel(writer,'WIO_split_shares_agg')
#writer.save()


del x_WIO, material_intens, aggregation_matrix, C, C_label, materials, intermediates, non_service, products, products_p1, products_p2, raw_materials, WIO_split_raw, \
    WIO_split_raw_rowSum, WIO_split_sum, WIO_split_shares,  Y_diag, multiplier
     

''' 
  A.2.3) Recalculate Results with Hypothetical Extraction Method (HEM) for defined product groups to
         identify the role of packaging and functionality of deliveries from service sectors
    '''

#read end-use sector aggregation from filter_matrix
residential = filter_matrix.loc[:,(['End-Use Category'],['Residential'])].to_numpy()#
non_residential = filter_matrix.loc[:,(['End-Use Category'],['Non-Residential'])].to_numpy()#
other_buildings = filter_matrix.loc[:,(['End-Use Category'],['Other buildings'])].to_numpy()#
infrastructure = filter_matrix.loc[:,(['End-Use Category'],['Infrastructure'])].to_numpy()#
other_construction = filter_matrix.loc[:,(['End-Use Category'],['Other construction'])].to_numpy()#
elec_machinery = filter_matrix.loc[:,(['End-Use Category'],['Electronic machinery'])].to_numpy()#
other_machinery = filter_matrix.loc[:,(['End-Use Category'],['Other machinery'])].to_numpy()#
motor_vehicles = filter_matrix.loc[:,(['End-Use Category'],['Motor vehicles'])].to_numpy()#
other_transport = filter_matrix.loc[:,(['End-Use Category'],['Other transport equipment'])].to_numpy()#
household_appl = filter_matrix.loc[:,(['End-Use Category'],['Household appliances'])].to_numpy()#
consumer_durables = filter_matrix.loc[:,(['End-Use Category'],['Other consumer durables'])].to_numpy()#
furniture = filter_matrix.loc[:,(['End-Use Category'],['Furniture'])].iloc[:,0].to_numpy()#
extraction = filter_matrix.loc[:,(['End-Use Category'],['Extraction'])].iloc[:,0].to_numpy()#
textiles = filter_matrix.loc[:,(['End-Use Category'],['Textiles'])].iloc[:,0].to_numpy()#
packaging = filter_matrix.loc[:,(['End-Use Category'],['Packaging'])].iloc[:,0].to_numpy()#
food_products = filter_matrix.loc[:,(['End-Use Category'],['Food products'])].to_numpy()#
products_nec = filter_matrix.loc[:,(['End-Use Category'],['Products nec'])].to_numpy()#
services = filter_matrix.loc[:,(['End-Use Category'],['Services'])].iloc[:,0].to_numpy()#
extension = filter_matrix.loc[:,(['End-Use Category'],['Extension'])].iloc[:,0].to_numpy()# 

product_groups = ['residential','non_residential','other_buildings','infrastructure','other_construction','elec_machinery','other_machinery','motor_vehicles','other_transport',\
                 'household_appl','consumer_durables','furniture','extraction','textiles','packaging','food_products','products_nec','services','extension']
dict_product_groups = dict(zip([x for x in product_groups] ,[eval(x) for x in product_groups]))
dict_HEM_shares = dict()

#this loop extract each of the above defined product groups via the HEM approach and calculates the difference to the original WIO-split from A.2.2
#as the product groups are inputs to other product groups; double counting occurs during the process and results do add up to more than total 

# TO HANSI / DOMINIK: the idea of this is to 1) determine the materials contained in packaging (which according to IO definitions is largely intermediate demand) and
# 2) to determine which 'functional product groups' make up the share of service deliveries to final demand (determine the prior processing stage which is input to services)

for product_group in product_groups:

    #set rows of product_group to zero in technology matries A_mp, A_pp (product_group as defined in the filter_matrix)
    HEM_to_extract = dict_product_groups.get(product_group)
    HEM_rowCol = np.argwhere(HEM_to_extract== 1).tolist()
    filt_Amp_HEM = filt_Amp.copy()
    filt_Amp_HEM[HEM_rowCol,:] = 0   
    #filt_Amp_HEM[:,HEM_rowCol] = 0 #optional following the approach of Dietzenbacher et al (2019) and similar to Yokoi et al. (2018); result is same   
    filt_App_HEM = filt_App.copy()  
    filt_App_HEM[HEM_rowCol,:] = 0  
    #filt_Amp_HEM[:,HEM_rowCol] = 0 #optional following the approach of Dietzenbacher et al (2019) and similar to Yokoi et al. (2018); result is same       
    Amp_filt_HEM = Amp_filt * filt_Amp_HEM 
    App_filt_HEM = App_filt * filt_App_HEM

    #set rows for packaging commodities to zero in final demand vector
    Y_HEM = Y.copy()
    Y_HEM.iloc[HEM_rowCol,:] = 0

    #recalculate total requirement matrix C
    I = np.eye(A.shape[0])
    C_HEM = np.dot(Amp_filt_HEM,np.linalg.inv(I-App_filt_HEM))
    C_HEM_label = pd.DataFrame(data = (C_HEM), index = Z.index, columns = Z.index)

    #diagonalize new final demand vector without product_group final demand
    Y_HEM_diag = np.zeros_like(Z)
    np.fill_diagonal(Y_HEM_diag , Y_HEM)

    #calculate end-use split with rows for selected product groups zero in A_mp/A_pp and final demand;
    #re-calculate multiplier with material_intens_diag from original WIO-MF calculation (code row 154/155)
    #--> this way multiplier based on original model
    #--> difference of deliveries to final demand between the mass_dummy for the original WIO-MF and WIO-MF-HEM;
    #are the deliveries of materials contained in extracted product group
    multiplier = np.dot(material_intens_diag,C_HEM) 
    WIO_split_HEM_raw = pd.DataFrame(np.dot(multiplier,Y_HEM_diag),index=Z.index, columns=Z.columns)
    WIO_split_HEM_raw_rowSum = WIO_split_HEM_raw.sum(axis=1)

    #filter for only the material sectors we are interested in and calculate end-use shares
    WIO_split_HEM = WIO_split_HEM_raw.loc[extension_sectors,:]
    WIO_split_HEM_rowSum = WIO_split_HEM.sum(axis=1)
    #WIO_split_HEM_rowSum_share = WIO_split_HEM_rowSum /env_ext.reshape(-1,1)
    ## calculate share of deliveries to final demand of WIO-MF-HEM in the original WIO-MF 
    # 1-share are the deliveries of materials contained in extracted product group
    mass_dummy_WIO_label = pd.DataFrame(data= mass_dummy_WIO, index = Z.index)
    env_ext = mass_dummy_WIO_label.loc[extension_sectors].to_numpy()   
    WIO_split_HEM_shares = (WIO_split_HEM/env_ext).transpose()

    '''WILL REMOVE THE to_numpy() HERE FROM TWO LINES BEFORE TO MAKE IT MORE CLEAN'''

    #aggregate to product-groups specified in filter_matrix
    aggregation_matrix = filter_matrix.iloc[:,5:-1].T #get only the end-use aggregation categories from the filter_matrix and remove row sum
    WIO_split_HEM_shares_aggregated = aggregation_matrix.dot(WIO_split_HEM_shares)
    WIO_split_HEM_shares_aggregated_colSum = WIO_split_HEM_shares_aggregated.sum(axis=0)

    #calculate the difference if the original WIO-MF and the HEM-WIO-MFA to determine contribution of extracted sector
    d_abs_HEM = WIO_split - WIO_split_HEM
    d_abs_HEM_aggregated = aggregation_matrix.dot(d_abs_HEM.T)
    d_split_HEM_shares = (d_abs_HEM_aggregated/env_ext.T)*100
    dict_HEM_shares[product_group] = d_split_HEM_shares
    
    del HEM_to_extract, HEM_rowCol, filt_Amp_HEM, filt_App_HEM, Amp_filt_HEM, App_filt_HEM, Y_HEM, I, C_HEM, C_HEM_label, Y_HEM_diag, multiplier,\
        WIO_split_HEM_raw, WIO_split_HEM_raw_rowSum, WIO_split_HEM, WIO_split_HEM_rowSum, mass_dummy_WIO_label, env_ext, WIO_split_HEM_shares, \
        aggregation_matrix, WIO_split_HEM_shares_aggregated, WIO_split_HEM_shares_aggregated_colSum, d_abs_HEM, d_abs_HEM_aggregated, d_split_HEM_shares,\
        product_group

# this loop builds a dataframe from the dict_HEM_shares which reflects the deliveries of product groups to final demand of the same product group
# the results should be equivalent to those of WIO_split_shares_aggregated
deliveries2Y_productGroups = pd.DataFrame() 
for i,j in enumerate(product_groups):
    group = dict_HEM_shares.get(j).iloc[i]
    deliveries2Y_productGroups  = deliveries2Y_productGroups.append(group.T)

#check if shares sum up to 100% and if deliveries2Y_productGroups ~equals WIO_split_shares_aggregated
deliveries2Y_productGroups_colSum = deliveries2Y_productGroups.sum(axis=0)  
d_WIO_HEM =  WIO_split_shares_aggregated - deliveries2Y_productGroups
if d_WIO_HEM.sum().sum() < 0.1:
    print('the difference of original WIO shares and HEM shares to final demand of product groups is less than 0.1%')
 
# now we will modify deliveries2Y_productGroups by 1) substracting the material that is packaging from product group deliveries and re-assign that as 'packaging'
# and 2) re-assigning the material delivered to final demand by the service product groups, according to the deliveries of other groups to services 
# --> cannot do because of double counting! 

#contribution of packaging to material deliveries to final demand 
deliveries_packaging = dict_HEM_shares.get('packaging')
deliveries_packaging_colSum = deliveries_packaging .sum(axis=0) 
 
#contribution of other sectors to the material deliveries to final demand of the service-product-group (contains double counting)
deliveries_to_services = pd.DataFrame()
for i,j in enumerate(product_groups):
    serv = dict_HEM_shares.get(j).iloc[17].rename(('Deliveries to services',j))  
    deliveries_to_services = deliveries_to_services.append(serv.T)
    
deliveries_to_services.index = pd.MultiIndex.from_tuples(deliveries_to_services.index)
deliveries_to_services.columns = pd.MultiIndex.from_tuples(deliveries_to_services.columns) 
 
deliveries_to_services.loc[['Deliveries to services'],['services'],:] = 0 #set the service sector itself zero (when you extract it with HEM, the results is the sum of all inputs)
for col in deliveries_to_services.columns:#furthermore, set the maximum of each column to zero (the maximum results if the extension sector is in the product group adn equals all deliveries to final demand from service sector)
    deliveries_to_services.loc[deliveries_to_services.idxmax()[col], col] = 0
deliveries_to_services_colSum = deliveries_to_services.sum(axis=0)  # this is the 


#save run to Excel, together with filter matrices used
#writer = pd.ExcelWriter('./output/WIOMF_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
#filter_matrix.to_excel(writer,'Filter_Settings')
#filt_Amp_label.to_excel(writer,'Filter_A_mp')
#filt_App_label.to_excel(writer,'Filter_A_pp')
#WIO_split_HEM.to_excel(writer,'WIO_HEM_split_abs')
#WIO_split_HEM_shares.to_excel(writer,'WIO_HEM_split_shares')
#WIO_split_HEM_shares_aggregated.to_excel(writer,'WIO_HEM_split_shares_agg')
#writer.save()

del Amp_filt, App_filt, residential, non_residential, infrastructure, other_construction, elec_machinery, other_machinery, motor_vehicles, other_transport, household_appl, \
    consumer_durables, other_buildings, furniture, extraction, textiles, packaging, food_products, services, products_nec, filt_Amp, filt_Amp_label, filt_App, filt_App_label,\
    deliveries2Y_productGroups, deliveries2Y_productGroups_colSum, d_WIO_HEM, deliveries_packaging, deliveries_packaging_colSum, deliveries_to_services,\
    deliveries_to_services_colSum, dict_HEM_shares, dict_product_groups, extension, extension_sectors, group, i, j, mass_dummy_WIO, serv, WIO_split,\
    WIO_split_shares_aggregated, col, material_intens_diag, product_groups
    
    

''' 
  A.2.4) New method idea: try to transfer rows of intermediate demand for packaging (as proof-of-concept) sector to final demand
    THIS IS NOT WELL THOUGHT THROUGH YET
    '''
    
# transfer the intermediate demand from packaging products in Z to new final demand Y_transferred
packaging = filter_matrix.loc[:,(['End-Use Category'],['Packaging'])].iloc[:,0].to_numpy()#
Z_transfer = pd.DataFrame(data=(Z.sum(axis=1)*packaging))
Z_transfer.index.set_names(['commodity_ID', 'commodity_label'], inplace=True)
Z_transfer.rename(columns = {0:'final_demand'}, inplace="True")
Y_transferred = Y.copy() + Z_transfer

# calculate a new A matrix from Z where packaging intermedate demand is deleted; use original x as this remains the same 
Z_deleted = Z*(1-packaging).reshape(-1,1)
x_diag = np.zeros_like(Z)
np.fill_diagonal(x_diag , x)
x_diag_inv = np.linalg.pinv(x_diag)
A_own = np.dot(Z_deleted,x_diag_inv )

print((A_label - A_own).sum().sum()) #only difference here should be the rows of the packaging sectors

#define the filter settings for different materials/product groups
raw_materials = filter_matrix.loc[:,(['All'],['Raw_materials'])]
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products_p1 = filter_matrix.loc[:,(['All'],['Products_p1'])]
products_p2 = filter_matrix.loc[:,(['All'],['Products_p2'])]
products = products_p1.to_numpy() + products_p2.to_numpy()
non_service = materials.to_numpy() + intermediates.to_numpy() + products + raw_materials.to_numpy() 

#from filter settings create filter matrix A_mp for materials going to products
filt_Amp_own = np.ones_like(Z)
filt_Amp_own = filt_Amp_own * materials.to_numpy() #only materials sectors remain
filt_Amp_own = (filt_Amp_own.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T #removes reverse flows of materials; e.g. sawmills --> pulp production (as specified in filter)
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of materials to service sectors if specified ('Yes') in filter matrix
    filt_Amp_own = (filt_Amp_own.T * non_service).T
np.fill_diagonal(filt_Amp_own, 0) #materials not made out of materials
filt_Amp_own_label = pd.DataFrame(data=filt_Amp_own, index= A_label.index, columns=A_label.columns) #assign labels

#from filter settings create filter matrix A_pp for products going to products
filt_App_own = np.ones_like(Z)
filt_App_own = filt_App_own  * (products + intermediates.to_numpy())
filt_App_own = (filt_App_own.T * (np.ones_like(raw_materials) - raw_materials.to_numpy())).T#removes reverse product flows --> products cannot go back to raw materials
filt_App_own = (filt_App_own.T * (np.ones_like(materials) - materials.to_numpy())).T #removes reverse product flows --> products cannot go back to materials
filt_App_own = (filt_App_own.T * (np.ones_like(intermediates) - intermediates.to_numpy())).T #remove deliveries to intermediate --> products cannot go back to intermediate sectors
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of materials to service sectors if specified ('Yes') in filter matrix
    filt_Ap_ownp = (filt_App_own.T * non_service).T 
filt_App_own_label = pd.DataFrame(data=filt_App_own, index= A_label.index, columns=A_label.columns) #assign labels


#filter technology matrix A according WIO-MFA filter settings as specified in A.2.1
Amp_filt_own = A_own * filt_Amp_own
App_filt_own = A_own * filt_App_own

#calculate material composition matrix C with filtered A
I = np.eye(A.shape[0])
C_own = np.dot(Amp_filt_own,np.linalg.inv(I-App_filt_own))
C_own_label = pd.DataFrame(data = (C_own), index = Z.index, columns = Z.index)

#recalculate total commodity output (x_OWN) with C and calculate a dummy multiplier to check later if all extension-material is delivered to final demand (mass balance)
x_OWN = np.dot(C_own, Y_transferred).reshape(-1,1)
if x.sum() > x_OWN.sum():
    print('sum of x_OWN is smaller than sum of initital x')
    
#calculate dummy material intensities to check later if all extension-material is delivered to final demand (mass balance)
mass_dummy_OWN = np.arange(1000,(np.shape(x_OWN)[0]+1)*1000,1000,dtype=float).reshape(-1,1)
mass_dummy_OWN.reshape(-1,1)
material_intens  = mass_dummy_OWN/x_OWN
material_intens[material_intens  == np.inf] = 0

material_intens_diag = pd.DataFrame(np.zeros_like(Z), index=Z.index, columns=Z.columns)
np.fill_diagonal(material_intens_diag.values, material_intens)
Y_diag = np.zeros_like(Z)
np.fill_diagonal(Y_diag, Y_transferred)
multiplier = np.dot(material_intens_diag ,C_own) 

#calculate the material deliveries for final demand
OWN_split_raw = pd.DataFrame(np.dot(multiplier,Y_diag),index=Z.index, columns=Z.columns)
OWN_split_raw_rowSum = OWN_split_raw.sum(axis=1)

#filter for only the material sectors we are interested in and calculate end-use shares
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()
OWN_split = OWN_split_raw.loc[extension_sectors]
OWN_split_sum = OWN_split.sum(axis=1)
OWN_split_shares = OWN_split.divide(OWN_split_sum,axis=0).transpose()*100

aggregation_matrix = filter_matrix.iloc[:,5:-1].T #get only the end-use aggregation categories from the filter_matrix and remove row sum
OWN_split_aggregated = aggregation_matrix.dot(OWN_split.T)

#aggregate to product-groups specified in filter_matrix
OWN_split_shares_aggregated = aggregation_matrix.dot(OWN_split_shares)
OWN_split_shares_aggregated.sum(axis=0) # check if all shares sum up to 100%


'''

 #B Ghosh-type
 
  B.1) INTERINDUSTRY MARKET SHARE APPROACH

#create filter matrix specific to approach B.1 y classifying commodities as intermediate (p1) or end-use (p2) as specified filter_matrix
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products_p1 = filter_matrix.loc[:,(['All'],['Products_p1'])]
products_p2 = filter_matrix.loc[:,(['All'],['Products_p2'])]
products = products_p1.to_numpy() + products_p2.to_numpy()
raw_materials = filter_matrix.loc[:,(['All'],['Raw_materials'])]
non_service = materials.to_numpy() + intermediates.to_numpy() + products + raw_materials.to_numpy() 

filt_Ghosh = np.ones_like(Z)
intermediate_Ghosh = materials.to_numpy() + intermediates.to_numpy() + products_p1.to_numpy() 
filt_Ghosh = filt_Ghosh * intermediate_Ghosh #only intermediate product rows remain with value 1; all others 0
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of materials to service sectors if specified in filter matrix
    filt_Ghosh= (filt_Ghosh.T * non_service).T
np.fill_diagonal(filt_Ghosh, 0) #materials not made out of materials
filt_Ghosh_label = pd.DataFrame(data=filt_Ghosh, index= A_label.index, columns=A_label.columns)

#apply filter matrix Ghosh_filt to transaction matrix Z, calculate market share matrix B_Ghosh 
Z_method = Z.copy()
Z_filt = Z_method  * filt_Ghosh
B_Ghosh = Z_filt.divide(Z_filt.sum(axis=1),axis=0).replace(np.nan,0.0)
B_Ghosh_sum = B_Ghosh.sum(axis=1) #check if column sum of B_Ghosh == 1 for intermediate commodity sectors
B_Ghosh = B_Ghosh.replace(np.inf,0)
B_Ghosh_complete = Z.divide(Z.sum(axis=1),axis=0).replace(np.nan,0.0)

#calculate supply chain distribution matrix G by calculating inverse of (I-B_Ghosh)
I = np.eye(B_Ghosh.shape[0])
G = np.linalg.inv(I - B_Ghosh)

#in G delete columns of commidities classified as intermediate (p1), 
#thus only keeping commidities classified as end-use (p2) - these end-use products 'absorbed' upstream inputs
#the next three lines create a filter matrix that specifies that only end-use commodity sectors can receive input;
# and thus sets columns of commidities classified as intermediate (p1) to zero
EndUse_filt = filt_Ghosh_label.T 
EndUse_filt = EndUse_filt.replace(1,2).replace(0,1).replace(2,0)
np.fill_diagonal(EndUse_filt.values, 0) # fill diagonal with 0 

#multiply end-use filter with G
Ghosh_split_shares_raw = G * EndUse_filt *100
Ghosh_split_shares_raw_rowSum = Ghosh_split_shares_raw.sum(axis=1) # check if columns of end-uses sum up to 100%

#sum up results and calculate shares of material going to different commodities
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()
Ghosh_split_shares = Ghosh_split_shares_raw.loc[extension_sectors,:].T

#aggregate to product-groups specified in filter_matrix
aggregation_matrix = filter_matrix.iloc[:,5:-1].T #get only the end-use aggregation categories from the filter_matrix and remove row sum
Ghosh_split_shares_agg = aggregation_matrix.dot(Ghosh_split_shares)
Ghosh_split_shares_agg_colSum = Ghosh_split_shares_agg.sum(axis=0)

#save run to Excel, together with filter matrices used
#writer = pd.ExcelWriter('Ghosh_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
#filter_matrix.to_excel(writer,'Filter_Settings')
#B_Ghosh.to_excel(writer,'Direct_market_shares')
#Ghosh_split_shares_raw.to_excel(writer,'Ghosh_split_shares_raw')
#Ghosh_split_shares.to_excel(writer,'Ghosh_split_shares')
#Ghosh_split_shares_agg.to_excel(writer,'Ghosh_split_shares_agg')
#writer.save()

####'''


