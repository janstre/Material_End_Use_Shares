# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 18:28:37 2022

@author: jstreeck
"""
import os
import sys
import numpy as np
import pandas as pd
import glob
import statistics 

#define working directory and data paths
main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
path_input_data =  os.path.join(main_path, 'input_data/') 
data_path_usa = os.path.join(main_path, 'output/USA/')
data_path_exio = os.path.join(main_path, 'output/Exiobase/')

from EndUseShares_GraphsStatistics_functions_v1 import save_list2Excel, save_dict2Excel, calc_relDeviation, assemble_materialEndUse_df

'''
    #1 Load end-use shares for USA (national tables and Exiobase)
'''


years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]


#1 read files for all methods and years into dictionaries
CBA_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'CBA_' + str(year) + '_Base' + '*.xlsx'))):
        CBA_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    CBA_dict[year] = CBA_single
    

Wio_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'WIO_plain_' + str(year) + '_Base' + '*.xlsx'))):
        Wio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    Wio_dict[year] = Wio_single
    
Wio_ext_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'WIO_plain_' + str(year) + '_ExtAgg' + '*.xlsx'))):
        Wio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    Wio_ext_dict[year] = Wio_single

Wio_withServiceInput_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'WIO_withServiceInput_' + str(year) + '_Base' + '*.xlsx'))):
        Wio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    Wio_withServiceInput_dict[year] = Wio_single

Ghosh_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'GhoshAMC_plain_' + str(year) + '_Base' + '*.xlsx'))):
        Ghosh_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    Ghosh_dict[year] = Ghosh_single
    
ParGhosh_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'PartialGhoshIO_plain_' + str(year) + '_Base' + '*.xlsx'))):
        ParGhosh_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    ParGhosh_dict[year] = ParGhosh_single
    
EUTWio_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'EUT_WIOMF_' + str(year) + '_Base' + '*.xlsx'))):
        EUTWio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    EUTWio_dict[year] = EUTWio_single
    
EUTWio_ext_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'EUT_WIOMF_' + str(year) + '_ExtAgg' + '*.xlsx'))):
        EUTWio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    EUTWio_ext_dict[year] = EUTWio_single
    
EUTWio_detail_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'EUT_WIOMF_' + str(year) + '_Base' + '*.xlsx'))):
        EUTWio_detail_single = pd.read_excel(file, sheet_name='EndUse_shares',index_col=[0,1],header=[0,1])
    EUTWio_detail_dict[year] = EUTWio_detail_single 

# dictionary for industry shipments in physical units    
phys_materials = ['pd_IronSteel','pd_Alu','pd_Copper','pd_Wood','pd_Cement','pd_Plastics']
phys_dict = {}
for material in phys_materials:
    frame= pd.read_excel(path_input_data + '//Industry_Shipments//Shipments_USA.xlsx', sheet_name=material).set_index('Year')
    dict_ele = {material:frame}
    phys_dict.update(dict_ele)

# dictionary for USA from Exiobase    
year = 1995
years_exio = list(range(1995,2012))   
regions = ['US'] 

# assemble EXIOBASE dictionary per region and year
Exio_dict = {}
for region in regions:
    Region_dict = {}
    for year in years_exio:
        for file in glob.glob(os.path.join((data_path_exio + 'Exio_EUT_WIOMF_' + str(year) + '_' + region + '*.xlsx'))):
            Region_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0])
        Region_dict[year] = Region_single
    Exio_dict[region] = Region_dict

# single country all end-uses plot:
materials = ['steel', 'wood', 'Plastic', 'glass', 'alumin', 'tin', 'Copper']

# assemble EXIOBASE dictionary per region and material
region_dict ={}
for region in regions:
    material_dict = []
    for material in materials:
        material_single = []
        material_df = pd.DataFrame([], index=Exio_dict.get(region).get(year).index.get_level_values(1), columns=years_exio)
        for year in years_exio:
            material_single = Exio_dict.get(region).get(year).iloc[:,Exio_dict.get(region).get(year).columns.get_level_values(0).map(lambda t: (material) in t).to_list()]
            material_df[year] = material_single.values
        material_dict.append(material_df)        
        dict_1 = dict(zip(materials,material_dict))
    region_dict.update({region:dict_1})

# SAVE selected dictionary to Excel    
# path = './output/USA/FiguresStats/' + 'EUTWIO_fullResults_USA'  
# save_dict2Excel(path, EUTWio_dict )  

'''
    #2 Assemble detailed comparison for USA national data + shipments + Exiobase (selected method)
'''

years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]

methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict] 
method_names = ['CBA', 'WIO-MFA', 'Ghosh-IO AMC', 'Partial Ghosh-IO', 'EUT-WIO' ]

# re-assemble data to dataframes per material and end-use
plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
    alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
    copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
    steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
    cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df  = assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict)



'''STATISTICS'''

# assemble lists for calculating relative deviations of MIOT-based results (EUT-WIO) to industry shipments with median, min, max, percentiles

figure2_overall_dev = [ wood_construction_df, wood_transport_df,wood_packaging_food_df, wood_machinery_df, wood_furniture_df,\
              steel_construction_df, steel_transport_df,  steel_packaging_food_df, steel_machinery_df, steel_furniture_df,\
              copper_construction_df, copper_transport_df,  copper_machinery_df, copper_furniture_df,\
              alu_construction_df, alu_transport_df, alu_packaging_food_df, alu_machinery_df, alu_furniture_df, \
              plastic_construction_df, plastic_transport_df, plastic_packaging_food_df, plastic_electrical_df, plastic_furniture_df]
    
    
figure2_elements = ['(a) wood_construction_df','(b) wood_transport_df','(c) wood_packaging_food_df', '(d) wood_machinery_df', '(e) wood_furniture_df',\
              '(f) steel_construction_df', '(g) steel_transport_df',  '(h) steel_packaging_food_df', '(i) steel_machinery_df',  '(j) steel_furniture_df',\
              '(k) copper_construction_df', '(l) copper_transport_df', '(m) copper_machinery_df', '(n) copper_furniture_df',\
              '(o) alu_construction_df', '(p) alu_transport_df', '(q) alu_packaging_food_df', '(r) alu_machinery_df', '(s) alu_furniture_df', \
              '(t) plastic_construction_df', '(u) plastic_transport_df',  '(v) plastic_packaging_food_df', '(w) plastic_electrical_df', '(x) plastic_furniture_df']

#per material
plastics_stats = [plastic_construction_df, plastic_transport_df, plastic_packaging_food_df, plastic_electrical_df, plastic_furniture_df]
alu_stats = [alu_construction_df, alu_transport_df, alu_packaging_food_df, alu_machinery_df, alu_furniture_df]
steel_stats = [steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_furniture_df]
wood_stats = [wood_construction_df, wood_transport_df,wood_packaging_food_df, wood_machinery_df, wood_furniture_df]
copper_stats = [copper_construction_df, copper_transport_df,  copper_machinery_df, copper_furniture_df]
                             
#per end-use category
construction_stats = [plastic_construction_df,copper_construction_df, wood_construction_df, steel_construction_df,alu_construction_df]
transport_stats = [plastic_transport_df, alu_transport_df, steel_transport_df, copper_transport_df, wood_transport_df]
machinery_stats = [plastic_electrical_df,alu_machinery_df,steel_machinery_df, wood_machinery_df, copper_machinery_df]
packaging_stats = [plastic_packaging_food_df, alu_packaging_food_df, steel_packaging_food_df, wood_packaging_food_df]

#####################    



#####

'''
STATS 1: calculate the relative deviation of EUT-WIO from industry shipment datasources
'''

analysis_list = ['figure2_overall_dev', 'plastics_stats', 'alu_stats', 'steel_stats', 'wood_stats', 'copper_stats', 'construction_stats', \
                 'transport_stats', 'machinery_stats', 'packaging_stats']
                 
    
analysis_list_eval = [eval(x) for x in analysis_list]
analysis_dict_1 = {}

k=0
for i in analysis_list_eval:
    total_deviation = []
    rel_deviation = []
    for frame in i:
        try:
            frame['EUT-Shipment1'] = frame['EUT-WIO'] - frame['Shipment_1']
            frame['EUT-Shipment1_rel']  = (frame['EUT-WIO'] - frame['Shipment_1'])/frame['Shipment_1']
            total_deviation.append(frame['EUT-Shipment1'].dropna().values.tolist())
            rel_deviation.append(frame['EUT-Shipment1_rel'].dropna().values.tolist())
        except:
            pass
        try:
            frame['EUT-Shipment2']  = frame['EUT-WIO'] - frame['Shipment_2']
            total_deviation.append(frame['EUT-Shipment2'].dropna().values.tolist())
            frame['EUT-Shipment2_rel']  = (frame['EUT-WIO'] - frame['Shipment_2'])/frame['Shipment_2']
            total_deviation.append(frame['EUT-Shipment2'].dropna().values.tolist())
            rel_deviation.append(frame['EUT-Shipment2_rel'].dropna().values.tolist())
        except:
            pass
        try:
            frame['EUT-Shipment3']  = frame['EUT-WIO'] - frame['Shipment_3']
            frame['EUT-Shipment3_rel']  = (frame['EUT-WIO'] - frame['Shipment_3'])/frame['Shipment_3']
            total_deviation.append(frame['EUT-Shipment3'].dropna().values.tolist())
            rel_deviation.append(frame['EUT-Shipment3_rel'].dropna().values.tolist())
        except:
            pass
        
    rel_deviation_abs =  [abs(x) for x in sum(rel_deviation, [])]
    rel_dev_mean = sum(rel_deviation_abs )/len(rel_deviation_abs )
    rel_dev_med = statistics.median(rel_deviation_abs )
    quantiles = statistics.quantiles(rel_deviation_abs,  n=40, method='exclusive')
    lower = quantiles[0] - rel_dev_med
    upper = quantiles[-1] - rel_dev_med
    maxim = max(rel_deviation_abs)
    minim = min(rel_deviation_abs)
    
    
    stat_dict = pd.DataFrame([[{'absolutes_rel_dev':rel_deviation_abs,'rel_dev_mean':rel_dev_mean, 'rel_dev_med':rel_dev_med, 'lower':lower,
                           'upper':upper, 'quantiles2.5':quantiles, 'maxim':maxim, 'minum':minim }]])
    analysis_dict_1[analysis_list[k]] = stat_dict
    
    k = k+1

# SAVE (optional)
writer = pd.ExcelWriter('./output/USA/FiguresStats/' + 'DeviationStats_ShipmentEUTWIO' + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
for df_name, df in analysis_dict_1.items():
    df.to_excel(writer, sheet_name=df_name)
writer.save()

##########


'''
STATS 2: calculate the relative deviation of USA national official MIOTs to EXIOBASE data for FIGURE2 plots (for EUT-WIO)
'''

analysis_list_eval = []
for x in figure2_elements:
    analysis_list_eval.append([eval(x[4:])])
    
analysis_dict_2 = {}

k=0
for i in analysis_list_eval:
    total_deviation = []
    rel_deviation = []
    for frame in i:
        try:
            frame['USA-Exio'] = frame['EUT-WIO'] - frame['Exio_EUT-WIO']
            frame['USA-Exio_rel']  = (frame['EUT-WIO'] - frame['Exio_EUT-WIO'])/frame['Exio_EUT-WIO']
            total_deviation.append(frame['USA-Exio'].dropna().values.tolist())
            rel_deviation.append(frame['USA-Exio_rel'].dropna().values.tolist())
        except:
            pass      
    
    try:
        rel_deviation_abs =  [abs(x) for x in sum(rel_deviation, [])]
        rel_dev_mean = sum(rel_deviation_abs )/len(rel_deviation_abs )
        rel_dev_med = statistics.median(rel_deviation_abs )
        quantiles = statistics.quantiles(rel_deviation_abs,  n=40, method='exclusive')
        lower = quantiles[0] - rel_dev_med
        upper = quantiles[-1] - rel_dev_med
        maxim = max(rel_deviation_abs)
        minim = min(rel_deviation_abs)
    except:
        pass      

    stat_dict = pd.DataFrame([[{'absolutes_rel_dev':rel_deviation_abs,'rel_dev_mean':rel_dev_mean, 'rel_dev_med':rel_dev_med, 'lower':lower,
                           'upper':upper, 'quantiles2.5':quantiles, 'maxim':maxim, 'minum':minim }]])
    analysis_dict_2[figure2_elements[k]] = stat_dict
    
    k = k+1

# SAVE (optional)
writer = pd.ExcelWriter('./output/USA/FiguresStats/' + 'DeviationStats_NationalExioEUTWIO' + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
for df_name, df in analysis_dict_2.items():
    df.to_excel(writer, sheet_name=df_name)
writer.save()


##### for EXIOBASE, differences of industry shipments and MIOT-based results are directly added to FIGURE 4 dataframes and can be found in 
##### script 'EndUseShares_Graphs__Outputs_v1'