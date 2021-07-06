# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 08:53:52 2020

@author: jstreeck
"""

import os
os.chdir('C:/Users/jstreeck/Desktop/EndUse_shortTermSave/2020_NationalOfficial_IOSUT/USA/Benchmark_SUTIO/')
import numpy as np
import pandas as pd

'''
READ PREPARED FILES FOR MATRICES Z, A, FINAL DEMAND'''

Z_icc = pd.read_excel('2007_2012_USA_SUT_497industries/Z_icc_2007_ImpNoExpNoCII_ExtAgg.xlsx',index_col=[0],header=[0]) #commodity x commodity transaction matrix
A_icc_label = pd.read_excel('2007_2012_USA_SUT_497industries/A_icc_2007_ImpNoExpNoCII_ExtAgg.xlsx',index_col=[0],header=[0]) # technology matrix: commodity x commodity with industry technology
final_demand = pd.read_excel('2007_2012_USA_SUT_497industries/FinalDemand_2007_ImpNoExpNoCII_ExtAgg.xlsx',index_col=[0]) # final demand vector (treatment of imports, exports and CII as specified in file name)

A_icc = A_icc_label.to_numpy()
I = np.eye(A_icc.shape[0])
L_icc = np.linalg.inv(I-A_icc)
x_icc = Z_icc.sum(axis=1) + final_demand.sum(axis=1)



''' APPLICATION OF METHODS TO DERIVE END-USE SPLITS

#1-Leontief-type:
    
1.1) CONSUMPTION BASED APPROACH'''

# load filter matrix for aggregation of commodities to commodity groups later on
filter_matrix = pd.read_excel('2007_2012_USA_SUT_497industries/Filter_WIObase_05072021_ExtensionAgg.xlsx',index_col=[0,1],header=[0,1])

# calculate a dummy multiplier to check later if all extension-material is delivered to final demand (mass balance)
x_icc_cons = x_icc.to_numpy().reshape(-1,1)
mass_dummy = np.arange(1000,(np.shape(x_icc_cons)[0]+1)*1000,1000,dtype=float).reshape(-1,1)
mult = mass_dummy/x_icc_cons
mult[mult == np.inf] = 0

# diagonalize multiplier and final demand and calculate (multiplier_diag x L_icc x finalDemand_diag), which results in splitting extension to deliveries to final demand for commodities
mult_diag = pd.DataFrame(np.zeros_like(Z_icc), index=Z_icc.index, columns=Z_icc.columns)
np.fill_diagonal(mult_diag.values, mult)
finalDemand_diag = np.zeros_like(Z_icc)
np.fill_diagonal(finalDemand_diag, final_demand)

initiator = np.dot(mult_diag,L_icc)  
Cons_split = pd.DataFrame(np.dot(initiator,finalDemand_diag),index=Z_icc.index, columns=Z_icc.columns)
Cons_split_colsum = Cons_split.sum(axis=1) # check if all of extension's 'mass' delivered to final demand


#filter for only the sectors we are interested in and calculate end-use shares
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()
Cons_split_sectors = Cons_split.iloc[extension_sectors,:]
Cons_sum = Cons_split_sectors.sum(axis=1)
Cons_split_shares = Cons_split_sectors.divide(Cons_sum,axis=0).transpose()*100
#ratio_fd_x_ind =   final_demand.iloc[:,0].values / x_SUT.iloc[:401]   

#aggregate to level specified in Filter Settings
construction_agg = filter_matrix.loc[:,(['End-Use Category'],['Construction'])].iloc[:,0].to_numpy()#
machinery_agg = filter_matrix.loc[:,(['End-Use Category'],['Machinery'])].iloc[:,0].to_numpy()#
vehicles_agg = filter_matrix.loc[:,(['End-Use Category'],['Motor vehicles'])].iloc[:,0].to_numpy()#
otherTrans_agg = filter_matrix.loc[:,(['End-Use Category'],['Other transport equipment'])].iloc[:,0].to_numpy()#
other_agg = filter_matrix.loc[:,(['End-Use Category'],['Products nec'])].iloc[:,0].to_numpy()#
furniture_agg = filter_matrix.loc[:,(['End-Use Category'],['Furniture'])].iloc[:,0].to_numpy()#
extract_agg = filter_matrix.loc[:,(['End-Use Category'],['Extraction'])].iloc[:,0].to_numpy()#
textiles_agg = filter_matrix.loc[:,(['End-Use Category'],['Textiles'])].iloc[:,0].to_numpy()#
packaging_agg = filter_matrix.loc[:,(['End-Use Category'],['Packaging'])].iloc[:,0].to_numpy()#
services_agg = filter_matrix.loc[:,(['End-Use Category'],['Services'])].iloc[:,0].to_numpy()#
other2_agg = filter_matrix.loc[:,(['End-Use Category'],['Other'])].iloc[:,0].to_numpy()#
Cons_agg_split = pd.DataFrame({'Construction': Cons_split_shares[construction_agg == 1].sum(axis=0),'Machinery': Cons_split_shares[machinery_agg == 1].sum(axis=0),\
                          'Motor Vehicles': Cons_split_shares[vehicles_agg == 1].sum(axis=0),'Other Transport': Cons_split_shares[otherTrans_agg == 1].sum(axis=0),\
                              'Products nec': Cons_split_shares[other_agg == 1].sum(axis=0), 'Furniture': Cons_split_shares[furniture_agg == 1].sum(axis=0), \
                                  'Agri & Extraction': Cons_split_shares[extract_agg == 1].sum(axis=0), 'Textiles': Cons_split_shares[textiles_agg == 1].sum(axis=0), \
                                      'Packaging': Cons_split_shares[packaging_agg == 1].sum(axis=0), 'Services': Cons_split_shares[services_agg == 1].sum(axis=0),\
                                        'Other': Cons_split_shares[other2_agg == 1].sum(axis=0)} )
    
Cons_agg_split['Sum'] = Cons_agg_split.sum(axis=1)

#save results and input data to reproduce those with time stamp for
writer = pd.ExcelWriter('C:/Users/jstreeck/Desktop/EndUse_shortTermSave/2020_NationalOfficial_IOSUT/USA/Benchmark_SUTIO/2007_2012_USA_SUT_497industries/WIO_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
filter_matrix.to_excel(writer,'Filter_Settings')
Cons_split.to_excel(writer,'Sheet4')
Cons_split_shares.to_excel(writer,'Sheet5')
Cons_agg_split.to_excel(writer,'Sheet6')
Cons_agg_split.to_excel(writer,'Sheet7')
writer.save()
      

'''
1.2) WASTE INPUT OUTPUT APPROACH TO MFA

 1.2.1) create filter matrices A_mp (materials to products) and A_pp (products to products) from filter setting'''

#read filter settings and create vectors for each filter category
filter_matrix = pd.read_excel('2007_2012_USA_SUT_497industries/Filter_WIObase_05072021_ExtensionAgg.xlsx',index_col=[0,1],header=[0,1])
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products_p1 = filter_matrix.loc[:,(['All'],['Products_p1'])]
products_p2 = filter_matrix.loc[:,(['All'],['Products_p2'])]
products = products_p1.to_numpy() + products_p2.to_numpy()
pre_material = filter_matrix.loc[:,(['All'],['Pre-material'])]
service = materials.to_numpy() + intermediates.to_numpy() + products + pre_material.to_numpy() 

#from filter categories create filter matrix A_mp for materials going to products
filt_Amp = np.ones_like(Z_icc)
filt_Amp = filt_Amp * materials.to_numpy() #only material extension sectors remain
filt_Amp = (filt_Amp.T * (np.ones_like(pre_material) - pre_material.to_numpy())).T #removes reverse flows in material extension rows; e.g. sawmills --> pulp production (as specified in filter)
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of material extension rows to service sectors if specified ('Yes') in filter matrix
    filt_Amp = (filt_Amp.T * service).T
np.fill_diagonal(filt_Amp, 0) #materials not made out of materials
filt_Amp_label = pd.DataFrame(data=filt_Amp, index= A_icc_label.index, columns=A_icc_label.columns)

#from filter categories create filter matrix A_pp for products going to products
filt_App = np.ones_like(Z_icc)
filt_App = filt_App  * (products + intermediates.to_numpy()) 
filt_App = (filt_App.T * (np.ones_like(pre_material) - pre_material.to_numpy())).T 
filt_App = (filt_App.T * (np.ones_like(materials) - materials.to_numpy())).T#removes reve #products cannot go back to materials or pre-materials, products cannot go back to intermediate, products can become products
filt_App = (filt_App.T * (np.ones_like(intermediates) - intermediates.to_numpy())).T #remove deliveries to intermediate
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of products to service sectors if specified in filter matrix
    filt_App = (filt_App.T * service).T 
#np.fill_diagonal(filt_App, 0)
filt_App_label = pd.DataFrame(data=filt_App, index= A_icc_label.index, columns=A_icc_label.columns)


'''
 1.2.2) create material composition matrix C multipliers for extension sectors'''

#filter technology matrix A according WIO-MFA filter settings as specified in 1.2.1
Amp_filt = A_icc * filt_Amp
App_filt = A_icc * filt_App

# calculate material composition matrix C with filtered A
I = np.eye(A_icc.shape[0])
C = np.dot(Amp_filt,np.linalg.inv(I-App_filt))
C_label = pd.DataFrame(data = (C), index = Z_icc.index, columns = Z_icc.index)

#recalculate total commodity output (x_icc_WIO) with C and calculate a dummy multiplier to check later if all extension-material is delivered to final demand (mass balance)
x_icc_WIO = np.dot(C, final_demand).reshape(-1,1)
mass_dummy = np.arange(1000,(np.shape(x_icc_WIO)[0]+1)*1000,1000,dtype=float).reshape(-1,1)
mass_dummy.reshape(-1,1)
mult = mass_dummy/x_icc_WIO
mult[mult == np.inf] = 0


'''
 1.2.3) calculate deliveries to final demand (multiplier x L_filt x final_demand)'''

mult_diag = pd.DataFrame(np.zeros_like(Z_icc), index=Z_icc.index, columns=Z_icc.columns)
np.fill_diagonal(mult_diag.values, mult)
finalDemand_diag = np.zeros_like(Z_icc)
np.fill_diagonal(finalDemand_diag, final_demand)

initiator = np.dot(mult_diag,C) 
WIO_split = pd.DataFrame(np.dot(initiator,finalDemand_diag),index=Z_icc.index, columns=Z_icc.columns)
WIO_split_colsum = WIO_split.sum(axis=1)

extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()

WIO_split_sectors = WIO_split.iloc[extension_sectors,:]
WIO_sum = WIO_split_sectors.sum(axis=1)
WIO_split_shares = WIO_split_sectors.divide(WIO_sum,axis=0).transpose()*100
#ratio_fd_x_ind =   final_demand.iloc[:,0].values / x_SUT.iloc[:401]   

#aggregate to level specified in Filter Settings
construction_agg = filter_matrix.loc[:,(['End-Use Category'],['Construction'])].iloc[:,0].to_numpy()#
machinery_agg = filter_matrix.loc[:,(['End-Use Category'],['Machinery'])].iloc[:,0].to_numpy()#
vehicles_agg = filter_matrix.loc[:,(['End-Use Category'],['Motor vehicles'])].iloc[:,0].to_numpy()#
otherTrans_agg = filter_matrix.loc[:,(['End-Use Category'],['Other transport equipment'])].iloc[:,0].to_numpy()#
other_agg = filter_matrix.loc[:,(['End-Use Category'],['Products nec'])].iloc[:,0].to_numpy()#
furniture_agg = filter_matrix.loc[:,(['End-Use Category'],['Furniture'])].iloc[:,0].to_numpy()#
extract_agg = filter_matrix.loc[:,(['End-Use Category'],['Extraction'])].iloc[:,0].to_numpy()#
textiles_agg = filter_matrix.loc[:,(['End-Use Category'],['Textiles'])].iloc[:,0].to_numpy()#
packaging_agg = filter_matrix.loc[:,(['End-Use Category'],['Packaging'])].iloc[:,0].to_numpy()#
services_agg = filter_matrix.loc[:,(['End-Use Category'],['Services'])].iloc[:,0].to_numpy()#
other2_agg = filter_matrix.loc[:,(['End-Use Category'],['Other'])].iloc[:,0].to_numpy()#
WIO_agg_split = pd.DataFrame({'Construction': WIO_split_shares[construction_agg == 1].sum(axis=0),'Machinery': WIO_split_shares[machinery_agg == 1].sum(axis=0),\
                          'Motor Vehicles': WIO_split_shares[vehicles_agg == 1].sum(axis=0),'Other Transport': WIO_split_shares[otherTrans_agg == 1].sum(axis=0),\
                              'Products nec': WIO_split_shares[other_agg == 1].sum(axis=0), 'Furniture': WIO_split_shares[furniture_agg == 1].sum(axis=0), \
                                  'Agri & Extraction': WIO_split_shares[extract_agg == 1].sum(axis=0), 'Textiles': WIO_split_shares[textiles_agg == 1].sum(axis=0), \
                                      'Packaging': WIO_split_shares[packaging_agg == 1].sum(axis=0), 'Services': WIO_split_shares[services_agg == 1].sum(axis=0),\
                                        'Other': WIO_split_shares[other2_agg == 1].sum(axis=0)} )
    
WIO_agg_split['Sum'] = WIO_agg_split.sum(axis=1)

''' 1.2.4) Recalculate Results with Hypothetical Extraction Method (HEM) for Packaging Sector'''

#set rows of packaging commodities to zero in technology matries A_mp, A_pp
packaging_rowCol = np.argwhere(packaging_agg== 1).tolist()
filt_Amp_noPack = filt_Amp
filt_Amp_noPack[packaging_rowCol,:] = 0
filt_App_noPack = filt_App
filt_App_noPack[packaging_rowCol,:] = 0
Amp_filt_noPack = Amp_filt * filt_Amp_noPack 
App_filt_noPack = App_filt * filt_App_noPack

#set rows for packaging commodities to zero in final demand vector
final_demand_noPack = final_demand
final_demand_noPack.iloc[packaging_rowCol,:] = 0

#recalculate total requirement matrix C and calculate deliveries to final demand
I = np.eye(A_icc.shape[0])
C_noPack = np.dot(Amp_filt_noPack,np.linalg.inv(I-App_filt_noPack))
C_noPack_label = pd.DataFrame(data = (C_noPack), index = Z_icc.index, columns = Z_icc.index)


finalDemand_noPack_diag = np.zeros_like(Z_icc)
np.fill_diagonal(finalDemand_noPack_diag , final_demand_noPack)

initiator = np.dot(mult_diag,C_noPack) 
WIO_split_noPack = pd.DataFrame(np.dot(initiator,finalDemand_noPack_diag),index=Z_icc.index, columns=Z_icc.columns)
WIO_split_noPack_colsum = WIO_split_noPack.sum(axis=1)


#sum up results and calculate shares of material going to different commodities
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()

WIO_split_sectors_noPack = WIO_split_noPack.iloc[extension_sectors,:]
WIO_split_sectors_noPack_sum = WIO_split_sectors_noPack.sum(axis=1)

env_ext = mass_dummy[extension_sectors]
WIO_split_shares_noPack = (WIO_split_sectors_noPack/env_ext).T

WIO_agg_split_noPack= pd.DataFrame({'Construction': WIO_split_shares_noPack[construction_agg == 1].sum(axis=0),'Machinery': WIO_split_shares_noPack[machinery_agg == 1].sum(axis=0),\
                          'Motor Vehicles': WIO_split_shares_noPack[vehicles_agg == 1].sum(axis=0),'Other Transport': WIO_split_shares_noPack[otherTrans_agg == 1].sum(axis=0),\
                              'Products nec': WIO_split_shares_noPack[other_agg == 1].sum(axis=0), 'Furniture': WIO_split_shares_noPack[furniture_agg == 1].sum(axis=0), \
                                  'Agri & Extraction': WIO_split_shares_noPack[extract_agg == 1].sum(axis=0), 'Textiles': WIO_split_shares_noPack[textiles_agg == 1].sum(axis=0), \
                                      'Packaging': WIO_split_shares_noPack[packaging_agg == 1].sum(axis=0), 'Services': WIO_split_shares_noPack[services_agg == 1].sum(axis=0),\
                                        'Other': WIO_split_shares_noPack[other2_agg == 1].sum(axis=0)} )
    
WIO_agg_split_noPack['Sum'] = WIO_agg_split_noPack.sum(axis=1)


#save run to Excel, together with filter matrices used
writer = pd.ExcelWriter('C:/Users/jstreeck/Desktop/EndUse_shortTermSave/2020_NationalOfficial_IOSUT/USA/Benchmark_SUTIO/2007_2012_USA_SUT_497industries/WIO_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
filter_matrix.to_excel(writer,'filter')
filt_Amp_label.to_excel(writer,'A_mp')
filt_App_label.to_excel(writer,'A_pp')
WIO_split.to_excel(writer,'WIO_split')
WIO_split_shares.to_excel(writer,'WIO_split_shares')
WIO_agg_split.to_excel(writer,'WIO_split_agg')
WIO_split_shares_noPack.to_excel(writer,'HEM_Packaging')
WIO_agg_split_noPack.to_excel(writer,'HEM_Packaging_agg')
writer.save()


'''
 1.3)-GHOSH-TYPE: INTERINDUSTRY MARKET SHARES'''

#read filter matrix from Excel
filter_matrix = pd.read_excel('2007_2012_USA_SUT_497industries/Filter_WIObase_05072021_ExtensionAgg.xlsx',index_col=[0,1],header=[0,1])

#create Ghosh-specific filter matrix from filter_matrix, by classifying commodities as intermediate or end-use
materials  = filter_matrix.loc[:,(['All'],['Materials'])]
intermediates = filter_matrix.loc[:,(['All'],['Intermediates_only'])]
products_p1 = filter_matrix.loc[:,(['All'],['Products_p1'])]
products_p2 = filter_matrix.loc[:,(['All'],['Products_p2'])]
products = products_p1.to_numpy() + products_p2.to_numpy()
pre_material = filter_matrix.loc[:,(['All'],['Pre-material'])]
service = materials.to_numpy() + intermediates.to_numpy() + products + pre_material.to_numpy() 

filt_Ghosh = np.ones_like(Z_icc)
intermediate_Ghosh = materials.to_numpy() + intermediates.to_numpy() + products_p1.to_numpy() 
filt_Ghosh = filt_Ghosh * intermediate_Ghosh #only intermediate product rows remain with value 1; all others 0
if filter_matrix.columns.get_level_values(1).name == 'Yes':  #removes deliveries of material extension rows to service sectors if specified in filter matrix
    filt_Ghosh= (filt_Ghosh.T * service).T
np.fill_diagonal(filt_Ghosh, 0) #materials not made out of materials
filt_Ghosh_label = pd.DataFrame(data=filt_Ghosh, index= A_icc_label.index, columns=A_icc_label.columns)


#apply Ghosh_filt to transaction matrix Z, calculate market share matrix B_Ghosh 
Z_method = Z_icc.copy()
Z_filt = Z_method  * filt_Ghosh
B_Ghosh = Z_filt.divide(Z_filt.sum(axis=1),axis=0).replace(np.nan,0.0)
B_Ghosh_sum = B_Ghosh.sum(axis=1) #check if column sum of B_Ghosh == 1 for intermediate commodity sectors
B_Ghosh = B_Ghosh.replace(np.inf,0)

#calculate supply chain distribution matrix G
I_agg =np.eye(B_Ghosh.shape[0])
G = np.linalg.inv(I_agg - B_Ghosh)

#delete columns of intermediate sectors in G; only keeping end-use commodity sectors
EndUse_filt = filt_Ghosh_label.T
EndUse_filt = EndUse_filt.replace(1,2).replace(0,1).replace(2,0)
Ghosh_split = G * EndUse_filt
np.fill_diagonal(Ghosh_split.values, 0) # fill diagonal with 0 
Ghosh_split_sum = Ghosh_split.sum(axis=1) # check if columns of end-uses sum up to 100%

#sum up results and calculate shares of material going to different commodities
extension_sectors = filter_matrix.loc[filter_matrix[('All','Materials')]== 1].index.get_level_values(0).to_list()
Ghosh_split_sectors = Ghosh_split.iloc[extension_sectors,:].T

#aggregate to level specified in Filter Settings
construction_agg = filter_matrix.loc[:,(['End-Use Category'],['Construction'])].iloc[:,0].to_numpy()#
machinery_agg = filter_matrix.loc[:,(['End-Use Category'],['Machinery'])].iloc[:,0].to_numpy()#
vehicles_agg = filter_matrix.loc[:,(['End-Use Category'],['Motor vehicles'])].iloc[:,0].to_numpy()#
otherTrans_agg = filter_matrix.loc[:,(['End-Use Category'],['Other transport equipment'])].iloc[:,0].to_numpy()#
other_agg = filter_matrix.loc[:,(['End-Use Category'],['Products nec'])].iloc[:,0].to_numpy()#
furniture_agg = filter_matrix.loc[:,(['End-Use Category'],['Furniture'])].iloc[:,0].to_numpy()#
extract_agg = filter_matrix.loc[:,(['End-Use Category'],['Extraction'])].iloc[:,0].to_numpy()#
textiles_agg = filter_matrix.loc[:,(['End-Use Category'],['Textiles'])].iloc[:,0].to_numpy()#
packaging_agg = filter_matrix.loc[:,(['End-Use Category'],['Packaging'])].iloc[:,0].to_numpy()#
services_agg = filter_matrix.loc[:,(['End-Use Category'],['Services'])].iloc[:,0].to_numpy()#
other2_agg = filter_matrix.loc[:,(['End-Use Category'],['Other'])].iloc[:,0].to_numpy()#
Ghosh_agg_split = pd.DataFrame({'Construction': Ghosh_split_sectors[construction_agg == 1].sum(axis=0),'Machinery': Ghosh_split_sectors[machinery_agg == 1].sum(axis=0),\
                          'Motor Vehicles': Ghosh_split_sectors[vehicles_agg == 1].sum(axis=0),'Other Transport': Ghosh_split_sectors[otherTrans_agg == 1].sum(axis=0),\
                              'Products nec': Ghosh_split_sectors[other_agg == 1].sum(axis=0), 'Furniture': Ghosh_split_sectors[furniture_agg == 1].sum(axis=0), \
                                  'Agri & Extraction': Ghosh_split_sectors[extract_agg == 1].sum(axis=0), 'Textiles': Ghosh_split_sectors[textiles_agg == 1].sum(axis=0), \
                                      'Packaging': Ghosh_split_sectors[packaging_agg == 1].sum(axis=0), 'Services': Ghosh_split_sectors[services_agg == 1].sum(axis=0),\
                                        'Other': Ghosh_split_sectors[other2_agg == 1].sum(axis=0)} )*100
    
Ghosh_agg_split['Sum'] = Ghosh_split.sum(axis=1)

#save run to Excel, together with filter matrices used
writer = pd.ExcelWriter('C:/Users/jstreeck/Desktop/EndUse_shortTermSave/2020_NationalOfficial_IOSUT/USA/Benchmark_SUTIO/2007_2012_USA_SUT_497industries/Ghosh_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
filter_matrix.to_excel(writer,'filter')

filter_matrix.to_excel(writer,'Filter_Settings')
B_Ghosh.to_excel(writer,'Market_Shares_B')
G.to_excel(writer,'Ghosh')
Ghosh_split.to_excel(writer,'Ghosh_split')
Ghosh_agg_split.to_excel(writer,'Ghosh_split_agg')
writer.save()
####
