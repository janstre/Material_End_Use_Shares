# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 17:11:33 2022

@author: jstreeck
"""
import numpy as np
import pandas as pd
from openpyxl import load_workbook

def save_list2Excel(path, matEndUse_nameList, matEndUse_dfList):
    list2dict = dict(zip(matEndUse_nameList, matEndUse_dfList))
    writer = pd.ExcelWriter(path + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    for df_name, df in  list2dict.items():
        df.to_excel(writer, sheet_name=df_name)
    writer.save()

def save_dict2Excel(path, diction):
    writer = pd.ExcelWriter(path + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
    for df_name, df in  diction.items():
        df.to_excel(writer, sheet_name=str(df_name))
    writer.save()


'''function calculating deviation per dataframe for HT-WIO and Industry Shipments'''
def calc_relDeviation(frame):
    import statistics 
    
    frame_cop = frame.copy()
    rel_deviation = []
    try:
        frame_cop['HT-Shipment1'] = frame_cop['HT-WIO'] - frame_cop['Shipment_1']
        frame_cop['HT-Shipment1_rel']  = (frame_cop['HT-WIO'] - frame_cop['Shipment_1'])/frame_cop['Shipment_1']
        rel_deviation.append(frame_cop['HT-Shipment1_rel'].dropna().values.tolist())
    except Exception:
        pass   
    try:
        frame_cop['HT-Shipment2']  = frame_cop['HT-WIO'] - frame_cop['Shipment_2']
        frame_cop['HT-Shipment2_rel']  = (frame_cop['HT-WIO'] - frame_cop['Shipment_2'])/frame_cop['Shipment_2']
        rel_deviation.append(frame_cop['HT-Shipment2_rel'].dropna().values.tolist())
    except Exception:
        pass
    try:
        frame_cop['HT-Shipment3']  = frame_cop['HT-WIO'] - frame_cop['Shipment_3']
        frame_cop['HT-Shipment3_rel']  = (frame_cop['HT-WIO'] - frame_cop['Shipment_3'])/frame_cop['Shipment_3']
        rel_deviation.append(frame_cop['HT-Shipment3_rel'].dropna().values.tolist())
    except Exception:
        pass
    
    
    rel_deviation_abs =  [abs(x) for x in sum(rel_deviation, [])]
    rel_dev_med = statistics.median(rel_deviation_abs )
    quantiles = statistics.quantiles(rel_deviation_abs,  n=40, method='exclusive')
    lower = quantiles[0] - rel_dev_med
    upper = quantiles[-1] - rel_dev_med
    maxim = max(rel_deviation_abs)
    minim = min(rel_deviation_abs)
    return rel_dev_med, minim, maxim

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
    wood_construction_df['Exio_HT-WIO'] = region_dict.get('US').get('wood').loc['Construction']
    # wood_construction_df.plot(kind='line',marker='o', title= 'Wood in Construction', legend = False)
    # plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    # plt.xticks(years)
    # plt.ylabel('%')
    # plt.show()
    
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
    wood_furniture_df['Exio_HT-WIO'] = region_dict.get('US').get('wood').loc['Furniture; other manufactured goods n.e.c.']
    
    
    #packaging
    wood_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_packaging_food_df[method_name] = Wood_dict.get(method_name).loc['Packaging']  + Wood_dict.get(method_name).loc['Food products']
    wood_packaging_food_df['Shipment_1'] = phys_dict.get('pd_Wood').T.loc['Packaging and shippling']*100 #'McKeever_packag.'
    wood_packaging_food_df['Exio_HT-WIO'] = region_dict.get('US').get('wood').loc['Food']
    
    
    #transport
    wood_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_transport_df[method_name] = Wood_dict.get(method_name).loc['Motor vehicles'] + Wood_dict.get(method_name).loc['Other transport equipment']
    wood_transport_df['Exio_HT-WIO'] = region_dict.get('US').get('wood').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('wood').loc['Other transport equipment']
    
    
    #machinery
    wood_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        wood_machinery_df[method_name] = Wood_dict.get(method_name).loc['Electronic machinery'] + Wood_dict.get(method_name).loc['Other machinery']
    wood_machinery_df['Exio_HT-WIO'] = region_dict.get('US').get('wood').loc['Machinery and equipment n.e.c. '] +\
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
    alu_construction_df['Exio_HT-WIO'] = region_dict.get('US').get('alumin').loc['Construction']
    
    #transport
    alu_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_transport_df[method_name] = alu_dict.get(method_name).loc['Motor vehicles'] + alu_dict.get(method_name).loc['Other transport equipment']
    alu_transport_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Transportation']*100
    alu_transport_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Transportation']*100
    alu_transport_df['Exio_HT-WIO'] = region_dict.get('US').get('alumin').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('alumin').loc['Other transport equipment']
    
    #packaging (assuming that also material in 'food products' is packaging)
    alu_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_packaging_food_df[method_name] = alu_dict.get(method_name).loc['Packaging'] + alu_dict.get(method_name).loc['Food products']
    alu_packaging_food_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Containers and packaging']*100
    alu_packaging_food_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Containers and packaging']*100
    alu_packaging_food_df['Exio_HT-WIO'] = region_dict.get('US').get('alumin').loc['Food']
    
    #machinery
    alu_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        alu_machinery_df[method_name] = alu_dict.get(method_name).loc['Electronic machinery'] + alu_dict.get(method_name).loc['Other machinery']
    alu_machinery_df['Shipment_1'] = phys_dict.get('pd_Alu').T.loc['USGS Electrical']*100 +phys_dict.get('pd_Alu').T.loc['USGS Machinery and equipment']*100 #USGS_mach.&equipm.+electrical'
    alu_machinery_df['Shipment_2'] = phys_dict.get('pd_Alu').T.loc['Liu Electrical']*100 +phys_dict.get('pd_Alu').T.loc['Liu Machinery and equipment']*100 #Liu_mach.&equipm.+electrical'
    alu_machinery_df['Exio_HT-WIO'] = region_dict.get('US').get('alumin').loc['Machinery and equipment n.e.c. '] +\
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
    alu_furniture_df['Exio_HT-WIO'] = region_dict.get('US').get('alumin').loc['Furniture; other manufactured goods n.e.c.']
    
    
    
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
    steel_construction_df['Exio_HT-WIO'] = region_dict.get('US').get('steel').loc['Construction']
    
    #transport
    steel_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_transport_df[method_name] = steel_dict.get(method_name).loc['Motor vehicles'] + steel_dict.get(method_name).loc['Other transport equipment']
    steel_transport_df['Shipment_1'] = phys_dict.get('pd_IronSteel').T.loc['Transportation USGS+Trade']*100
    steel_transport_df['Shipment_2'] = phys_dict.get('pd_IronSteel').T.loc['Transport YSTAFB']*100
    steel_transport_df['Shipment_3'] = phys_dict.get('pd_IronSteel').T.loc['Automotive Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
        + phys_dict.get('pd_IronSteel').T.loc['Shipbuilding Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Aircraft Pauliuk']*100
    steel_transport_df['Exio_HT-WIO'] = region_dict.get('US').get('steel').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('steel').loc['Other transport equipment']
    
    #packaging (assuming that also material in 'food products' is packaging)
    steel_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_packaging_food_df[method_name] = steel_dict.get(method_name).loc['Packaging'] + steel_dict.get(method_name).loc['Food products']
    steel_packaging_food_df['Shipment_1'] = phys_dict.get('pd_IronSteel').T.loc['Containers USGS+Trade']*100
    steel_packaging_food_df['Exio_HT-WIO'] = region_dict.get('US').get('steel').loc['Food']
    steel_packaging_food_df['Shipment_3'] = phys_dict.get('pd_IronSteel').T.loc['Containers, shipping materials Pauliuk']*100
    
    #machinery
    steel_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        steel_machinery_df[method_name] = steel_dict.get(method_name).loc['Other machinery'] + steel_dict.get(method_name).loc['Electronic machinery']
    steel_machinery_df['Shipment_2'] = phys_dict.get('pd_IronSteel').T.loc['Machinery & Appliances YSTAFB']*100
    steel_machinery_df['Exio_HT-WIO'] = region_dict.get('US').get('steel').loc['Machinery and equipment n.e.c. '] +\
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
    steel_furniture_df['Exio_HT-WIO'] = region_dict.get('US').get('steel').loc['Furniture; other manufactured goods n.e.c.']
    
    
    '''USA - - COPPER (some problems assembling the material dict so took the easy way)''' 
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
        
    ##values are NOT in the correct sequence --> plots still work I think, check!
    
    #construction
    copper_construction_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_construction_df[method_name] = copper_dict.get(method_name).loc['Residential'] + copper_dict.get(method_name).loc['Non-Residential'] + copper_dict.get(method_name).loc['Other buildings'] + copper_dict.get(method_name).loc['Infrastructure'] + copper_dict.get(method_name).loc['Other construction']
    copper_construction_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Building construction USGS+Trade']*100
    copper_construction_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Building construction CDA+Trade']*100
    copper_construction_df['Exio_HT-WIO'] = region_dict.get('US').get('Copper').loc['Construction']
    
    
    #transportation
    copper_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_transport_df[method_name] = copper_dict.get(method_name).loc['Motor vehicles'] + copper_dict.get(method_name).loc['Other transport equipment']
    copper_transport_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Transportation equipment USGS+Trade']*100
    copper_transport_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Transportation equipment CDA+Trade']*100
    copper_transport_df['Exio_HT-WIO'] = region_dict.get('US').get('Copper').loc['Motor vehicles, trailers and semi-trailers'] +\
        region_dict.get('US').get('Copper').loc['Other transport equipment']
    
    #machinery
    copper_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        copper_machinery_df[method_name] = copper_dict.get(method_name).loc['Electronic machinery'] + copper_dict.get(method_name).loc['Other machinery']
    copper_machinery_df['Shipment_1'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products USGS+Trade']*100 +phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment USGS+Trade']*100
    copper_machinery_df['Shipment_2'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products CDA+Trade']*100 +phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment CDA+Trade']*100
    copper_machinery_df['Exio_HT-WIO'] = region_dict.get('US').get('Copper').loc['Machinery and equipment n.e.c. '] +\
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
    copper_furniture_df['Exio_HT-WIO'] = region_dict.get('US').get('Copper').loc['Furniture; other manufactured goods n.e.c.']
    
    
    
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
    plastic_construction_df['Exio_HT-WIO'] = region_dict.get('US').get('Plastic').loc['Construction']
    
    #packaging (assuming that also material in 'food products' is packaging)
    plastic_packaging_food_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_packaging_food_df[method_name] = plastic_dict.get(method_name).loc['Packaging'] + plastic_dict.get(method_name).loc['Food products'] 
    plastic_packaging_food_df['Shipment_1'] = phys_dict.get('pd_Plastics').T.loc['Packaging Euromap USA']*100
    plastic_packaging_food_df['Shipment_2'] = phys_dict.get('pd_Plastics').T.loc['Packaging PE']*100 #'PlasticsEurope_EU_packag.'
    plastic_packaging_food_df['Exio_HT-WIO'] = region_dict.get('US').get('Plastic').loc['Food']
    
    #transport (assuming that also material in 'food products' is transport)
    plastic_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
    for method_name in method_names:
        plastic_transport_df[method_name] = plastic_dict.get(method_name).loc['Motor vehicles'] + plastic_dict.get(method_name).loc['Other transport equipment'] 
    plastic_transport_df['Shipment_1'] = phys_dict.get('pd_Plastics').T.loc['Automotive Euromap USA']*100
    plastic_transport_df['Shipment_2'] = phys_dict.get('pd_Plastics').T.loc['Automotive PE']*100
    plastic_transport_df['Exio_HT-WIO'] = region_dict.get('US').get('Plastic').loc['Motor vehicles, trailers and semi-trailers'] +\
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
    plastic_furniture_df['Exio_HT-WIO'] = region_dict.get('US').get('Plastic').loc['Furniture; other manufactured goods n.e.c.']
    
    return plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
        alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
        copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
        steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
        cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df