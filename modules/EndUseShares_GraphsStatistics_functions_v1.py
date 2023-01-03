# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 17:11:33 2022

@author: jstreeck
"""
import os
import sys
import numpy as np
import pandas as pd
import glob
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from openpyxl import load_workbook


def save_list2Excel(path, matEndUse_nameList, matEndUse_dfList):
    list2dict = dict(zip(matEndUse_nameList, matEndUse_dfList))
    writer = pd.ExcelWriter(path + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    for df_name, df in  list2dict.items():
        df.to_excel(writer, sheet_name=df_name)
    writer.save()
    
####################


def save_dict2Excel(path, diction):
    writer = pd.ExcelWriter(path + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    for df_name, df in  diction.items():
        df.to_excel(writer, sheet_name=str(df_name))
    writer.save()

####################


'''Calculate deviation of EUT-WIO and Industry Shipments
per dataframe'''

def calc_relDeviation(frame):
    import statistics 
    
    frame_cop = frame.copy()
    rel_deviation = []
    try:
        frame_cop['EUT-Shipment1'] = frame_cop['EUT-WIO'] - frame_cop['Shipment_1']
        frame_cop['EUT-Shipment1_rel']  = (frame_cop['EUT-WIO'] - frame_cop['Shipment_1'])/frame_cop['Shipment_1']
        rel_deviation.append(frame_cop['EUT-Shipment1_rel'].dropna().values.tolist())
    except Exception:
        pass   
    try:
        frame_cop['EUT-Shipment2']  = frame_cop['EUT-WIO'] - frame_cop['Shipment_2']
        frame_cop['EUT-Shipment2_rel']  = (frame_cop['EUT-WIO'] - frame_cop['Shipment_2'])/frame_cop['Shipment_2']
        rel_deviation.append(frame_cop['EUT-Shipment2_rel'].dropna().values.tolist())
    except Exception:
        pass
    try:
        frame_cop['EUT-Shipment3']  = frame_cop['EUT-WIO'] - frame_cop['Shipment_3']
        frame_cop['EUT-Shipment3_rel']  = (frame_cop['EUT-WIO'] - frame_cop['Shipment_3'])/frame_cop['Shipment_3']
        rel_deviation.append(frame_cop['EUT-Shipment3_rel'].dropna().values.tolist())
    except Exception:
        pass
    
    
    rel_deviation_abs =  [abs(x) for x in sum(rel_deviation, [])]
    rel_dev_med = statistics.median(rel_deviation_abs )
    maxim = max(rel_deviation_abs)
    minim = min(rel_deviation_abs)
    return rel_dev_med, minim, maxim

####################


'''Assemble end-use dataframes by material 
for USA'''

def assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict ):
        
    '''USA - - WOOD'''
    
    year = 1963
    Wood_dict = {}
    count = -1
    for method in methods:
        wood_single = []
        Wood_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
        count= count +1
        for year in years:
            wood_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('Sawmill' or 'Wood') in t).to_list()]
            Wood_df[year] = wood_single.values
        Wood_dict[(method_names[count])] = Wood_df
            
    #construction
    wood_construction_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_construction_df[method_name] = Wood_dict.get(method_name).loc['Residential'] + Wood_dict.get(method_name).loc['Non-Residential'] + Wood_dict.get(method_name).loc['Other buildings'] + Wood_dict.get(method_name ).loc['Infrastructure'] + Wood_dict.get(method_name).loc['Other construction']
    wood_construction_df['Shipment_1'] = phys_dict.get('pd_Wood').T.loc['Construction total']*100 #'McKeever_constr.
    wood_construction_df['Exio_EUT-WIO'] = region_dict.get('US').get('wood').loc['Construction']
    
    #residential
    wood_residential_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_residential_df[method_name] = Wood_dict.get(method_name).loc['Residential']
    wood_residential_df['Shipment_1'] = phys_dict.get('pd_Wood').T.loc['Total New Houses']*100 #'McKeever_resid.build.new.'
    
    #non-residential
    wood_nonresidential_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_nonresidential_df[method_name] = Wood_dict.get(method_name).loc['Non-Residential']
    wood_nonresidential_df['Shipment_1'] = phys_dict.get('pd_Wood').T.loc['Nonres Total']*100 #'McKeever_non.resid.constr.'
    
    #furniture
    wood_furniture_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_furniture_df[method_name] = Wood_dict.get(method_name).loc['Furniture']
    wood_furniture_df['Shipment_1'] = phys_dict.get('pd_Wood').T.loc['Furniture']*100 #'McKeever_furnit.'
    wood_furniture_df['Exio_EUT-WIO'] = region_dict.get('US').get('wood').loc['Furniture; other manufactured goods n.e.c.']
    
    #packaging
    wood_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_packaging_food_df[method_name] = Wood_dict.get(method_name).loc['Packaging']  + Wood_dict.get(method_name).loc['Food products']
    wood_packaging_food_df['Shipment_1'] = phys_dict.get('pd_Wood').T.loc['Packaging and shippling']*100 #'McKeever_packag.'
    wood_packaging_food_df['Exio_EUT-WIO'] = region_dict.get('US').get('wood').loc['Food']
    
    #transport
    wood_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_transport_df[method_name] = Wood_dict.get(method_name).loc['Motor vehicles'] + Wood_dict.get(method_name).loc['Other transport equipment']
    wood_transport_df['Exio_EUT-WIO'] = region_dict.get('US').get('wood').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('wood').loc['Other transport equipment']
    
    #machinery
    wood_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_machinery_df[method_name] = Wood_dict.get(method_name).loc['Electronic machinery'] + Wood_dict.get(method_name).loc['Other machinery']
    wood_machinery_df['Exio_EUT-WIO'] = region_dict.get('US').get('wood').loc['Machinery and equipment n.e.c. '] +\
        region_dict.get('US').get('wood').loc['Electrical machinery and apparatus n.e.c.']
    
    
    '''USA - - ALUMINUM'''
    
    alu_dict = {}
    count = -1
    for method in methods:
        alu_single = []
        alu_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
        count= count +1
        for year in years:
            alu_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('alu' or 'Alu') in t).to_list()]
            alu_df[year] = alu_single.values
        alu_dict[(method_names[count])] = alu_df
    
    #construction
    alu_construction_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_construction_df[method_name] = alu_dict.get(method_name).loc['Residential'] + alu_dict.get(method_name).loc['Non-Residential'] + alu_dict.get(method_name).loc['Other buildings'] + alu_dict.get(method_name ).loc['Infrastructure'] + alu_dict.get(method_name).loc['Other construction']
    alu_construction_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Construction']*100
    alu_construction_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Building & Construction']*100
    alu_construction_df['Exio_EUT-WIO'] = region_dict.get('US').get('alumin').loc['Construction']
    
    #transport
    alu_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_transport_df[method_name] = alu_dict.get(method_name).loc['Motor vehicles'] + alu_dict.get(method_name).loc['Other transport equipment']
    alu_transport_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Transportation']*100
    alu_transport_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Transportation']*100
    alu_transport_df['Exio_EUT-WIO'] = region_dict.get('US').get('alumin').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('alumin').loc['Other transport equipment']
    
    #packaging (assuming that also material in 'food products' is packaging)
    alu_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_packaging_food_df[method_name] = alu_dict.get(method_name).loc['Packaging'] + alu_dict.get(method_name).loc['Food products']
    alu_packaging_food_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Containers and packaging']*100
    alu_packaging_food_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Containers and packaging']*100
    alu_packaging_food_df['Exio_EUT-WIO'] = region_dict.get('US').get('alumin').loc['Food']
    
    #machinery
    alu_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_machinery_df[method_name] = alu_dict.get(method_name).loc['Electronic machinery'] + alu_dict.get(method_name).loc['Other machinery']
    alu_machinery_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Electrical']*100 +phys_dict.get('pd_Alu').T.loc['USGS Machinery and equipment']*100 #USGS_mach.&equipm.+electrical'
    alu_machinery_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Electrical']*100 +phys_dict.get('pd_Alu').T.loc['Liu Machinery and equipment']*100 #Liu_mach.&equipm.+electrical'
    alu_machinery_df['Exio_EUT-WIO'] = region_dict.get('US').get('alumin').loc['Machinery and equipment n.e.c. '] +\
        region_dict.get('US').get('alumin').loc['Electrical machinery and apparatus n.e.c.']
    
    #machinery electrical
    alu_machineryElectric_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_machineryElectric_df[method_name] = alu_dict.get(method_name).loc['Electronic machinery'] 
    alu_machineryElectric_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Electrical']*100 
    alu_machineryElectric_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Electrical']*100 
    
    #machinery other
    alu_machineryOther_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_machineryOther_df[method_name] = alu_dict.get(method_name).loc['Other machinery']
    alu_machineryOther_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Machinery and equipment']*100
    alu_machineryOther_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Machinery and equipment']*100
    
    #furniture
    alu_furniture_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_furniture_df[method_name] = alu_dict.get(method_name).loc['Furniture']
    alu_furniture_df['Exio_EUT-WIO'] = region_dict.get('US').get('alumin').loc['Furniture; other manufactured goods n.e.c.']
    
    
    '''USA - - STEEL'''
    
    steel_dict = {}
    count = -1
    for method in methods:
        steel_single = []
        steel_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
        count= count +1
        for year in years:
            steel_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('steel' or 'Blast') in t).to_list()]
            steel_df[year] = steel_single.values
        steel_dict[(method_names[count])] = steel_df
            
    #construction
    steel_construction_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_construction_df[method_name] = steel_dict.get(method_name).loc['Residential'] + steel_dict.get(method_name).loc['Non-Residential'] + steel_dict.get(method_name).loc['Other buildings'] + steel_dict.get(method_name).loc['Infrastructure'] + steel_dict.get(method_name).loc['Other construction']
    steel_construction_df['Shipment_1'] = phys_dict.get('pd_IronSteel').T.loc['Construction USGS+Trade']*100
    steel_construction_df['Shipment_2'] = phys_dict.get('pd_IronSteel').T.loc['Construction YSTAFB']*100
    steel_construction_df['Shipment_3'] = phys_dict.get('pd_IronSteel').T.loc['Construction Pauliuk']*100
    steel_construction_df['Exio_EUT-WIO'] = region_dict.get('US').get('steel').loc['Construction']
    
    #transport
    steel_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_transport_df[method_name] = steel_dict.get(method_name).loc['Motor vehicles'] + steel_dict.get(method_name).loc['Other transport equipment']
    steel_transport_df['Shipment_1'] = phys_dict.get('pd_IronSteel').T.loc['Transportation USGS+Trade']*100
    steel_transport_df['Shipment_2'] = phys_dict.get('pd_IronSteel').T.loc['Transport YSTAFB']*100
    steel_transport_df['Shipment_3'] = phys_dict.get('pd_IronSteel').T.loc['Automotive Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
        + phys_dict.get('pd_IronSteel').T.loc['Shipbuilding Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Aircraft Pauliuk']*100
    steel_transport_df['Exio_EUT-WIO'] = region_dict.get('US').get('steel').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('steel').loc['Other transport equipment']
    
    #packaging (assuming that also material in 'food products' is packaging)
    steel_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_packaging_food_df[method_name] = steel_dict.get(method_name).loc['Packaging'] + steel_dict.get(method_name).loc['Food products']
    steel_packaging_food_df['Shipment_1'] = phys_dict.get('pd_IronSteel').T.loc['Containers USGS+Trade']*100
    steel_packaging_food_df['Exio_EUT-WIO'] = region_dict.get('US').get('steel').loc['Food']
    steel_packaging_food_df['Shipment_3'] = phys_dict.get('pd_IronSteel').T.loc['Containers, shipping materials Pauliuk']*100
    
    #machinery
    steel_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_machinery_df[method_name] = steel_dict.get(method_name).loc['Other machinery'] + steel_dict.get(method_name).loc['Electronic machinery']
    steel_machinery_df['Shipment_2'] = phys_dict.get('pd_IronSteel').T.loc['Machinery & Appliances YSTAFB']*100
    steel_machinery_df['Exio_EUT-WIO'] = region_dict.get('US').get('steel').loc['Machinery and equipment n.e.c. '] +\
        region_dict.get('US').get('steel').loc['Electrical machinery and apparatus n.e.c.']
    steel_machinery_df['Shipment_3'] = phys_dict.get('pd_IronSteel').T.loc['Machinery Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
            + phys_dict.get('pd_IronSteel').T.loc['Electrical Equipment Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Appliances Pauliuk']*100
    
    #remainder (not including furniture)
    steel_remainder_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_remainder_df[method_name] = 100 - (steel_dict.get(method_name).loc['Other machinery'] + \
        steel_dict.get(method_name).loc['Packaging'] + steel_dict.get(method_name).loc['Food products']+\
        steel_dict.get(method_name).loc['Motor vehicles'] + steel_dict.get(method_name).loc['Other transport equipment'] +\
        steel_dict.get(method_name).loc['Residential'] + steel_dict.get(method_name).loc['Non-Residential'] + steel_dict.get(method_name).loc['Other buildings'] + steel_dict.get(method_name).loc['Infrastructure'] + steel_dict.get(method_name).loc['Other construction'])
    steel_remainder_df['Shipment_1'] = phys_dict.get('pd_IronSteel').T.loc['Service centers and distributors USGS+Trade']*100 +\
        phys_dict.get('pd_IronSteel').T.loc['Other USGS+Trade']*100 + phys_dict.get('pd_IronSteel').T.loc['Undistributed USGS+Trade']*100
    steel_remainder_df['Shipment_2'] = phys_dict.get('pd_IronSteel').T.loc['Other products YSTAFB']*100
    steel_remainder_df['Shipment_3'] = 100 - (phys_dict.get('pd_IronSteel').T.loc['Containers, shipping materials Pauliuk']*100 +\
        phys_dict.get('pd_IronSteel').T.loc['Automotive Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
            + phys_dict.get('pd_IronSteel').T.loc['Shipbuilding Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Aircraft Pauliuk']*100 +\
              phys_dict.get('pd_IronSteel').T.loc['Construction Pauliuk']*100 +  phys_dict.get('pd_IronSteel').T.loc['Machinery Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
                      + phys_dict.get('pd_IronSteel').T.loc['Electrical Equipment Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Appliances Pauliuk']*100)
    
    #furniture
    steel_furniture_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_furniture_df[method_name] = steel_dict.get(method_name).loc['Furniture']
    steel_furniture_df['Exio_EUT-WIO'] = region_dict.get('US').get('steel').loc['Furniture; other manufactured goods n.e.c.']
    
    
    '''USA - - COPPER ''' 
    
    years_cop = [1963,1967,1972,1977,1982,1987,1992]
    years_cop2 =  [1997]
    years_cop3 = [2002]
    years_cop4 = [2007,2012]
    copper_dict = {}
    count = -1
    for method in methods:
        copper_single = []
        copper_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
        count= count +1
        for year in years_cop:
            copper_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(0).astype(str).map(lambda t: ('3801' ) in t).to_list()]
            copper_df[year] = copper_single.values
        copper_dict[(method_names[count])] = copper_df 
        for year2 in years_cop2:
            copper_single = method.get(year2).iloc[:,method.get(year2).columns.get_level_values(1).map(lambda t: ('smelting') in t).to_list()]
            copper_df[year2] = copper_single.values
        copper_dict[(method_names[count])] = copper_df
        for year3 in years_cop3:
            copper_single = method.get(year3).iloc[:,method.get(year3).columns.get_level_values(0).astype(str).map(lambda t: ('331411') in t).to_list()]
            copper_df[year3] = copper_single.values
        copper_dict[(method_names[count])] = copper_df
        for year4 in years_cop4:
            copper_single = method.get(year4).iloc[:,method.get(year4).columns.get_level_values(1).map(lambda t: ('Copper') in t).to_list()]
            copper_df[year4] = copper_single.values
        copper_dict[(method_names[count])] = copper_df
           
    #construction
    copper_construction_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_construction_df[method_name] = copper_dict.get(method_name).loc['Residential'] + copper_dict.get(method_name).loc['Non-Residential'] + copper_dict.get(method_name).loc['Other buildings'] + copper_dict.get(method_name).loc['Infrastructure'] + copper_dict.get(method_name).loc['Other construction']
    copper_construction_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Building construction USGS+Trade']*100
    copper_construction_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Building construction CDA+Trade']*100
    copper_construction_df['Exio_EUT-WIO'] = region_dict.get('US').get('Copper').loc['Construction']
    
    #transportation
    copper_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_transport_df[method_name] = copper_dict.get(method_name).loc['Motor vehicles'] + copper_dict.get(method_name).loc['Other transport equipment']
    copper_transport_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Transportation equipment USGS+Trade']*100
    copper_transport_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Transportation equipment CDA+Trade']*100
    copper_transport_df['Exio_EUT-WIO'] = region_dict.get('US').get('Copper').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('Copper').loc['Other transport equipment']
    
    #machinery
    copper_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_machinery_df[method_name] = copper_dict.get(method_name).loc['Electronic machinery'] + copper_dict.get(method_name).loc['Other machinery']
    copper_machinery_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products USGS+Trade']*100 +phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment USGS+Trade']*100
    copper_machinery_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products CDA+Trade']*100 +phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment CDA+Trade']*100
    copper_machinery_df['Exio_EUT-WIO'] = region_dict.get('US').get('Copper').loc['Machinery and equipment n.e.c. '] +\
        region_dict.get('US').get('Copper').loc['Electrical machinery and apparatus n.e.c.']
    
    #machinery electrical
    copper_machineryElectric_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_machineryElectric_df[method_name] = copper_dict.get(method_name).loc['Electronic machinery'] 
    copper_machineryElectric_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products USGS+Trade']*100
    copper_machineryElectric_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products CDA+Trade']*100
    
    #machinery other
    copper_machineryOther_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_machineryOther_df[method_name] = copper_dict.get(method_name).loc['Other machinery']
    copper_machineryOther_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment USGS+Trade']*100
    copper_machineryOther_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment CDA+Trade']*100
    
    #furniture
    copper_furniture_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_furniture_df[method_name] = copper_dict.get(method_name).loc['Furniture']
    copper_furniture_df['Exio_EUT-WIO'] = region_dict.get('US').get('Copper').loc['Furniture; other manufactured goods n.e.c.']
    
    
    '''USA - - CEMENT''' 
    
    cement_dict = {}
    count = -1
    for method in methods:
        cement_single = []
        cement_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
        count= count +1
        for year in years:
            cement_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('Cement' or 'cement') in t).to_list()]
            cement_df[year] = cement_single.values
        cement_dict[(method_names[count])] = cement_df
    
    #residential
    cement_residential_df = pd.DataFrame([], index=list(range(1963,2017)), columns=method_names)
    for method_name in method_names:
        cement_residential_df[method_name] = cement_dict.get(method_name).loc['Residential']
    cement_residential_df['Shipment_1'] = phys_dict.get('pd_Cement').T.loc['Residential PCA']*100 #'PCA_resid.buildings'
    cement_residential_df['Shipment_2'] = phys_dict.get('pd_Cement').T.loc['Residential Cao']*100 #'Cao_resid.building'
    cement_residential_df['Shipment_3'] = phys_dict.get('pd_Cement').T.loc['Residential buildings PCA Kapur & web']*100
    
    #non-residential
    cement_nonresidential_df = pd.DataFrame([], index=list(range(1963,2017)), columns=method_names)
    for method_name in method_names:
        cement_nonresidential_df[method_name] = cement_dict.get(method_name).loc['Non-Residential']
    cement_nonresidential_df['Shipment_1'] = phys_dict.get('pd_Cement').T.loc['Nonresidential buildings PCA']*100 #'PCA_nonres.buildings
    cement_nonresidential_df['Shipment_2'] = phys_dict.get('pd_Cement').T.loc['Non-Residential Cao']*100 #'Cao_nonres.building'
    cement_nonresidential_df['Shipment_3'] = phys_dict.get('pd_Cement').T.loc['Commercial buildings PCA Kapur & web']*100 + \
        phys_dict.get('pd_Cement').T.loc['Public Buildings PCA Kapur & web']*100 + phys_dict.get('pd_Cement').T.loc['Farm construction PCA Kapur & web']*100
    
    #civil engineering
    cement_civil_engineering_df = pd.DataFrame([], index=list(range(1963,2017)), columns=method_names)
    for method_name in method_names:
        cement_civil_engineering_df[method_name] = cement_dict.get(method_name).loc['Infrastructure'] + cement_dict.get(method_name).loc['Other construction']
    cement_civil_engineering_df['Shipment_1'] = phys_dict.get('pd_Cement').T.loc['Civil engineering/Infra']*100 + phys_dict.get('pd_Cement').T.loc['Highways & Streets']*100 #'PCA_civ.eng+streets'
    cement_civil_engineering_df['Shipment_2'] = phys_dict.get('pd_Cement').T.loc['Civil Engineering Cao']*100
    cement_civil_engineering_df['Shipment_3'] = phys_dict.get('pd_Cement').T.loc['Utilities PCA Kapur & web']*100 + \
        phys_dict.get('pd_Cement').T.loc['Streets and Highways PCA Kapur & web']*100 + phys_dict.get('pd_Cement').T.loc['Others PCA Kapur & web']*100\
            + phys_dict.get('pd_Cement').T.loc['Water and waste management PCA Kapur & web']*100 #'PCAKapur_util.+streets+other'
    
    
    '''USA - - PLASTICS''' 
    
    plastic_dict = {}
    count = -1
    for method in methods:
        plastic_single = []
        plastic_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
        count= count +1
        for year in years:
            plastic_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('Plastic' or 'plastic') in t).to_list()]
            plastic_df[year] = plastic_single.values
        plastic_dict[(method_names[count])] = plastic_df
    
    #construction
    plastic_construction_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_construction_df[method_name] = plastic_dict.get(method_name).loc['Residential'] + plastic_dict.get(method_name).loc['Non-Residential'] + plastic_dict.get(method_name).loc['Other buildings'] + plastic_dict.get(method_name).loc['Infrastructure'] + plastic_dict.get(method_name).loc['Other construction']
    plastic_construction_df['Shipment_1'] = phys_dict.get('pd_Plastics').T.loc['Construction industry Euromap USA']*100
    plastic_construction_df['Shipment_2'] = phys_dict.get('pd_Plastics').T.loc['Building and construction PE']*100 #'PlasticsEurope_EU_'
    plastic_construction_df['Exio_EUT-WIO'] = region_dict.get('US').get('Plastic').loc['Construction']
    
    #packaging (assuming that also material in 'food products' is packaging)
    plastic_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_packaging_food_df[method_name] = plastic_dict.get(method_name).loc['Packaging'] + plastic_dict.get(method_name).loc['Food products'] 
    plastic_packaging_food_df['Shipment_1'] = phys_dict.get('pd_Plastics').T.loc['Packaging Euromap USA']*100
    plastic_packaging_food_df['Shipment_2'] = phys_dict.get('pd_Plastics').T.loc['Packaging PE']*100 #'PlasticsEurope_EU_packag.'
    plastic_packaging_food_df['Exio_EUT-WIO'] = region_dict.get('US').get('Plastic').loc['Food']
    
    #transport (assuming that also material in 'food products' is transport)
    plastic_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_transport_df[method_name] = plastic_dict.get(method_name).loc['Motor vehicles'] + plastic_dict.get(method_name).loc['Other transport equipment'] 
    plastic_transport_df['Shipment_1'] = phys_dict.get('pd_Plastics').T.loc['Automotive Euromap USA']*100
    plastic_transport_df['Shipment_2'] = phys_dict.get('pd_Plastics').T.loc['Automotive PE']*100
    plastic_transport_df['Exio_EUT-WIO'] = region_dict.get('US').get('Plastic').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('Plastic').loc['Other transport equipment']
    
    #electronics (assuming that also material in 'food products' is transport)
    plastic_electrical_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_electrical_df[method_name] = plastic_dict.get(method_name).loc['Electronic machinery']  
    plastic_electrical_df['Shipment_1'] = phys_dict.get('pd_Plastics').T.loc['Electrical, electronics & telecom Euromap USA']*100
    plastic_electrical_df['Shipment_2'] = phys_dict.get('pd_Plastics').T.loc['Electrical&Electronic PE']*100
    
    #furniture
    plastic_furniture_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_furniture_df[method_name] = plastic_dict.get(method_name).loc['Furniture']
    plastic_furniture_df['Exio_EUT-WIO'] = region_dict.get('US').get('Plastic').loc['Furniture; other manufactured goods n.e.c.']
    
    return plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
        alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
        copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
        steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
        cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df
        
####################       


'''Load MIOT-based and industry shipment 
data for USA (for standard MIOT methods)'''

def load_data_USA(path_input_data, data_path_usa,data_path_exio):
    years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]

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
        
    # dictionary for USA from EXIOBASE    
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

    # assemble EXIOBASE dictionary per region and material
    materials = ['steel', 'wood', 'Plastic', 'glass', 'alumin', 'tin', 'Copper']

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
        
    return CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, EUTWio_detail_dict, phys_dict, region_dict

####################


'''Load MIOT-based and industry shipment 
data for USA (for MIOT method variations to assess sensitivity)'''

def load_data_USA_sensitivity(path_input_data, data_path_usa,data_path_exio):
    years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]      

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
    
    

    # dictionary for industry shipments in physical units    
    phys_materials = ['pd_IronSteel','pd_Alu','pd_Copper','pd_Wood','pd_Cement','pd_Plastics']
    phys_dict = {}
    for material in phys_materials:
        frame= pd.read_excel(path_input_data + '//Industry_Shipments//Shipments_USA.xlsx', sheet_name=material).set_index('Year')
        dict_ele = {material:frame}
        phys_dict.update(dict_ele)
        
    # dictionary for USA from EXIOBASE    
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

    # assemble EXIOBASE dictionary per region and material
    materials = ['steel', 'wood', 'Plastic', 'glass', 'alumin', 'tin', 'Copper']

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
        
    return Wio_dict, Wio_ext_dict, Wio_withServiceInput_dict, EUTWio_dict, EUTWio_ext_dict, phys_dict, region_dict
        
####################    


''' Save method dictionaries from function load_data_USA() to Excel 
(and calculate sum of all end-use shares to check if 100%)'''

def save_method_dictionaries(methods, method_names, path_1, path_2):
    from EndUseShares_GraphsStatistics_functions_v1 import save_dict2Excel
    k=0
    for k in range(0,len(methods)):
        for e,f in methods[k].items():
            f.loc['sum'] = f.sum(axis=0)
        save_dict2Excel( path_1 + method_names[k] + path_2, methods[k] )
        k = k+1

####################

# ''' Assemble material end-use dataframes for comparison of USA 
# national MIOTs + EXIOBASE MIOTs + industry shipments'''

# def assemble_plot_frames_USA_standard(methods, method_names, CBA_dict, phys_dict, region_dict):
    
#     # from EndUseShares_GraphsStatistics_functions_v1 import assemble_materialEndUse_df
    
#     years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]
        
#     # # re-assemble data to dataframes per material and end-use
#     # plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
#     #     alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
#     #     copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
#     #     steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
#     #     cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df  = assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict)
    
#     #assemble material dictionary time series 
#     year = 1963
    
#     plastic_dict = {}
#     count = -1
#     for method in methods:
#         plastic_single = []
#         plastic_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             plastic_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('Plastic' or 'plastic') in t).to_list()]
#             plastic_df[year] = plastic_single.values
#         plastic_dict[(method_names[count])] = plastic_df
    
#     cement_dict = {}
#     count = -1
#     for method in methods:
#         cement_single = []
#         cement_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             cement_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('Cement' or 'cement') in t).to_list()]
#             cement_df[year] = cement_single.values
#         cement_dict[(method_names[count])] = cement_df
        
#     years_cop = [1963,1967,1972,1977,1982,1987,1992]
#     years_cop2 =  [1997]
#     years_cop3 = [2002]
#     years_cop4 = [2007,2012]
#     copper_dict = {}
#     count = -1
#     for method in methods:
#         copper_single = []
#         copper_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years_cop:
#             copper_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(0).astype(str).map(lambda t: ('3801' ) in t).to_list()]
#             copper_df[year] = copper_single.values
#         copper_dict[(method_names[count])] = copper_df 
#         for year2 in years_cop2:
#             copper_single = method.get(year2).iloc[:,method.get(year2).columns.get_level_values(1).map(lambda t: ('smelting') in t).to_list()]
#             copper_df[year2] = copper_single.values
#         copper_dict[(method_names[count])] = copper_df
#         for year3 in years_cop3:
#             copper_single = method.get(year3).iloc[:,method.get(year3).columns.get_level_values(0).astype(str).map(lambda t: ('331411') in t).to_list()]
#             copper_df[year3] = copper_single.values
#         copper_dict[(method_names[count])] = copper_df
#         for year4 in years_cop4:
#             copper_single = method.get(year4).iloc[:,method.get(year4).columns.get_level_values(1).map(lambda t: ('Copper') in t).to_list()]
#             copper_df[year4] = copper_single.values
#         copper_dict[(method_names[count])] = copper_df
            
#     steel_dict = {}
#     count = -1
#     for method in methods:
#         steel_single = []
#         steel_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             steel_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('steel' or 'Blast') in t).to_list()]
#             steel_df[year] = steel_single.values
#         steel_dict[(method_names[count])] = steel_df
        
#     alu_dict = {}
#     count = -1
#     for method in methods:
#         alu_single = []
#         alu_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             alu_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('alu' or 'Alu') in t).to_list()]
#             alu_df[year] = alu_single.values
#         alu_dict[(method_names[count])] = alu_df
        
#     Wood_dict = {}
#     count = -1
#     for method in methods:
#         wood_single = []
#         Wood_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             wood_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: ('Sawmill' or 'Wood') in t).to_list()]
#             Wood_df[year] = wood_single.values
#         Wood_dict[(method_names[count])] = Wood_df
    
#     bricks_dict = {}
#     count = -1
#     for method in methods:
#         bricks_single = []
#         bricks_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             bricks_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Brick' in t or 'Clay product' in t).to_list()]
#             bricks_df[year] = bricks_single.values
#         bricks_dict[(method_names[count])] = bricks_df
    
#     years =  [1963, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002]
#     #only do for these years as for 2007/12 all glass is aggregated
#     flat_dict = {}
#     count = -1
#     for method in methods:
#         flat_single = []
#         flat_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             flat_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Flat glass' in t or 'glass products' in t).to_list()]
#             flat_df[year] = flat_single.values
#         flat_dict[(method_names[count])] = flat_df
            
#     years =  [1963, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007, 2012]
#     paper_dict = {}
#     count = -1
#     for method in methods:
#         paper_single = []
#         paper_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             paper_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Pulp' in t or 'Paper' in t).to_list()]
#             paper_df[year] = paper_single.values
#         paper_dict[(method_names[count])] = paper_df
    
#     years =  [1963, 1967, 1972, 1977, 1982]
#     lead_dict = {}
#     count = -1
#     for method in methods:
#         lead_single = []
#         lead_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             lead_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Lead' in t or 'lead' in t).to_list()]
#             lead_df[year] = lead_single.values
#         lead_dict[(method_names[count])] = lead_df
    
#     years =  [1963, 1967, 1972, 1977, 1982]
#     zinc_dict = {}
#     count = -1
#     for method in methods:
#         zinc_single = []
#         zinc_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
#         count= count +1
#         for year in years:
#             zinc_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'zinc' in t or 'zinc' in t).to_list()]
#             zinc_df[year] = zinc_single.values
#         zinc_dict[(method_names[count])] = zinc_df
    
#     years =  [1963, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007, 2012]
    
#     return zinc_dict, lead_dict, paper_dict, flat_dict, bricks_dict, Wood_dict, alu_dict, copper_dict, steel_dict,cement_dict, plastic_dict

####################


'''Plot FIGURE2: low end-use resolution'''

def plot_USA_low_resolution(methods, method_names, CBA_dict, phys_dict, region_dict, years):
    
    from EndUseShares_GraphsStatistics_functions_v1 import assemble_materialEndUse_df, calc_relDeviation
    
    plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
        alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
        copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
        steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
        cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df  = assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict)
    

    dummy_df = plastic_electrical_df.copy()
    dummy_df[:] = 0
    
    pal = sns.color_palette("colorblind") 
    
    color_dict = {'CBA':pal[0], 'WIO-MFA': pal[1], 'Ghosh-IO AMC':pal[2],  \
                  'Partial Ghosh-IO': pal[3], 'EUT-WIO': 'maroon', 'Exio_EUT-WIO': pal[4],\
                'Shipment_1':pal[7], 'Shipment_2':pal[0],'Shipment_3':pal[3]}
    
    marker_dict = {'CBA':'o', 'WIO-MFA': 'o', 'Ghosh-IO AMC':'o',  \
                  'Partial Ghosh-IO': 'o', 'EUT-WIO': 'v', 'Exio_EUT-WIO': '.'}
        
    element_dict = {'(a) wood_construction_df':wood_construction_df,'(b) wood_transport_df':wood_transport_df,'(c) wood_packaging_food_df':wood_packaging_food_df, '(d) wood_machinery_df':wood_machinery_df, '(e) wood_furniture_df':wood_furniture_df,\
                      '(f) steel_construction_df':steel_construction_df, '(g) steel_transport_df':steel_transport_df,  '(h) steel_packaging_food_df':steel_packaging_food_df, '(i) steel_machinery_df':steel_machinery_df,  '(j) steel_furniture_df':steel_furniture_df,\
                      '(k) copper_construction_df':copper_construction_df, '(l) copper_transport_df':copper_transport_df,  '(x) dummy_df':dummy_df , '(m) copper_machinery_df':copper_machinery_df, '(n) copper_furniture_df':copper_furniture_df,\
                      '(o) alu_construction_df':alu_construction_df, '(p) alu_transport_df':alu_transport_df, '(q) alu_packaging_food_df':alu_packaging_food_df, '(r) alu_machinery_df':alu_machinery_df, '(s) alu_furniture_df':alu_furniture_df, \
                      '(t) plastic_construction_df':plastic_construction_df, '(u) plastic_transport_df':plastic_transport_df,  '(v) plastic_packaging_food_df':plastic_packaging_food_df, '(w) plastic_electrical_df':plastic_electrical_df, '(x) plastic_furniture_df':plastic_furniture_df}
 
    i,j = 0,0  
    fig, axs = plt.subplots(5,5 ,sharex=False, sharey=False, figsize=(33,20))
    
    for key, value in element_dict.items():       
        value.plot(ax=axs[i,j], color = [color_dict.get(r) for r in value], style = [marker_dict.get(r, '*') for r in value], kind='line', title= key[:-3], fontsize=16, legend = False)
        value.xs('EUT-WIO',axis=1).dropna().plot(ax=axs[i,j], color = 'maroon', style =  'v', kind='line', legend = False, linestyle='--')
        axs[i,j].set_ylabel('%')
        axs[i,j].set_xticks([1963,1972,1982,1992,2002,2012])
        axs[i,j].title.set_fontsize(18)
        median = []
        try:
            median, minim, maxim = calc_relDeviation(value)
            axs[i,j].annotate(str(round(median,2)) + ', ' + str(round( minim,2)) + ', ' + str(round(maxim ,2)) , ((2002.5, axs[i,j].get_ylim()[1]-axs[i,j].get_ylim()[1]*0.04)))
        except Exception:
            pass
        j = j+1
        if j > 4:
            i = i+1
            j = 0
    
    axs[2,2].clear()
    axs[2,2].axis('off')
    lgd = axs[2,2].legend(loc='center',fontsize=18, ncol=5) #, ,fontsize=14)# bbox_to_anchor=(0.145, -0.02)
    
    def add_line(legend):
        a1 = axs[1,0].get_legend_handles_labels()[0][:-6] 
        b1 = axs[1,0].get_legend_handles_labels()[1][:-6] 
        a2 = [axs[1,0].get_legend_handles_labels()[0][-1]]
        b2 = [axs[1,0].get_legend_handles_labels()[1][-1]]
        a3 = axs[1,0].get_legend_handles_labels()[0][-5:-1] 
        b3 = axs[1,0].get_legend_handles_labels()[1][-5:-1] 
        c = tuple(((a1+a2+a3),(b1+b2+b3)))
        handles, labels = c
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
    
    add_line(lgd)
    fig.suptitle('Comparison of end-use shares - low sector resolution', y=1, fontsize = 22)
    fig.tight_layout()
    fig.savefig('Figure2.pdf', format='pdf', dpi =600, bbox_inches='tight', pad_inches=0)
    
    return fig, element_dict

####################


''' Plot FIGURE2 SENSITIVITY: sensitivity to extension and filter matrix choice at low end-use resolution
variables methods & method_names need to be changed above for this plot to work'''

def plot_USA_low_resolution_sensitivity(methods, method_names, CBA_dict, phys_dict, region_dict, years):
    
    from EndUseShares_GraphsStatistics_functions_v1 import assemble_materialEndUse_df, calc_relDeviation
    
    plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
        alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
        copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
        steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
        cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df  = assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict)
    
    dummy_df = plastic_electrical_df.copy()
    dummy_df[:] = 0
    
    pal = sns.color_palette("colorblind") 
    
    color_dict = {'WIO-MFA': pal[3], 'EUT-WIO': 'maroon', 'WIO-MFA_extAgg': pal[3],'WIO-MFA_filtDif': pal[3], \
                'EUT-WIO_extAgg': 'maroon','Exio_EUT-WIO': pal[4], 'Shipment_1':pal[7], 'Shipment_2':pal[0],'Shipment_3':pal[3]}
    
    marker_dict = {'WIO-MFA': 'o', 'EUT-WIO': 'v', 'WIO-MFA_extAgg': 'X','WIO-MFA_filtDif': '+' ,\
                'EUT-WIO_extAgg': 'X'}
        
    element_dict = {'(a) wood_construction_df': wood_construction_df,'(b) wood_transport_df':wood_transport_df,'(c) wood_packaging_food_df':wood_packaging_food_df, '(d) wood_machinery_df':wood_machinery_df, '(e) wood_furniture_df':wood_furniture_df,\
                      '(f) steel_construction_df':steel_construction_df, '(g) steel_transport_df':steel_transport_df,  '(h) steel_packaging_food_df':steel_packaging_food_df, '(i) steel_machinery_df':steel_machinery_df,  '(j) steel_furniture_df':steel_furniture_df,\
                      '(k) copper_construction_df':copper_construction_df, '(l) copper_transport_df':copper_transport_df,  '(x) dummy_df':dummy_df , '(m) copper_machinery_df':copper_machinery_df, '(n) copper_furniture_df':copper_furniture_df,\
                      '(o) alu_construction_df':alu_construction_df, '(p) alu_transport_df':alu_transport_df, '(q) alu_packaging_food_df':alu_packaging_food_df, '(r) alu_machinery_df':alu_machinery_df, '(s) alu_furniture_df':alu_furniture_df, \
                      '(t) plastic_construction_df':plastic_construction_df, '(u) plastic_transport_df':plastic_transport_df,  '(v) plastic_packaging_food_df':plastic_packaging_food_df, '(w) plastic_electrical_df':plastic_electrical_df, '(x) plastic_furniture_df':plastic_furniture_df}
 
    i,j = 0,0     
    fig, axs = plt.subplots(5,5 ,sharex=False, sharey=False, figsize=(33,20))
    
    for key, value in element_dict.items():       
        value.plot(ax=axs[i,j], color = [color_dict.get(r) for r in value], style = [marker_dict.get(r, '*') for r in value], kind='line', title= key[:-3], fontsize=16, legend = False)
        value.xs('EUT-WIO',axis=1).dropna().plot(ax=axs[i,j], color = 'maroon', style =  'v', kind='line', legend = False, linestyle='--')
        axs[i,j].set_ylabel('%')
        axs[i,j].set_xticks([1963,1972,1982,1992,2002,2012])
        axs[i,j].title.set_fontsize(18)
        median = []
        try:
            median, minim, maxim = calc_relDeviation(value)
            axs[i,j].annotate(str(round(median,2)) + ', ' + str(round( minim,2)) + ', ' + str(round(maxim ,2)) , ((2002.5, axs[i,j].get_ylim()[1]-axs[i,j].get_ylim()[1]*0.04)))
        except Exception:
            pass
        j = j+1
        if j > 4:
            i = i+1
            j = 0
    
    axs[2,2].clear()
    axs[2,2].axis('off')
    lgd = axs[2,2].legend(loc='center',fontsize=18, ncol=5) #, ,fontsize=14)# bbox_to_anchor=(0.145, -0.02)
    
    def add_line(legend):
        a1 = axs[1,0].get_legend_handles_labels()[0][:-6] 
        b1 = axs[1,0].get_legend_handles_labels()[1][:-6] 
        a2 = [axs[1,0].get_legend_handles_labels()[0][-1]]
        b2 = [axs[1,0].get_legend_handles_labels()[1][-1]]
        a3 = axs[1,0].get_legend_handles_labels()[0][-5:-1] 
        b3 = axs[1,0].get_legend_handles_labels()[1][-5:-1] 
        c = tuple(((a1+a2+a3),(b1+b2+b3)))
        handles, labels = c
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
    
    add_line(lgd)
    fig.suptitle('Sensitivity to extension choice & filter design (WIO-MFA, EUT-WIO) - high sector aggregation', y=1, fontsize = 16)
    fig.tight_layout()
    
    #ADD differences of sensitivity and base cases and SAVE to EXCEL
    for key, value in element_dict.items():
        try:
            value['Diff_WIO-MFA_extAgg'] = value['WIO-MFA'] - value['WIO-MFA_extAgg']
            value['Diff_EUT-WIO_extAgg'] = value['EUT-WIO'] - value['EUT-WIO_extAgg']
            value['Diff_WIO-MFA_filtDif'] = value['WIO-MFA'] - value['WIO-MFA_filtDif']
            value['rel_Diff_WIO-MFA_extAgg'] = (value['WIO-MFA'] - value['WIO-MFA_extAgg']) / value['WIO-MFA'] 
            value['rel_Diff_EUT-WIO_extAgg'] = (value['EUT-WIO'] - value['EUT-WIO_extAgg']) / value['EUT-WIO']
            value['rel_Diff_WIO-MFA_filtDif'] = (value['WIO-MFA'] - value['WIO-MFA_filtDif']) / value['WIO-MFA'] 
        except:
            pass
        
    return fig, element_dict
     
####################


''' Assemble data for detailed plots for WOOD and CEMENT 
in the CONSTRUCTION SECTOR for FIGURE3 (needs to be manually 
processed due to differing sector labels over years)'''

def save_construction_detail(data_path, EUTWio_detail_dict):
    #isolate construction sector sub-sectors and save in excel for manual processing
    #(no automatic processing as different for each year)
    constr_1963 = EUTWio_detail_dict.get(1963).iloc[19:26,:]
    constr_1967 = EUTWio_detail_dict.get(1967).iloc[26:76,:]
    constr_1972 = EUTWio_detail_dict.get(1972).iloc[26:76,:]
    constr_1977 = EUTWio_detail_dict.get(1977).iloc[30:83,:]
    constr_1982 = EUTWio_detail_dict.get(1982).iloc[30:83,:]
    constr_1987 = EUTWio_detail_dict.get(1987).iloc[30:83,:]
    constr_1992 = EUTWio_detail_dict.get(1992).iloc[30:45,:] #checl if to add to this and the above minign stuff
    constr_1997 = EUTWio_detail_dict.get(1997).iloc[26:45,:]
    constr_2002 = EUTWio_detail_dict.get(2002).iloc[27:40,:]
    constr_2007 = EUTWio_detail_dict.get(2007).iloc[19:36,:] 
    constr_2012 = EUTWio_detail_dict.get(2012).iloc[19:36,:] 

    # save to Excel, including used filter matrices
    writer = pd.ExcelWriter(data_path + '/Construction_detail' + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    constr_1963.to_excel(writer,'1963')
    constr_1967.to_excel(writer,'1967')
    constr_1972.to_excel(writer,'1972')
    constr_1977.to_excel(writer,'1977')
    constr_1982.to_excel(writer,'1982')
    constr_1987.to_excel(writer,'1987')
    constr_1992.to_excel(writer,'1992')
    constr_1997.to_excel(writer,'1997')
    constr_2002.to_excel(writer,'2002')
    constr_2007.to_excel(writer,'2007')
    constr_2012.to_excel(writer,'2012')
    writer.save()

####################   


''' Plot FIGURE 3: combine high, medium and low 
sector aggregation
'''

def plot_USA_medium_resolution(methods, method_names, CBA_dict, phys_dict, region_dict, years, wood_detail, cement_detail):
    
    from EndUseShares_GraphsStatistics_functions_v1 import assemble_materialEndUse_df, calc_relDeviation
    
    pal = sns.color_palette("colorblind") 
    color_dict = {'CBA':pal[0], 'WIO-MFA': pal[1], 'Ghosh-IO AMC':pal[2],  \
                  'Partial Ghosh-IO': pal[3], 'EUT-WIO': 'maroon', 'Exio_EUT-WIO': pal[4],\
                'Shipment_1':pal[7], 'Shipment_2':pal[0],'Shipment_3':pal[3]}
    marker_dict = {'CBA':'o', 'WIO-MFA': 'o', 'Ghosh-IO AMC':'o',  \
                  'Partial Ghosh-IO': 'o', 'EUT-WIO': 'v', 'Exio_EUT-WIO': '.'}
           
    plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
        alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
        copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
        steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
        cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df  = assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict)
        
    dummy_df1 = wood_packaging_food_df.copy()
    dummy_df2 = wood_packaging_food_df.copy()
    dummy_df3 = wood_packaging_food_df.copy()
    dummy_df4 = wood_packaging_food_df.copy()
    dummy_df1[:] = 0
    dummy_df2[:] = 0
    dummy_df3[:] = 0
    dummy_df4[:] = 0
    
    element_dict = {'(a) wood_construction_df': wood_construction_df, '(b) wood_nonresidential_df': wood_nonresidential_df,'(a) wood_residential_df': wood_residential_df, '(x) dummy_df1': dummy_df1,
                  '(x) dummy_df2': dummy_df2, '(x) dummy_df3': dummy_df3, '(e) cement_civil_engineering_df': cement_civil_engineering_df, '(d) cement_nonresidential_df': cement_nonresidential_df, 
                  '(c) cement_residential_df': cement_residential_df, '(x) dummy_df4': dummy_df4}
    
    annotation_spot = [2000,2000,2000,2004,2004,2004,2004,2004,2004,2004,2004,2004]
    
    k,i,j = 0,0,0     
    fig, axs = plt.subplots(5,2,sharex=False, sharey=False, figsize=(11,15),gridspec_kw={'height_ratios':[1,1,0.6,1,1]})
    for key, value in element_dict.items():
        try:
            value.plot(ax=axs[i,j], color = [color_dict.get(r,pal[0]) for r in value], style = [marker_dict.get(r, '*') for r in value], kind='line', title= key[:-3], legend = False)
            value.xs('EUT-WIO',axis=1).dropna().plot(ax=axs[i,j], color = 'maroon', style =  'v', kind='line', legend = False, linestyle='--')
            axs[i,j].set_ylabel('%')
            axs[i,j].set_xticks([1963,1972,1982,1992,2002,2012])
        except:
            pass
        median = []
        try:
            median, minim, maxim = calc_relDeviation(value)
            axs[i,j].annotate(str(round(median,2)) + ', ' + str(round( minim,2)) + ', ' + str(round(maxim ,2)) , ((annotation_spot[k], axs[i,j].get_ylim()[1]-axs[i,j].get_ylim()[1]*0.06)))
        except Exception:
            pass
        k = k+1
        j = j+1
        if j > 1:
            i = i+1
            j = 0
                 
    axs[2,0].clear()
    axs[2,0].axis('off')
    axs[2,1].clear()
    axs[2,1].axis('off')
    axs[1,1].clear()
    axs[4,1].clear()
    
    pal = sns.color_palette("Paired") 
    color_dict_low = {'MIOT new single-family*':pal[0],'MIOT new multi-family*':pal[1],'MIOT resid. repairs/alterations':pal[2], 'MIOT resid. other':pal[3],\
                  'MIOT highways & streets*':pal[4], 'PCA new single-family buildings':pal[0], 'PCA new multi-family buildings':pal[1], \
                  'PCA res. buildungs improvements':pal[2], 'PCA highways & streets':pal[4], 'McK new single-family housing':pal[0], \
                  'McK new multi-family housing':pal[1], 'McK new manufactued housing':pal[3], 'McK resid. repair & remodeling':pal[2]}
    					
    marker_dict_low = {'MIOT new single-family*':'.-','MIOT new multi-family*':'.-','MIOT resid. repairs/alterations':'.-', 'MIOT resid. other':'.-',\
                  'MIOT highways & streets*':'.-',  'McK new single-family housing':'^', 'McK new multi-family housing':'^',
                   'McK new manufactued housing':'^', 'McK resid. repair & remodeling':'^'}
      
    element_dict_low = {'(g) wood_detail':wood_detail,'(f) cement_detail':cement_detail}
    i_list = [(1,1),(4,1)]
    
    f=0
    for key, value in element_dict_low.items():
        i,j = i_list[f]
        try:
            value.plot(ax=axs[i,j], color = [color_dict_low.get(r,pal[0]) for r in value], style = [marker_dict_low.get(r, '*') for r in value], kind='line', title= key[:-7], legend = False)
            axs[i,j].set_ylabel('%')
        except:
            continue
        f = f+1
        
            
    cement_detail.iloc[np.r_[1:9,13],:].plot(ax=axs[4,1], color = [color_dict_low.get(r) for r in cement_detail.iloc[np.r_[1:9,13],:]], style = [marker_dict_low.get(r, '*') for r in cement_detail], kind='line', title= '(f) cement_detail'[:-7], legend = False)
    wood_detail.iloc[np.r_[0:7,8],:3].plot(ax=axs[1,1], color = [color_dict_low.get(r) for r in wood_detail.iloc[np.r_[0:7,8],:3]], style = [marker_dict_low.get(r, '*') for r in wood_detail], kind='line', title= '(g) wood_detail'[:-7], legend = False)
    wood_detail.iloc[np.r_[0:6,8],3].plot(ax=axs[1,1], color = pal[3], style = [marker_dict_low.get(r, '*') for r in wood_detail], kind='line', title= '(g) wood_detail'[:-7], legend = False)
                      
    ##lgd for medium end-use resolution plot:
    lgd = fig.legend(loc='center', bbox_to_anchor=(0.5, 0.535),fontsize=12, ncol = 5) 
    
    def add_line(legend):
        a1 = axs[4,0].get_legend_handles_labels()[0][:-5] 
        b1 = axs[4,0].get_legend_handles_labels()[1][:-5] 
        a2 = [axs[4,0].get_legend_handles_labels()[0][-1]]
        b2 = [axs[4,0].get_legend_handles_labels()[1][-1]]
        a3 = axs[4,0].get_legend_handles_labels()[0][-4:-1] 
        b3 = axs[4,0].get_legend_handles_labels()[1][-4:-1] 
        c = tuple(((a1+a2+a3),(b1+b2+b3)))
        handles, labels = c
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
        
    add_line(lgd)
        
    ##lgd for high end-use resolution plot:
    lgd_low = fig.legend(loc='center', bbox_to_anchor=(0.5, 0.471),fontsize=12, ncol = 3) 
    
    def add_line(legend):
        a = axs[1,1].get_legend_handles_labels()[0][:9] + axs[4,1].get_legend_handles_labels()[0][4:9]
        b = axs[1,1].get_legend_handles_labels()[1][:9] + axs[4,1].get_legend_handles_labels()[1][4:9]
        c = tuple((a,b))
        handles, labels = c
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
               
    add_line(lgd_low)
    
    axs[1,1].set_xticks([1967,1972,1982,1992,2002,2007])
    axs[4,1].set_xticks([1963,1972,1982,1992,2002,2012])
    axs[1,1].xaxis.label.set_visible(False)
    axs[4,1].xaxis.label.set_visible(False)
    
    axs[0,0].set_title('(a) wood construction')
    axs[0,1].set_title('(b) wood construction: non-residential')
    axs[1,0].set_title('(c) wood construction: residential')
    axs[1,1].set_title('(d) wood residential: housing types & repairs (EUT-WIO)')
    
    axs[3,0].set_title('(e) cement construction: civil engineering')
    axs[3,1].set_title('(f) cement construction: non-residential')
    axs[4,0].set_title('(g) cement construction: residential')
    axs[4,1].set_title('(h) cement residential: housing types & repairs (EUT-WIO)')
    
    fig.suptitle('Construction end-use shares wood & cement - low to high sector resolution', y=1, fontsize = 16)
    fig.tight_layout()
    
    element_dict.update(element_dict_low)
    
    return fig, element_dict
           
####################
    

''' Assemble EXIOBASE results 
(for multiple countries / regions)'''

def assemble_exiobase_results(data_path_exio, years_exio, regions):    
        
    region_transl = {'PT':'Portugal', 'US':'USA', 'GB':'Great Britain', 'FR':'France','IT':'Italy',\
                      'DE':'Germany','IN':'India','CN':'China','RU':'Russia','ZA':'South Africa', \
                      'JP':'Japan', 'AT':'Austria', 'AU':'Australia', 'BE':'Belgium', 'BR':'Brazil',\
                      'NL':'Netherlands', 'NO':'Norway', 'ES':'Spain', 'CH':'Switzerland'}
    
    # assemble EXIOBASE dictionary per region
    Exio_dict = {}
    for region in regions:
        Region_dict = {}
        for year in years_exio:
            for file in glob.glob(os.path.join((data_path_exio + 'Exio_EUT_WIOMF_' + str(year) + '_' + region + '*.xlsx'))):
                Region_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0])
            Region_dict[year] = Region_single
        Exio_dict[region] = Region_dict
    
    # assemble EXIOBASE dictionary per material
    materials = ['steel', 'Wood', 'Plastic', 'alumin', 'Lead, zinc and tin', 'Copper', 'non-ferrous metal', 'Precious metals',
                 'Cement, lime and plaster', 'Bricks, tiles', 'Glass', 'Bitumen', 'Pulp', 'Sand and clay', 'Stone']
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
    
    return materials, region_transl, region_dict

####################


''' Save EXIOBASE results for selected regions and materials 
from function: assemble_exiobase_results'''

def save_exiobase_country_results(output_path, file_name, materials, region_dict, save_regions):
    writer = pd.ExcelWriter(output_path + file_name + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    for region in save_regions:
        for material in materials:
            df = region_dict.get(region).get(material)
            df.to_excel(writer, sheet_name = material)
        writer.save() 
    
####################

'''Assemble dictionary for comparision
of EUT-WIO results from EXIOBASE with physical
industry shipments (aggregating some sectors)'''

def assemble_exiobase_comparison_agg(data_path_exio, data_path_shipments, years_exio, \
                                     regions, region_transl, region_dict, plotMaterials):
    
    ### LOAD PHYSICAL SHIPMENT DATA FOR COUNTRIES OTHER THAN USA
    physSplit_plastics_Intern  = pd.read_excel(data_path_shipments + '/Shipments_Plastics_EUROMAP.xlsx', sheet_name='clean data manip')
    physSplit_plastics_China  = pd.read_excel(data_path_shipments + '/Shipments_Plastics_ChinaEU28.xlsx', sheet_name='China').set_index('Year')*100
    physSplit_plastics_EU28  = pd.read_excel(data_path_shipments + '/Shipments_Plastics_ChinaEU28.xlsx', sheet_name='EU28').set_index('Year')*100
    physSplit_steel_China = pd.read_excel(data_path_shipments + '/Shipments_IronSteel.xlsx', sheet_name='China').set_index('Year')*100
    physSplit_steel_India = pd.read_excel(data_path_shipments + '/Shipments_IronSteel.xlsx', sheet_name='India').set_index('Year')*100
    physSplit_steel_UK = pd.read_excel(data_path_shipments + '/Shipments_IronSteel.xlsx', sheet_name='UK').set_index('Year')*100
    physSplit_alu_intern = pd.read_excel(data_path_shipments + '/Shipments_Alu_LiuMüller2013.xlsx', sheet_name='Liu_out', index_col=[0], header=[0,1])*100
    physSplit_copper_EU28 = pd.read_excel(data_path_shipments + '/Shipments_Copper.xlsx', sheet_name='EU').set_index('Year')*100
    
    plotRegions = regions 
    EU28 = ['GB', 'AT', 'DE', 'BE', 'IT', 'PT', 'NL', 'FR', 'NO', 'ES']
        
    material_region_dict = {}
    for plotMaterial in plotMaterials:
        Exio_region_plotDict = []
        for plotRegion in plotRegions:
            dict_2={}
            plot_frame = region_dict.get(plotRegion).get(plotMaterial).T
            plot_frame['Other machinery & appliances'] =  plot_frame['Machinery and equipment n.e.c. '] + \
                plot_frame['Medical, precision and optical instruments, watches and clocks']
            plot_frame['Electrical machinery & appliances'] =  plot_frame['Office machinery and computers'] + \
                plot_frame['Radio, television and communication equipment and apparatus']+ \
                   plot_frame['Electrical machinery and apparatus n.e.c.']
            plot_frame['Transportation'] = plot_frame['Motor vehicles, trailers and semi-trailers'] + \
                plot_frame['Other transport equipment']
            plot_frame['All other'] = plot_frame['Printed matter and recorded media'] + plot_frame['Other raw materials']+\
                 + plot_frame['Secondary materials'] + plot_frame['Energy carriers']  \
                     + plot_frame[ 'Other'] + plot_frame[ 'Products nec'] + plot_frame['Services'] + plot_frame['Textiles']\
                     + plot_frame['Furniture; other manufactured goods n.e.c.']        
            
            if plotMaterial == 'Plastic':
                try:
                    plot_frame['Packaging_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Packaging']
                    plot_frame['Automotive_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Automotive']
                    plot_frame['Electrical_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Construction industry']
                    plot_frame['Construction_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Electrical, electronics & telecom']
                    plot_frame['Other_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Others']
                except:
                    pass
                if plotRegion == 'CN':
                    plot_frame['Jiang_Packaging'] = physSplit_plastics_China['Packaging']
                    plot_frame['Jiang_B&C'] = physSplit_plastics_China['B&C']
                    plot_frame['Jiang_Automobile'] = physSplit_plastics_China['Automobile']
                    plot_frame['Jiang_Electronics'] = physSplit_plastics_China['Electronics']
                    plot_frame['Jiang_Agriculture'] = physSplit_plastics_China['Agriculture']
                    plot_frame['Jiang_Others'] = physSplit_plastics_China['Others']
                if plotRegion in EU28: #watch out: EU28 list not complete
                    plot_frame['PlastEU_Packaging'] = physSplit_plastics_EU28['Packaging PE']
                    plot_frame['PlastEU_B&C'] = physSplit_plastics_EU28['Building and construction PE']
                    plot_frame['PlastEU_Automotive'] = physSplit_plastics_EU28['Automotive PE']
                    plot_frame['PlastEU_Electrical'] = physSplit_plastics_EU28['Electrical&Electronic PE']
                    plot_frame['PlastEU_Agriculture'] = physSplit_plastics_EU28['Agriculture PE']
                    plot_frame['PlastEU_Others'] = physSplit_plastics_EU28['Others PE']
                    
            if plotMaterial == 'steel':
                if plotRegion == 'CN':
                    plot_frame['Wang_Construction'] = physSplit_steel_China['RFSCon']
                    plot_frame['Wang_Transportation'] = physSplit_steel_China['RFSTra']
                    plot_frame['Wang_Machinery&Appliances'] = physSplit_steel_China['RFSM']
                    plot_frame['Wang_Other'] = physSplit_steel_China['RFSOth']
                if plotRegion == 'IN':
                    plot_frame['Pauliuk_Construction'] = physSplit_steel_India['construction']
                    plot_frame['Pauliuk_Transportation'] = physSplit_steel_India['transportation']
                    plot_frame['Pauliuk_Machinery'] = physSplit_steel_India['machinery']
                    plot_frame['Pauliuk_Products'] = physSplit_steel_India['products']
                if plotRegion == 'GB':
                    plot_frame['Pauliuk_Construction'] = physSplit_steel_UK['Construction']
                    plot_frame['Pauliuk_Transportation'] = physSplit_steel_UK['Transportation']
                    plot_frame['Pauliuk_Machinery'] = physSplit_steel_UK['Machinery']
                    plot_frame['Pauliuk_Products'] = physSplit_steel_UK['Products']
            
            if plotMaterial == 'Copper':
                if plotRegion in EU28: #watch out: EU28 list not complete
                    plot_frame['Ciacci_B&C'] = physSplit_copper_EU28['Building and construction']
                    plot_frame['Ciacci_Electrical'] = physSplit_copper_EU28['Electrical and Electronic Goods']
                    plot_frame['Ciacci_Machinery'] = physSplit_copper_EU28['Industrial Machinery and Equipment']
                    plot_frame['Ciacci_Transportation'] = physSplit_copper_EU28['Transportation Equipment']
                    plot_frame['Ciacci_Products'] = physSplit_copper_EU28['Consumer and General Products']
            
            if plotMaterial == 'alumin':
                try:
                    alu_shipment = physSplit_alu_intern.xs(region_transl.get(plotRegion), level=0, axis=1)
                    plot_frame['Liu_building&construction'] = alu_shipment['B&C']
                    plot_frame['Liu_Transport'] = alu_shipment['Trans']
                    plot_frame['Liu_Machinery&equipment'] = alu_shipment['M&E']
                    plot_frame['Liu_Electric&electronics'] = alu_shipment['EE']
                    plot_frame['Liu_Containers&packaging']= alu_shipment['C&P']
                    plot_frame['Liu_Consumer Durables'] = alu_shipment['ConDur']
                    plot_frame['Liu_Others'] = alu_shipment['Others']
                except:
                    pass
            
            Exio_region_plotDict.append(plot_frame) 
            dict_2 = dict(zip(plotRegions,Exio_region_plotDict))
        material_region_dict.update({plotMaterial:dict_2})   
        
    # assemble data for one material end-use and ALL countries for use in plots 
    #ALU CONSTRUCTION
    end_use_all_aluConst =  pd.DataFrame([])# index=years_exio, columns=regions)
    for region in regions:
        end_use_region = pd.DataFrame(region_dict.get(region).get('alumin').loc['Construction']).rename(columns = {'Construction':region})
        end_use_all_aluConst[region] = end_use_region
    del end_use_region
    #end_use_all.T.plot( kind='box', title= 'Copper to Construction')

    #Steel CONSTRUCTION
    end_use_all_steelConst =  pd.DataFrame([])# index=years_exio, columns=regions)
    for region in regions:
        end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Construction']).rename(columns = {'Construction':region})
        end_use_all_steelConst[region] = end_use_region
    del end_use_region

    #Steel MOTOR VEHICLES
    end_use_all_steelMotor =  pd.DataFrame([])# index=years_exio, columns=regions)
    for region in regions:
        end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Motor vehicles, trailers and semi-trailers']).rename(columns = {'Construction':region})
        end_use_all_steelMotor[region] = end_use_region
    del end_use_region
        
    return material_region_dict, end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor
    
####################

'''Assemble dictionary for comparision
of EUT-WIO results from EXIOBASE with physical
industry shipments (full sector detail)'''

def assemble_exiobase_comparison_full(data_path_exio,data_path_shipments, years_exio, \
                                     regions, region_transl, region_dict, plotMaterials):

        ### LOAD PHYSICAL SHIPMENT DATA FOR COUNTRIES OTHER THAN USA
        physSplit_plastics_Intern  = pd.read_excel(data_path_shipments + '/Shipments_Plastics_EUROMAP.xlsx', sheet_name='clean data manip')
        physSplit_plastics_China  = pd.read_excel(data_path_shipments + '/Shipments_Plastics_ChinaEU28.xlsx', sheet_name='China').set_index('Year')*100
        physSplit_plastics_EU28  = pd.read_excel(data_path_shipments + '/Shipments_Plastics_ChinaEU28.xlsx', sheet_name='EU28').set_index('Year')*100
        physSplit_steel_China = pd.read_excel(data_path_shipments + '/Shipments_IronSteel.xlsx', sheet_name='China').set_index('Year')*100
        physSplit_steel_India = pd.read_excel(data_path_shipments + '/Shipments_IronSteel.xlsx', sheet_name='India').set_index('Year')*100
        physSplit_steel_UK = pd.read_excel(data_path_shipments + '/Shipments_IronSteel.xlsx', sheet_name='UK').set_index('Year')*100
        physSplit_alu_intern = pd.read_excel(data_path_shipments + '/Shipments_Alu_LiuMüller2013.xlsx', sheet_name='Liu_out', index_col=[0], header=[0,1])*100
        physSplit_copper_EU28 = pd.read_excel(data_path_shipments + '/Shipments_Copper.xlsx', sheet_name='EU').set_index('Year')*100
        
        plotRegions = regions 
        EU28 = ['GB', 'AT', 'DE', 'BE', 'IT', 'PT', 'NL', 'FR', 'NO', 'ES']
        

        material_region_dict = {}
        for plotMaterial in plotMaterials:
            Exio_region_plotDict = []
            for plotRegion in plotRegions:
                dict_2={}
                plot_frame = region_dict.get(plotRegion).get(plotMaterial).T
                plot_frame['Other machinery & appliances'] =  plot_frame['Machinery and equipment n.e.c. '] + \
                    plot_frame['Medical, precision and optical instruments, watches and clocks']
                plot_frame['Electrical machinery & appliances'] =  plot_frame['Office machinery and computers'] + \
                    plot_frame['Radio, television and communication equipment and apparatus']+ \
                        plot_frame['Electrical machinery and apparatus n.e.c.']
                plot_frame['Transportation'] = plot_frame['Motor vehicles, trailers and semi-trailers'] + \
                    plot_frame['Other transport equipment']
                plot_frame['All other'] = plot_frame['Printed matter and recorded media'] + plot_frame['Other raw materials']+\
                      + plot_frame['Secondary materials'] + plot_frame['Energy carriers']  \
                          + plot_frame[ 'Other'] + plot_frame[ 'Products nec'] + plot_frame['Services']
                
                if plotMaterial == 'Plastic':
                    try:
                        plot_frame['Packaging_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Packaging']
                        plot_frame['Automotive_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Automotive']
                        plot_frame['Electrical_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Construction industry']
                        plot_frame['Construction_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Electrical, electronics & telecom']
                        plot_frame['Other_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Others']
                    except:
                        pass
                    if plotRegion == 'CN':
                        plot_frame['Jiang_Packaging'] = physSplit_plastics_China['Packaging']
                        plot_frame['Jiang_B&C'] = physSplit_plastics_China['B&C']
                        plot_frame['Jiang_Automobile'] = physSplit_plastics_China['Automobile']
                        plot_frame['Jiang_Electronics'] = physSplit_plastics_China['Electronics']
                        plot_frame['Jiang_Agriculture'] = physSplit_plastics_China['Agriculture']
                        plot_frame['Jiang_Others'] = physSplit_plastics_China['Others']
                    if plotRegion in EU28: #watch out: EU28 list not complete
                        plot_frame['PlastEU_Packaging'] = physSplit_plastics_EU28['Packaging PE']
                        plot_frame['PlastEU_B&C'] = physSplit_plastics_EU28['Building and construction PE']
                        plot_frame['PlastEU_Automotive'] = physSplit_plastics_EU28['Automotive PE']
                        plot_frame['PlastEU_Electrical'] = physSplit_plastics_EU28['Electrical&Electronic PE']
                        plot_frame['PlastEU_Agriculture'] = physSplit_plastics_EU28['Agriculture PE']
                        plot_frame['PlastEU_Others'] = physSplit_plastics_EU28['Others PE']
                        
                if plotMaterial == 'steel':
                    if plotRegion == 'CN':
                        plot_frame['Wang_Construction'] = physSplit_steel_China['RFSCon']
                        plot_frame['Wang_Transportation'] = physSplit_steel_China['RFSTra']
                        plot_frame['Wang_Machinery&Appliances'] = physSplit_steel_China['RFSM']
                        plot_frame['Wang_Other'] = physSplit_steel_China['RFSOth']
                    if plotRegion == 'IN':
                        plot_frame['Pauliuk_Construction'] = physSplit_steel_India['construction']
                        plot_frame['Pauliuk_Transportation'] = physSplit_steel_India['transportation']
                        plot_frame['Pauliuk_Machinery'] = physSplit_steel_India['machinery']
                        plot_frame['Pauliuk_Products'] = physSplit_steel_India['products']
                    if plotRegion == 'GB':
                        plot_frame['Pauliuk_Construction'] = physSplit_steel_UK['Construction']
                        plot_frame['Pauliuk_Transportation'] = physSplit_steel_UK['Transportation']
                        plot_frame['Pauliuk_Machinery'] = physSplit_steel_UK['Machinery']
                        plot_frame['Pauliuk_Products'] = physSplit_steel_UK['Products']
                
                if plotMaterial == 'Copper':
                    if plotRegion in EU28: #watch out: EU28 list not complete
                        plot_frame['Ciacci_B&C'] = physSplit_copper_EU28['Building and construction']
                        plot_frame['Ciacci_Electrical'] = physSplit_copper_EU28['Electrical and Electronic Goods']
                        plot_frame['Ciacci_Machinery'] = physSplit_copper_EU28['Industrial Machinery and Equipment']
                        plot_frame['Ciacci_Transportation'] = physSplit_copper_EU28['Transportation Equipment']
                        plot_frame['Ciacci_Products'] = physSplit_copper_EU28['Consumer and General Products']
                
                if plotMaterial == 'alumin':
                    try:
                        alu_shipment = physSplit_alu_intern.xs(region_transl.get(plotRegion), level=0, axis=1)
                        plot_frame['Liu_building&construction'] = alu_shipment['B&C']
                        plot_frame['Liu_Transport'] = alu_shipment['Trans']
                        plot_frame['Liu_Machinery&equipment'] = alu_shipment['M&E']
                        plot_frame['Liu_Electric&electronics'] = alu_shipment['EE']
                        plot_frame['Liu_Containers&packaging']= alu_shipment['C&P']
                        plot_frame['Liu_Consumer Durables'] = alu_shipment['ConDur']
                        plot_frame['Liu_Others'] = alu_shipment['Others']
                    except:
                        pass
                
                Exio_region_plotDict.append(plot_frame) 
                dict_2 = dict(zip(plotRegions,Exio_region_plotDict))
            material_region_dict.update({plotMaterial:dict_2})   
    
        # assemble data for one material end-use and ALL countries for use in plots 
        #ALU CONSTRUCTION
        end_use_all_aluConst =  pd.DataFrame([])# index=years_exio, columns=regions)
        for region in regions:
            end_use_region = pd.DataFrame(region_dict.get(region).get('alumin').loc['Construction']).rename(columns = {'Construction':region})
            end_use_all_aluConst[region] = end_use_region
        del end_use_region
        #end_use_all.T.plot( kind='box', title= 'Copper to Construction')
        
        #Steel CONSTRUCTION
        end_use_all_steelConst =  pd.DataFrame([])# index=years_exio, columns=regions)
        for region in regions:
            end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Construction']).rename(columns = {'Construction':region})
            end_use_all_steelConst[region] = end_use_region
        del end_use_region
        
        #Steel MOTOR VEHICLES
        end_use_all_steelMotor =  pd.DataFrame([])# index=years_exio, columns=regions)
        for region in regions:
            end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Motor vehicles, trailers and semi-trailers']).rename(columns = {'Construction':region})
            end_use_all_steelMotor[region] = end_use_region
        del end_use_region
        
        return material_region_dict, end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor

####################


'''SAVE dictionary of exio_shipment comparison for selected materials and
countries in dictionaries from functions: assemble_exiobase_comparison_x (x = agg, full)'''
def save_exiobase_shipment_results(path, file_name, materials, material_region_dict):
    writer = pd.ExcelWriter(path + file_name + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    for material in materials:
        for region, df in  material_region_dict.get(material).items():
            df.to_excel(writer, sheet_name= material + '_' + region)
    writer.save()  
    
####################
   

'''Plot FIGURE4 - EXIOBASE EUT-WIO results versus
industry shipments (some sector aggregated)'''

def plot_exiobase_agg(data_path_exio, data_path_shipments, years_exio, regions, material_region_dict,\
                      end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor):
    
    #AGGREGATED material_region DICTIONARY       
    dropped_sectors_aluSteel = ['Machinery and equipment n.e.c. ', 'Medical, precision and optical instruments, watches and clocks', \
                       'Office machinery and computers','Radio, television and communication equipment and apparatus',\
                        'Electrical machinery and apparatus n.e.c.', 'Office machinery and computers',  'Motor vehicles, trailers and semi-trailers',
                        'Other transport equipment', 'Secondary materials', 'Printed matter and recorded media', 'Other raw materials',\
                          'Energy carriers','Other','Products nec', 'Services','Textiles','Furniture; other manufactured goods n.e.c.','All other']
    
    dropped_sectors_plast = ['Machinery and equipment n.e.c. ', 'Medical, precision and optical instruments, watches and clocks', \
                       'Office machinery and computers','Radio, television and communication equipment and apparatus',\
                        'Electrical machinery and apparatus n.e.c.', 'Office machinery and computers',  'Motor vehicles, trailers and semi-trailers',
                        'Other transport equipment', 'Secondary materials', 'Printed matter and recorded media', 'Other raw materials',\
                          'Energy carriers','Other','Products nec', 'Services','Textiles','Furniture; other manufactured goods n.e.c.']
      
    pal = sns.color_palette("colorblind")
     
    color_dict = {'Construction':pal[0], 'Packaging_Euromap':pal[4], 'Automotive_Euromap':pal[1],'Electrical_Euromap':pal[2],'Construction_Euromap':pal[0],
                  'Other_Euromap':pal[7],'Jiang_Packaging':pal[4], 'Jiang_B&C':pal[0], 'Jiang_Automobile':pal[1],'Jiang_Electronics':pal[2],'Jiang_Agriculture':pal[8], 'Jiang_Others':pal[5],
    'PlastEU_Packaging':pal[4], 'PlastEU_B&C':pal[0], 'PlastEU_Automotive':pal[1], 'PlastEU_Electrical':pal[2], 'PlastEU_Agriculture':pal[7],
    'PlastEU_Others':pal[7], 'Wang_Construction':pal[0], 'Wang_Transportation':pal[1], 'Wang_Machinery&Appliances':pal[3], 'Wang_Appliances':pal[3], 
    'Wang_Other':pal[7], 'Pauliuk_Construction':pal[0], 'Pauliuk_Transportation':pal[1], 'Pauliuk_Machinery':pal[3],'Pauliuk_Products':pal[5],
     'Ciacci_B&C':pal[0], 'Ciacci_Electrical':pal[2], 'Ciacci_Machinery':pal[3], 'Ciacci_Transportation':pal[1], 'Ciacci_Products':pal[5],
     'Electrical machinery & appliances':pal[2], 'Transportation':pal[1], 'Other machinery & appliances':pal[3], 
     'Furniture; other manufactured goods n.e.c.':pal[7], 'Textiles':pal[9], 'Food':'maroon', 'All other':pal[5],
     'Liu_building&construction':pal[0], 'Liu_Transport':pal[1], 'Liu_Machinery&equipment':pal[3], 'Liu_Electric&electronics':pal[2],
     'Liu_Containers&packaging':pal[4], 'Liu_Consumer Durables':pal[7], 'Liu_Others':pal[7] } 
    
    marker_dict = {'Construction':'.-', 'Electrical machinery & appliances':'.-', 'Transportation':'.-', 
                   'Other machinery & appliances':'.-', 'Furniture; other manufactured goods n.e.c.':'.-', 
                   'Textiles':'.-', 'Food':'.-', 'All other':'.-' }
    
    
    china_steel = material_region_dict.get('steel').get('CN').replace(0,np.nan).drop(dropped_sectors_aluSteel,axis=1).drop('Wang_Other',axis=1)
    india_steel = material_region_dict.get('steel').get('IN').replace(0,np.nan).drop(dropped_sectors_aluSteel,axis=1)
    britain_steel= material_region_dict.get('steel').get('GB').replace(0,np.nan).drop(dropped_sectors_aluSteel,axis=1) 
    china_alumin = material_region_dict.get('alumin').get('CN').replace(0,np.nan).drop(dropped_sectors_aluSteel,axis=1).drop('Liu_Others',axis=1)
    india_alumin = material_region_dict.get('alumin').get('IN').replace(0,np.nan).drop(dropped_sectors_aluSteel,axis=1).drop('Liu_Others',axis=1)
    britain_alumin= material_region_dict.get('alumin').get('GB').replace(0,np.nan).drop(dropped_sectors_aluSteel,axis=1).drop('Liu_Others',axis=1)
    china_Plastic = material_region_dict.get('Plastic').get('CN').replace(0,np.nan).drop(dropped_sectors_plast,axis=1)
    india_Plastic = material_region_dict.get('Plastic').get('IN').replace(0,np.nan).drop(dropped_sectors_plast,axis=1)
    britain_Plastic= material_region_dict.get('Plastic').get('GB').replace(0,np.nan).drop(dropped_sectors_plast,axis=1)   
    dummy_df = china_steel.copy()
    dummy_df[:] = 0
  
    fig, axs = plt.subplots(5,3 ,sharex=False, sharey=False, figsize=(14,18),gridspec_kw={'height_ratios':[1,1,0.6,1,1]})
    
    china_steel.plot(ax=axs[0,0], kind='line', title= '(a) Steel China', legend = False, color= [color_dict.get(r) for r in china_steel], style=[marker_dict.get(r, '*') for r in china_steel])
    india_steel.plot(ax=axs[0,1], kind='line',title= '(b) Steel India', legend = False, color= [color_dict.get(r) for r in india_steel], style=[marker_dict.get(r, '*') for r in india_steel])
    britain_steel.plot(ax=axs[0,2], kind='line', title= '(c) Steel UK', legend = False, color= [color_dict.get(r) for r in britain_steel], style=[marker_dict.get(r, '*') for r in britain_steel])
    china_alumin.plot(ax=axs[1,0], kind='line', title= '(d) Aluminum China', legend = False, color= [color_dict.get(r) for r in china_alumin], style=[marker_dict.get(r, '*') for r in china_alumin])
    india_alumin.plot(ax=axs[1,1], kind='line',title= '(e) Aluminum India', legend = False, color= [color_dict.get(r) for r in india_alumin], style=[marker_dict.get(r, '*') for r in india_alumin])
    britain_alumin.plot(ax=axs[1,2], kind='line', title= '(f) Aluminum UK', legend = False, color= [color_dict.get(r) for r in britain_alumin], style=[marker_dict.get(r, '*') for r in britain_alumin])
    
    dummy_df.plot(ax=axs[2,0], legend = False)
    dummy_df.plot(ax=axs[2,1], legend = False)
    dummy_df.plot(ax=axs[2,2], legend = False)
    
    china_Plastic.plot(ax=axs[3,0], kind='line', title= '(g) Plastics China', legend = False, color= [color_dict.get(r) for r in china_Plastic], style=[marker_dict.get(r, '*') for r in china_Plastic])
    india_Plastic.plot(ax=axs[3,1], kind='line',title= '(h) Plastics India', legend = False, color= [color_dict.get(r) for r in india_Plastic], style=[marker_dict.get(r, '*') for r in india_Plastic])
    britain_Plastic.plot(ax=axs[3,2], kind='line', title= '(i) Plastics UK', legend = False, color= [color_dict.get(r) for r in britain_Plastic], style=[marker_dict.get(r, '*') for r in britain_Plastic])  
    
    sns.boxplot(ax=axs[4,0],data=end_use_all_aluConst.T,whis=[0, 100], width=.6, palette="vlag")
    sns.swarmplot(ax=axs[4,0],data=end_use_all_aluConst.T, size=2)
    sns.boxplot(ax=axs[4,1],data=end_use_all_steelConst.T,whis=[0, 100], width=.6, palette="vlag")
    sns.swarmplot(ax=axs[4,1],data=end_use_all_steelConst.T, size=2)
    sns.boxplot(ax=axs[4,2],data=end_use_all_steelMotor.T,whis=[0, 100], width=.6, palette="vlag")
    sns.swarmplot(ax=axs[4,2],data=end_use_all_steelMotor.T, size=2)
    axs[4,0].set(ylabel = '%', title = '(j) Aluminum Construction All Regions')
    axs[4,1].set(ylabel = '%', title = '(k) Steel Construction All Regions')
    axs[4,2].set(ylabel = '%', title = '(l) Steel Motor Vehicles All Regions')
    axs[4,0].set_xticklabels(years_exio,fontsize = 6)
    axs[4,1].set_xticklabels(years_exio,fontsize = 6)
    axs[4,2].set_xticklabels(years_exio,fontsize = 6)
    for i in range(0,4):
        for j in range (0,3):
                axs[i,j].set_ylabel('%')
                axs[i,j].set_xticks(list(range(1995,2012,2)))
                
    p = 0
    swarms = [end_use_all_aluConst,end_use_all_steelConst,end_use_all_steelMotor]
    for item in swarms:
        max_labels = pd.DataFrame(item.idxmax(axis=1))
        max_vals = item.max(axis=1)
        min_labels = pd.DataFrame(item.idxmin(axis=1))
        min_vals = item.min(axis=1)
        for i in range(0,17):
            axs[4,p].annotate(max_labels.iloc[i,:][0], xy=((i,max_vals.iloc[i])))
            axs[4,p].annotate(min_labels.iloc[i,:][0], xy=((i,min_vals.iloc[i])))
        p = p+1
        
    axs[2,0].clear()
    axs[2,0].axis('off')
    axs[2,1].clear()
    axs[2,1].axis('off')
    axs[2,2].clear()
    axs[2,2].axis('off')
     
    lgd = fig.legend(loc='center', bbox_to_anchor=(0.5, 0.48),fontsize=14, ncol=3)
    
    def add_line(legend):
        from matplotlib.lines import Line2D
        a = axs[3,0].get_legend_handles_labels()[0][:6] 
        b = axs[3,0].get_legend_handles_labels()[1][:6] 
        c = tuple((a,b))
        handles, labels = c
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
        
        handles.append(Line2D([0],[0],color=pal[0],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Construction")
        handles.append(Line2D([0],[0],color=pal[1],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Transportation")
        handles.append(Line2D([0],[0],color=pal[2],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Electrical")
        handles.append(Line2D([0],[0],color=pal[3],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Machinery&Appl.")
        handles.append(Line2D([0],[0],color=pal[4],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Packaging")
        handles.append(Line2D([0],[0],color=pal[7],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Other")
        
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
    
    add_line(lgd)
    fig.suptitle('EXIOBASE all end-uses for selected regions (a-i) and all regions for selected end-uses (j-l)', y=1, fontsize = 16)
    fig.tight_layout()
    
    # add differences between shipments and EXIOBASE shares 
    figure_4_frames = {'china_steel':china_steel, 'india_steel':india_steel, 'britain_steel':britain_steel, 'china_alumin':china_alumin, 'india_alumin':india_alumin,\
                       'britain_alumin':britain_alumin, 'china_Plastic':china_Plastic, 'india_Plastic':india_Plastic, 'britain_Plastic':britain_Plastic, 'end_use_all_aluConst':end_use_all_aluConst,\
                        'end_use_all_steelConst':end_use_all_steelConst, 'end_use_all_steelMotor':end_use_all_steelMotor}
      
    for key, value in figure_4_frames.items():
        try:
            value['ExioConstruct-Construction_Euromap'] = value['Construction'] - value['Construction_Euromap']
            value['ExioTransport-Automotive_Euromap'] = value['Transportation'] - value['Automotive_Euromap']
            value['ExioMachElectric-Electrical_Euromap'] = value['Electrical machinery & appliances'] + value['Other machinery & appliances']  - value['Electrical_Euromap']
            value['rel_Construction_Euromap'] = value['ExioConstruct-Construction_Euromap'] / value['Construction_Euromap']
            value['rel_Automotive_Euromap'] = value['ExioTransport-Automotive_Euromap'] / value['Automotive_Euromap']
            value['rel_Electrical_Euromap'] = value['ExioMachElectric-Electrical_Euromap'] / value['Electrical_Euromap']
        except:
            pass      
        try:
            value['ExioConstruct-Jiang_B&C'] = value['Construction'] - value['Jiang_B&C']
            value['ExioTransport-Jiang_Automobile'] = value['Transportation'] - value['Jiang_Automobile']
            value['ExioMachElectric-Jiang_Electronics'] = value['Electrical machinery & appliances'] + value['Other machinery & appliances']  - value['Jiang_Electronics']
            value['rel_Jiang_B&C'] = value['ExioConstruct-Jiang_B&C'] / value['Jiang_B&C']
            value['rel_Jiang_Automobile'] = value['ExioTransport-Jiang_Automobile'] / value['Jiang_Automobile']
            value['rel_Jiang_Electronics'] = value['ExioMachElectric-Jiang_Electronics'] / value['Jiang_Electronics']
        except:
            pass     
        try:
            value['ExioConstruct-PlastEU_B&C'] = value['Construction'] - value['PlastEU_B&C']
            value['ExioTransport-PlastEU_Automotive'] = value['Transportation'] - value['PlastEU_Automotive']
            value['ExioMachElectric-PlastEU_Electrical'] = value['Electrical machinery & appliances'] + value['Other machinery & appliances']  - value['PlastEU_Electrical']
            value['rel_PlastEU_B&C'] = value['ExioConstruct-PlastEU_B&C'] / value['PlastEU_B&C']
            value['rel_PlastEU_Automotive'] = value['ExioTransport-PlastEU_Automotive'] / value['PlastEU_Automotive']
            value['rel_PlastEU_Electrical'] = value['ExioMachElectric-PlastEU_Electrical'] / value['PlastEU_Electrical']
        except:
            pass  
        try:
            value['ExioConstruct-Wang_Construction'] = value['Construction'] - value['Wang_Construction']
            value['ExioTransport-Wang_Transportation'] = value['Transportation'] - value['Wang_Transportation']
            value['ExioMachElectric-Wang_Mach&Appliances'] = value['Electrical machinery & appliances'] + value['Other machinery & appliances']  - value['Wang_Machinery'] - value['Wang_Appliances']
            value['rel_Wang_Construction'] = value['ExioConstruct-Wang_Construction'] / value['Wang_Construction']
            value['rel_Wang_Transportation'] = value['ExioTransport-Wang_Transportation'] / value['Wang_Transportation']
            value['rel_Wang_Mach&Appliances'] = value['ExioMachElectric-Wang_Mach&Appliances'] / (value['Wang_Machinery'] - value['Wang_Appliances'])
        except:
            pass  
        try:
            value['ExioConstruct-Pauliuk_Construction'] = value['Construction'] - value['Pauliuk_Construction']
            value['ExioTransport-Pauliuk_Transportation'] = value['Transportation'] - value['Pauliuk_Transportation']
            value['ExioMachElectric-Pauliuk_Machinery'] = value['Electrical machinery & appliances'] + value['Other machinery & appliances']  - value['Pauliuk_Machinery']
            value['rel_Pauliuk_Construction'] = value['ExioConstruct-Pauliuk_Construction'] / value['Pauliuk_Construction']
            value['rel_Pauliuk_Transportation'] = value['ExioTransport-Pauliuk_Transportation'] / value['Pauliuk_Transportation']
            value['rel_Pauliuk_Machinery'] = value['ExioMachElectric-Pauliuk_Machinery'] / value['Pauliuk_Machinery']
        except:
            pass
        try:
            value['ExioConstruct-Liu_building&construction'] = value['Construction'] - value['Liu_building&construction']
            value['ExioTransport-Liu_Transport'] = value['Transportation'] - value['Liu_Transport']
            value['ExioOtherMach-Liu_Machinery&equipment'] =  value['Other machinery & appliances']  - value['Liu_Machinery&equipment']
            value['ExioElectric-Liu_Electric&electronics'] =   value['Electrical machinery & appliances']   -  value['Liu_Electric&electronics']
            value['rel_Liu_building&construction'] = value['ExioConstruct-Liu_building&construction'] / value['Liu_building&construction']
            value['rel_Liu_Transport'] = value['ExioTransport-Liu_Transport'] / value['Liu_Transport']
            value['rel_Liu_Machinery&equipment'] = value['ExioOtherMach-Liu_Machinery&equipment'] / value['Liu_Machinery&equipment']
            value['rel_Liu_Electric&electronics'] = value['ExioElectric-Liu_Electric&electronics'] / value['Liu_Electric&electronics']
        except:
            pass
    
    return fig, figure_4_frames

########################


'''Plot FIGURE4 - EXIOBASE EUT-WIO results versus
industry shipments (full sector detail)'''

def plot_exiobase_full(data_path_exio, data_path_shipments, years_exio, regions, material_region_dict,\
                      end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor):
    
    ##FULL material_region DICTIONARY    
    dropped_sectors = ['Machinery and equipment n.e.c. ', 'Medical, precision and optical instruments, watches and clocks', \
                        'Office machinery and computers','Radio, television and communication equipment and apparatus',\
                        'Electrical machinery and apparatus n.e.c.', 'Office machinery and computers',  'Motor vehicles, trailers and semi-trailers',
                        'Other transport equipment', 'Secondary materials', 'Printed matter and recorded media', 'Other raw materials',\
                          'Energy carriers','Other','Products nec', 'Services' ]
    
    pal = sns.color_palette("colorblind")
     
    color_dict = {'Construction':pal[0], 'Packaging_Euromap':pal[4], 'Automotive_Euromap':pal[1],'Electrical_Euromap':pal[2],'Construction_Euromap':pal[0],
                  'Other_Euromap':pal[7],'Jiang_Packaging':pal[4], 'Jiang_B&C':pal[0], 'Jiang_Automobile':pal[1],'Jiang_Electronics':pal[2],'Jiang_Agriculture':pal[8], 'Jiang_Others':pal[5],
    'PlastEU_Packaging':pal[4], 'PlastEU_B&C':pal[0], 'PlastEU_Automotive':pal[1], 'PlastEU_Electrical':pal[2], 'PlastEU_Agriculture':pal[7],
    'PlastEU_Others':pal[7], 'Wang_Construction':pal[0], 'Wang_Transportation':pal[1], 'Wang_Machinery&Appliances':pal[3], 'Wang_Appliances':pal[3], 
    'Wang_Other':pal[7], 'Pauliuk_Construction':pal[0], 'Pauliuk_Transportation':pal[1], 'Pauliuk_Machinery':pal[3],'Pauliuk_Products':pal[5],
     'Ciacci_B&C':pal[0], 'Ciacci_Electrical':pal[2], 'Ciacci_Machinery':pal[3], 'Ciacci_Transportation':pal[1], 'Ciacci_Products':pal[5],
     'Electrical machinery & appliances':pal[2], 'Transportation':pal[1], 'Other machinery & appliances':pal[3], 
     'Furniture; other manufactured goods n.e.c.':pal[7], 'Textiles':pal[9], 'Food':'maroon', 'All other':pal[5],
     'Liu_building&construction':pal[0], 'Liu_Transport':pal[1], 'Liu_Machinery&equipment':pal[3], 'Liu_Electric&electronics':pal[2],
     'Liu_Containers&packaging':pal[4], 'Liu_Consumer Durables':pal[7], 'Liu_Others':pal[7] } 
    
    marker_dict = {'Construction':'.-', 'Electrical machinery & appliances':'.-', 'Transportation':'.-', 
                   'Other machinery & appliances':'.-', 'Furniture; other manufactured goods n.e.c.':'.-', 
                   'Textiles':'.-', 'Food':'.-', 'All other':'.-' }
    
    # # ##FULL material_region DICTIONARY    
    china_steel = material_region_dict.get('steel').get('CN').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Wang_Other',axis=1)
    india_steel = material_region_dict.get('steel').get('IN').replace(0,np.nan).drop(dropped_sectors,axis=1)
    britain_steel= material_region_dict.get('steel').get('GB').replace(0,np.nan).drop(dropped_sectors,axis=1) 
    china_alumin = material_region_dict.get('alumin').get('CN').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Liu_Others',axis=1)
    india_alumin = material_region_dict.get('alumin').get('IN').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Liu_Others',axis=1)
    britain_alumin= material_region_dict.get('alumin').get('GB').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Liu_Others',axis=1)
    china_Plastic = material_region_dict.get('Plastic').get('CN').replace(0,np.nan).drop(dropped_sectors,axis=1)
    india_Plastic = material_region_dict.get('Plastic').get('IN').replace(0,np.nan).drop(dropped_sectors,axis=1)
    britain_Plastic= material_region_dict.get('Plastic').get('GB').replace(0,np.nan).drop(dropped_sectors,axis=1) 
    dummy_df = china_steel.copy()
    dummy_df[:] = 0
    
    
    fig, axs = plt.subplots(5,3 ,sharex=False, sharey=False, figsize=(14,18),gridspec_kw={'height_ratios':[1,1,0.6,1,1]})
    
    china_steel.plot(ax=axs[0,0], kind='line', title= '(a) Steel China', legend = False, color= [color_dict.get(r) for r in china_steel], style=[marker_dict.get(r, '*') for r in china_steel])
    india_steel.plot(ax=axs[0,1], kind='line',title= '(b) Steel India', legend = False, color= [color_dict.get(r) for r in india_steel], style=[marker_dict.get(r, '*') for r in india_steel])
    britain_steel.plot(ax=axs[0,2], kind='line', title= '(c) Steel UK', legend = False, color= [color_dict.get(r) for r in britain_steel], style=[marker_dict.get(r, '*') for r in britain_steel])
    china_alumin.plot(ax=axs[1,0], kind='line', title= '(d) Aluminum China', legend = False, color= [color_dict.get(r) for r in china_alumin], style=[marker_dict.get(r, '*') for r in china_alumin])
    india_alumin.plot(ax=axs[1,1], kind='line',title= '(e) Aluminum India', legend = False, color= [color_dict.get(r) for r in india_alumin], style=[marker_dict.get(r, '*') for r in india_alumin])
    britain_alumin.plot(ax=axs[1,2], kind='line', title= '(f) Aluminum UK', legend = False, color= [color_dict.get(r) for r in britain_alumin], style=[marker_dict.get(r, '*') for r in britain_alumin])
    dummy_df.plot(ax=axs[2,0], legend = False)
    dummy_df.plot(ax=axs[2,1], legend = False)
    dummy_df.plot(ax=axs[2,2], legend = False)
    
    china_Plastic.plot(ax=axs[3,0], kind='line', title= '(g) Plastics China', legend = False, color= [color_dict.get(r) for r in china_Plastic], style=[marker_dict.get(r, '*') for r in china_Plastic])
    india_Plastic.plot(ax=axs[3,1], kind='line',title= '(h) Plastics India', legend = False, color= [color_dict.get(r) for r in india_Plastic], style=[marker_dict.get(r, '*') for r in india_Plastic])
    britain_Plastic.plot(ax=axs[3,2], kind='line', title= '(i) Plastics UK', legend = False, color= [color_dict.get(r) for r in britain_Plastic], style=[marker_dict.get(r, '*') for r in britain_Plastic])
    
    sns.boxplot(ax=axs[4,0],data=end_use_all_aluConst.T,whis=[0, 100], width=.6, palette="vlag")
    sns.swarmplot(ax=axs[4,0],data=end_use_all_aluConst.T, size=2)
    sns.boxplot(ax=axs[4,1],data=end_use_all_steelConst.T,whis=[0, 100], width=.6, palette="vlag")
    sns.swarmplot(ax=axs[4,1],data=end_use_all_steelConst.T, size=2)
    sns.boxplot(ax=axs[4,2],data=end_use_all_steelMotor.T,whis=[0, 100], width=.6, palette="vlag")
    sns.swarmplot(ax=axs[4,2],data=end_use_all_steelMotor.T, size=2)
    axs[4,0].set(ylabel = '%', title = '(j) Aluminum Construction All Regions')
    axs[4,1].set(ylabel = '%', title = '(k) Steel Construction All Regions')
    axs[4,2].set(ylabel = '%', title = '(l) Steel Motor Vehicles All Regions')
    axs[4,0].set_xticklabels(years_exio,fontsize = 6)
    axs[4,1].set_xticklabels(years_exio,fontsize = 6)
    axs[4,2].set_xticklabels(years_exio,fontsize = 6)
    for i in range(0,4):
        for j in range (0,3):
                axs[i,j].set_ylabel('%')
                axs[i,j].set_xticks(list(range(1995,2012,2)))
                
    p = 0
    swarms = [end_use_all_aluConst,end_use_all_steelConst,end_use_all_steelMotor]
    for item in swarms:
        max_labels = pd.DataFrame(item.idxmax(axis=1))
        max_vals = item.max(axis=1)
        min_labels = pd.DataFrame(item.idxmin(axis=1))
        min_vals = item.min(axis=1)
        for i in range(0,17):
            axs[4,p].annotate(max_labels.iloc[i,:][0], xy=((i,max_vals.iloc[i])))
            axs[4,p].annotate(min_labels.iloc[i,:][0], xy=((i,min_vals.iloc[i])))
        p = p+1
        
    axs[2,0].clear()
    axs[2,0].axis('off')
    axs[2,1].clear()
    axs[2,1].axis('off')
    axs[2,2].clear()
    axs[2,2].axis('off')
     
    lgd = fig.legend(loc='center', bbox_to_anchor=(0.5, 0.48),fontsize=14, ncol=3)
    
    def add_line(legend):
        #ax1 = legend.axes
        from matplotlib.lines import Line2D
    
        #import matplotlib.patches as mpatches
        a = axs[3,0].get_legend_handles_labels()[0][:6] 
        b = axs[3,0].get_legend_handles_labels()[1][:6] 
        c = tuple((a,b))
        handles, labels = c
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
        
        handles.append(Line2D([0],[0],color=pal[0],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Construction")
        handles.append(Line2D([0],[0],color=pal[1],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Transportation")
        handles.append(Line2D([0],[0],color=pal[2],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Electrical")
        handles.append(Line2D([0],[0],color=pal[3],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Machinery&Appl.")
        handles.append(Line2D([0],[0],color=pal[4],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Packaging")
        handles.append(Line2D([0],[0],color=pal[7],linewidth=3, marker='*', linestyle='None', markersize=9))
        labels.append("Shipment_Other")
        
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)
        legend.set_title(legend.get_title().get_text())
    
    add_line(lgd)
    fig.suptitle('EXIOBASE all end-uses for selected regions (a-i) and all regions for selected end-uses (j-l)', y=1, fontsize = 16)
    fig.tight_layout()
    return fig

####################

'''Plot additional countries: EXIOBASE plots in SI 1.3.3 (comparison of country-level 
industry shipments with MIOT-based results for selected materials)'''
## needs to be run with FULL DETAIL material_region_dictionary

def plots_exiobase_shipment_add_countries(material_region_dict, materials):
    dropped_sectors = ['Machinery and equipment n.e.c. ', 'Medical, precision and optical instruments, watches and clocks', \
                        'Office machinery and computers','Radio, television and communication equipment and apparatus',\
                        'Electrical machinery and apparatus n.e.c.', 'Office machinery and computers',  'Motor vehicles, trailers and semi-trailers',
                        'Other transport equipment', 'Secondary materials', 'Printed matter and recorded media', 'Other raw materials',\
                          'Energy carriers','Other','Products nec', 'Services' ]
    
    pal = sns.color_palette("colorblind")
    color_dict = {'Construction':pal[0], 'Packaging_Euromap':pal[4], 'Automotive_Euromap':pal[1],'Electrical_Euromap':pal[2],'Construction_Euromap':pal[0],
                  'Other_Euromap':pal[7],'Jiang_Packaging':pal[4], 'Jiang_B&C':pal[0], 'Jiang_Automobile':pal[1],'Jiang_Electronics':pal[2],'Jiang_Agriculture':pal[8], 'Jiang_Others':pal[5],
    'PlastEU_Packaging':pal[4], 'PlastEU_B&C':pal[0], 'PlastEU_Automotive':pal[1], 'PlastEU_Electrical':pal[2], 'PlastEU_Agriculture':pal[7],
    'PlastEU_Others':pal[7], 'Wang_Construction':pal[0], 'Wang_Transportation':pal[1], 'Wang_Machinery&Appliances':pal[3], 'Wang_Appliances':pal[3], 
    'Wang_Other':pal[7], 'Pauliuk_Construction':pal[0], 'Pauliuk_Transportation':pal[1], 'Pauliuk_Machinery':pal[3],'Pauliuk_Products':pal[5],
     'Ciacci_B&C':pal[0], 'Ciacci_Electrical':pal[2], 'Ciacci_Machinery':pal[3], 'Ciacci_Transportation':pal[1], 'Ciacci_Products':pal[5],
     'Electrical machinery & appliances':pal[2], 'Transportation':pal[1], 'Other machinery & appliances':pal[3], 
     'Furniture; other manufactured goods n.e.c.':pal[7], 'Textiles':pal[9], 'Food':'maroon', 'All other':pal[5],
     'Liu_building&construction':pal[0], 'Liu_Transport':pal[1], 'Liu_Machinery&equipment':pal[3], 'Liu_Electric&electronics':pal[2],
     'Liu_Containers&packaging':pal[4], 'Liu_Consumer Durables':pal[7], 'Liu_Others':pal[7] } 
    
    marker_dict = {'Construction':'.-', 'Electrical machinery & appliances':'.-', 'Transportation':'.-', 
                   'Other machinery & appliances':'.-', 'Furniture; other manufactured goods n.e.c.':'.-', 
                   'Textiles':'.-', 'Food':'.-', 'All other':'.-' }
    
    for material in materials:
        for region, df in  material_region_dict.get(material).items():
            df = df.replace(0,np.nan).drop(dropped_sectors,axis=1)
            df.plot( ylabel = '%', title= material + '_' + region, kind='line', color= [color_dict.get(r) for r in df], style=[marker_dict.get(r, '*') for r in df], legend=False)
