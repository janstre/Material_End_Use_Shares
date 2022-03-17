# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 14:51:52 2020

@author: jstreeck
"""

import numpy as np
import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import random
import os
import sys

main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
data_path_usa = os.path.join(main_path, 'output/USA/')
data_path_exio = os.path.join(main_path, 'output/Exiobase/')

'''
    #1 Load USA national tables
'''

years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]

#1 read files for all methods and years into dictionaries

CBA_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'CBA_' + str(year) + '_Base' + '*.xlsx'))):
        CBA_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    CBA_dict[year] = CBA_single
    
# CBA_ext_dict = {}
# for year in years:
#     for file in glob.glob(os.path.join((data_path_usa + 'CBA_' + str(year) +'_ExtAgg' + '*.xlsx'))):
#         CBA_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
#     CBA_ext_dict[year] = CBA_single
    
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
    
HTWio_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'HT_WIOMF_' + str(year) + '_Base' + '*.xlsx'))):
        HTWio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    HTWio_dict[year] = HTWio_single
    
HTWio_ext_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'HT_WIOMF_' + str(year) + '_Base' + '*.xlsx'))):
        HTWio_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0,1])
    HTWio_ext_dict[year] = HTWio_single
    
HTWio_detail_dict = {}
for year in years:
    for file in glob.glob(os.path.join((data_path_usa + 'HT_WIOMF_' + str(year) + '_Base' + '*.xlsx'))):
        HTWio_detail_single = pd.read_excel(file, sheet_name='EndUse_shares',index_col=[0,1],header=[0,1])
    HTWio_detail_dict[year] = HTWio_detail_single 
    
phys_materials = ['pd_IronSteel','pd_Alu','pd_Copper','pd_Wood','pd_Cement','pd_Plastics']

phys_dict = {}
for material in phys_materials:
    frame= pd.read_excel('C:/Users/jstreeck/Desktop/EndUse_shortTermSave/SectorSplit_WasteFilter_physical/USA_SectorSplit/US_SectorSplitData.xlsx',sheet_name=material).set_index('Year')
    dict_ele = {material:frame}
    phys_dict.update(dict_ele)
    
    
    
    
    
'''
    #2 Load Exiobase tables/results (so far with HT_WIO only)
'''


year = 1995
years_exio = list(range(1995,2012))
# regions = ['US','AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR',\
#   'HR', 'HU', 'IE', 'IT', 'US', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO',\
#      'SE', 'SI', 'SK', 'GB','JP', 'CN', 'CA', 'KR', 'BR', 'IN', 'MX',\
#       'RU', 'AU', 'CH', 'TR', 'TW', 'NO', 'ID', 'ZA', 'WA', 'WL', 'WE', 'WF',\
#        'WM'] #'US' not in above as already run
    
regions = ['US'] #'US' not in above as already run

Exio_dict = {}

for region in regions:
    Region_dict = {}
    for year in years_exio:
        for file in glob.glob(os.path.join((data_path_exio + 'Exio_HT_WIOMF_' + str(year) + '_' + region + '*.xlsx'))):
            Region_single = pd.read_excel(file, sheet_name='EndUse_shares_agg',index_col=[0,1],header=[0])
        Region_dict[year] = Region_single
    Exio_dict[region] = Region_dict

# single country all end-uses plot:
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
    





'''
    #3 Assemble detailed comparison for USA national data + shipments + Exiobase (selected method)
'''





methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, HTWio_dict]
method_names = ['CBA', 'WIO', 'Ghosh', 'ParGhosh', 'HT-WIO']
years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]
#exio mat = ['steel', 'wood', 'Plastic', 'glass', 'alumin', 'tin', 'Copper']
#exio_enduse
#'Construction', 'Machinery and equipment n.e.c. ','Office machinery and computers (30)',
# 'Electrical machinery and apparatus n.e.c. (31)','Radio, television and communication equipment and apparatus (32)',
# 'Medical, precision and optical instruments, watches and clocks (33)','Motor vehicles, trailers and semi-trailers (34)',
# 'Other transport equipment (35)','Furniture; other manufactured goods n.e.c. (36)', 'Textiles (17)',
# 'Printed matter and recorded media (22)', 'Food', 'Other raw materials','Secondary materials', 
# 'Energy carriers', 'Energy carriers.1', 'Other','Products nec', 'Services']

# WOOD
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
wood_construction_df['McKeever_constr.'] = phys_dict.get('pd_Wood').T.loc['Construction total']
wood_construction_df['Exio_HTwio'] = region_dict.get('US').get('wood').loc['Construction']
wood_construction_df.plot(kind='line',marker='o', title= 'Wood in Construction', legend = False)
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()


#residential
wood_residential_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    wood_residential_df[method_name] = Wood_dict.get(method_name).loc['Residential']
wood_residential_df['McKeever_resid.build.new.'] = phys_dict.get('pd_Wood').T.loc['Total New Houses']*100
wood_residential_df.plot( kind='line',marker='o', title= 'Wood in Residential')
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#non-residential
wood_nonresidential_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    wood_nonresidential_df[method_name] = Wood_dict.get(method_name).loc['Non-Residential']
wood_nonresidential_df['McKeever_non.resid.constr.'] = phys_dict.get('pd_Wood').T.loc['Nonres Total']*100
wood_nonresidential_df.plot(kind='line',marker='o', title= 'Wood in Non-Residential')
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#furniture
wood_furniture_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    wood_furniture_df[method_name] = Wood_dict.get(method_name).loc['Furniture']
wood_furniture_df['McKeever_furnit.'] = phys_dict.get('pd_Wood').T.loc['Furniture']*100
wood_furniture_df['Exio_HTwio'] = region_dict.get('US').get('wood').loc['Furniture; other manufactured goods n.e.c.']
wood_furniture_df.plot(kind='line',marker='o', title= 'Wood in Furniture' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#packaging
wood_packaging_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    wood_packaging_df[method_name] = Wood_dict.get(method_name).loc['Packaging']
wood_packaging_df['McKeever_packag.'] = phys_dict.get('pd_Wood').T.loc['Packaging and shippling']*100
wood_packaging_df['Exio_HTwio'] = region_dict.get('US').get('wood').loc['Food']
wood_packaging_df.plot(kind='line',marker='o', title= 'Wood in Packaging')
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

# # single-fam, multi-fam, manuf-houses, repair
# singleFam_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
# singleFam_df [HTWIO_] = Wood_dict.get(method_name).loc['Packaging']


year = 1992
# ALUMINUM
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
alu_construction_df['USGS_constr.'] = phys_dict.get('pd_Alu').T.loc['USGS Construction']*100
alu_construction_df['Liu_constr.'] = phys_dict.get('pd_Alu').T.loc['Liu Building & Construction']*100
alu_construction_df['Exio_HTwio'] = region_dict.get('US').get('alumin').loc['Construction']
alu_construction_df.plot(kind='line',marker='o', title= 'Aluminum in Construction' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#transportation
alu_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    alu_transport_df[method_name] = alu_dict.get(method_name).loc['Motor vehicles'] + alu_dict.get(method_name).loc['Other transport equipment']
alu_transport_df['USGS_transport.'] = phys_dict.get('pd_Alu').T.loc['USGS Transportation']*100
alu_transport_df['Liu_transport.'] = phys_dict.get('pd_Alu').T.loc['Liu Transportation']*100
alu_transport_df['Exio_HTwio'] = region_dict.get('US').get('alumin').loc['Motor vehicles, trailers and semi-trailers'] +\
    region_dict.get('US').get('alumin').loc['Other transport equipment']
alu_transport_df.plot(kind='line',marker='o', title= 'Aluminum in Transportation' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()


#packaging (assuming that also material in 'food products' is packaging)
alu_packaging_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    alu_packaging_df[method_name] = alu_dict.get(method_name).loc['Packaging'] + alu_dict.get(method_name).loc['Food products']
alu_packaging_df['USGS_cont.&packag.'] = phys_dict.get('pd_Alu').T.loc['USGS Containers and packaging']*100
alu_packaging_df['Liu_cont.&packag.'] = phys_dict.get('pd_Alu').T.loc['Liu  Containers and packaging']*100
alu_packaging_df['Exio_HTwio'] = region_dict.get('US').get('alumin').loc['Food']
alu_packaging_df.plot(kind='line',marker='o', title= 'Aluminum in Packaging' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()


#machinery
alu_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    alu_machinery_df[method_name] = alu_dict.get(method_name).loc['Electronic machinery'] + alu_dict.get(method_name).loc['Other machinery']
alu_machinery_df['USGS_mach.&equipm.+electrical'] = phys_dict.get('pd_Alu').T.loc['USGS Electrical']*100 +phys_dict.get('pd_Alu').T.loc['USGS Machinery and equipment']*100
alu_machinery_df['Liu_mach.&equipm.+electrical'] = phys_dict.get('pd_Alu').T.loc['Liu Electrical']*100 +phys_dict.get('pd_Alu').T.loc['Liu Machinery and equipment']*100
alu_machinery_df['Exio_HTwio'] = region_dict.get('US').get('alumin').loc['Machinery and equipment n.e.c. '] +\
    region_dict.get('US').get('alumin').loc['Electrical machinery and apparatus n.e.c.']
alu_machinery_df.plot(kind='line',marker='o', title= 'Aluminum in Machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#machinery electrical
alu_machineryElectric_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    alu_machineryElectric_df[method_name] = alu_dict.get(method_name).loc['Electronic machinery'] 
alu_machineryElectric_df['USGS_electrical'] = phys_dict.get('pd_Alu').T.loc['USGS Electrical']*100 
alu_machineryElectric_df['Liu_electrical'] = phys_dict.get('pd_Alu').T.loc['Liu Electrical']*100 
alu_machineryElectric_df.plot(kind='line',marker='o', title= 'Aluminum in Electronic machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()


#machinery other
alu_machineryOther_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    alu_machineryOther_df[method_name] = alu_dict.get(method_name).loc['Other machinery']
alu_machineryOther_df['USGS_mach.&equipm.'] = phys_dict.get('pd_Alu').T.loc['USGS Machinery and equipment']*100
alu_machineryOther_df['Liu_mach.&equipm.'] = phys_dict.get('pd_Alu').T.loc['Liu Machinery and equipment']*100
alu_machineryOther_df.plot(kind='line',marker='o', title= 'Aluminum in Other machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()


# STEEL
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
steel_construction_df['USGS_constr.'] = phys_dict.get('pd_IronSteel').T.loc['Construction USGS+Trade']*100
steel_construction_df['YSTAFB_constr'] = phys_dict.get('pd_IronSteel').T.loc['Construction YSTAFB']*100
steel_construction_df['Pauliuk_constr'] = phys_dict.get('pd_IronSteel').T.loc['Construction Pauliuk']*100
steel_construction_df['Exio_HTwio'] = region_dict.get('US').get('steel').loc['Construction']
steel_construction_df.plot(kind='line',marker='o', title= 'Steel in Construction' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#transportation
steel_transportation_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    steel_transportation_df[method_name] = steel_dict.get(method_name).loc['Motor vehicles'] + steel_dict.get(method_name).loc['Other transport equipment']
steel_transportation_df['USGS_transport.'] = phys_dict.get('pd_IronSteel').T.loc['Transportation USGS+Trade']*100
steel_transportation_df['Exio_HTwio'] = region_dict.get('US').get('steel').loc['Motor vehicles, trailers and semi-trailers'] +\
    region_dict.get('US').get('steel').loc['Other transport equipment']
steel_transportation_df['YSTAFB_transport.'] = phys_dict.get('pd_IronSteel').T.loc['Transport YSTAFB']*100
steel_transportation_df['Pauliuk_transport.'] = phys_dict.get('pd_IronSteel').T.loc['Automotive Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
    + phys_dict.get('pd_IronSteel').T.loc['Shipbuilding Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Aircraft Pauliuk']*100
steel_transportation_df.plot(kind='line',marker='o', title= 'Steel in Transportation' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#packaging (assuming that also material in 'food products' is packaging)
steel_packaging_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    steel_packaging_df[method_name] = steel_dict.get(method_name).loc['Packaging'] + steel_dict.get(method_name).loc['Food products']
steel_packaging_df['USGS_containers'] = phys_dict.get('pd_IronSteel').T.loc['Containers USGS+Trade']*100
steel_packaging_df['Exio_HTwio'] = region_dict.get('US').get('steel').loc['Food']
steel_packaging_df['Pauliuk_containers'] = phys_dict.get('pd_IronSteel').T.loc['Containers, shipping materials Pauliuk']*100
steel_packaging_df.plot(kind='line',marker='o', title= 'Steel in Packaging' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#machinery
steel_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    steel_machinery_df[method_name] = steel_dict.get(method_name).loc['Other machinery']
steel_machinery_df['YSTAFB_mach.&appl.)'] = phys_dict.get('pd_IronSteel').T.loc['Machinery & Appliances YSTAFB']*100
steel_machinery_df['Exio_HTwio'] = region_dict.get('US').get('steel').loc['Machinery and equipment n.e.c. '] +\
    region_dict.get('US').get('steel').loc['Electrical machinery and apparatus n.e.c.']
steel_machinery_df['Pauliuk_mach.'] = phys_dict.get('pd_IronSteel').T.loc['Machinery Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
        + phys_dict.get('pd_IronSteel').T.loc['Electrical Equipment Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Appliances Pauliuk']*100
steel_machinery_df.plot(kind='line',marker='o', title= 'Steel in Machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#remainder
steel_remainder_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    steel_remainder_df[method_name] = 100 - (steel_dict.get(method_name).loc['Other machinery'] + \
    steel_dict.get(method_name).loc['Packaging'] + steel_dict.get(method_name).loc['Food products']+\
    steel_dict.get(method_name).loc['Motor vehicles'] + steel_dict.get(method_name).loc['Other transport equipment'] +\
    steel_dict.get(method_name).loc['Residential'] + steel_dict.get(method_name).loc['Non-Residential'] + steel_dict.get(method_name).loc['Other buildings'] + steel_dict.get(method_name).loc['Infrastructure'] + steel_dict.get(method_name).loc['Other construction'])
steel_remainder_df['Shipment_USGS'] = phys_dict.get('pd_IronSteel').T.loc['Service centers and distributors USGS+Trade']*100 +\
    phys_dict.get('pd_IronSteel').T.loc['Other USGS+Trade']*100 + phys_dict.get('pd_IronSteel').T.loc['Undistributed USGS+Trade']*100
steel_remainder_df['Shipment_YSTAFB(M&A)'] = phys_dict.get('pd_IronSteel').T.loc['Other products YSTAFB']*100
steel_remainder_df['Shipment_Pauliuk'] = 100 - (phys_dict.get('pd_IronSteel').T.loc['Containers, shipping materials Pauliuk']*100 +\
    phys_dict.get('pd_IronSteel').T.loc['Automotive Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
        + phys_dict.get('pd_IronSteel').T.loc['Shipbuilding Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Aircraft Pauliuk']*100 +\
          phys_dict.get('pd_IronSteel').T.loc['Construction Pauliuk']*100 +  phys_dict.get('pd_IronSteel').T.loc['Machinery Pauliuk']*100 + phys_dict.get('pd_IronSteel').T.loc['Rail Transportation Pauliuk']*100\
                  + phys_dict.get('pd_IronSteel').T.loc['Electrical Equipment Pauliuk']*100 +  + phys_dict.get('pd_IronSteel').T.loc['Appliances Pauliuk']*100)
steel_remainder_df.plot(kind='line',marker='o', title= 'Steel in Other' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()



# COPPER (some problems assembling the material dict so took the easy way)
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
copper_construction_df['Shipment'] = phys_dict.get('pd_Copper').T.loc['Building construction USGS+Trade']*100
copper_construction_df['Shipment_CDA'] = phys_dict.get('pd_Copper').T.loc['Building construction CDA+Trade']*100
copper_construction_df['Exio_HTwio'] = region_dict.get('US').get('Copper').loc['Construction']
copper_construction_df.plot(kind='line',marker='o', title= 'Copper in Construction' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#transportation
copper_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    copper_transport_df[method_name] = copper_dict.get(method_name).loc['Motor vehicles'] + copper_dict.get(method_name).loc['Other transport equipment']
copper_transport_df['Shipment'] = phys_dict.get('pd_Copper').T.loc['Transportation equipment USGS+Trade']*100
copper_transport_df['Shipment_CDA'] = phys_dict.get('pd_Copper').T.loc['Transportation equipment CDA+Trade']*100
copper_transport_df['Exio_HTwio'] = region_dict.get('US').get('Copper').loc['Motor vehicles, trailers and semi-trailers'] +\
    region_dict.get('US').get('Copper').loc['Other transport equipment']
copper_transport_df.plot(kind='line',marker='o', title= 'Copper in Transportation' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#machinery
copper_machinery_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    copper_machinery_df[method_name] = copper_dict.get(method_name).loc['Electronic machinery'] + copper_dict.get(method_name).loc['Other machinery']
copper_machinery_df['Shipment_USGS'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products USGS+Trade']*100 +phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment USGS+Trade']*100
copper_machinery_df['Shipment_CDA'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products CDA+Trade']*100 +phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment CDA+Trade']*100
copper_machinery_df['Exio_HTwio'] = region_dict.get('US').get('Copper').loc['Machinery and equipment n.e.c. '] +\
    region_dict.get('US').get('Copper').loc['Electrical machinery and apparatus n.e.c.']
copper_machinery_df.plot(kind='line',marker='o', title= 'Copper in Machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#machinery electrical
copper_machineryElectric_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    copper_machineryElectric_df[method_name] = copper_dict.get(method_name).loc['Electronic machinery'] 
copper_machineryElectric_df['Shipment_USGS'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products USGS+Trade']*100
copper_machineryElectric_df['Shipment_CDA'] = phys_dict.get('pd_Copper').T.loc['Electrical and electronic products CDA+Trade']*100
copper_machineryElectric_df.plot(kind='line',marker='o', title= 'Copper in Electronic machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#machinery other
copper_machineryOther_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    copper_machineryOther_df[method_name] = copper_dict.get(method_name).loc['Other machinery']
copper_machineryOther_df['Shipment_USGS'] = phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment USGS+Trade']*100
copper_machineryOther_df['Shipment_CDA'] = phys_dict.get('pd_Copper').T.loc['Industrial machinery and equipment CDA+Trade']*100
copper_machineryOther_df.plot(kind='line',marker='o', title= 'Copper in Other machinery' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()



# CEMENT
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

cement_residential_df = pd.DataFrame([], index=list(range(1963,2017)), columns=method_names)
for method_name in method_names:
    cement_residential_df[method_name] = cement_dict.get(method_name).loc['Residential']
cement_residential_df['PCA_resid.buildings'] = phys_dict.get('pd_Cement').T.loc['Residential PCA']*100
cement_residential_df['Cao_resid.building'] = phys_dict.get('pd_Cement').T.loc['Residential Cao']*100
cement_residential_df['PCA Kapur__resid.buildings'] = phys_dict.get('pd_Cement').T.loc['Residential buildings PCA Kapur & web']*100
cement_residential_df.plot(kind='line',marker='o', title= 'Cement in Residential STRUCTURES' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

cement_nonRes_df = pd.DataFrame([], index=list(range(1963,2017)), columns=method_names)
for method_name in method_names:
    cement_nonRes_df[method_name] = cement_dict.get(method_name).loc['Non-Residential']
cement_nonRes_df['PCA_nonres.buildings'] = phys_dict.get('pd_Cement').T.loc['Nonresidential buildings PCA']*100
cement_nonRes_df['Cao_nonres.building'] = phys_dict.get('pd_Cement').T.loc['Non-Residential Cao']*100
cement_nonRes_df['PCAKapur_comm.publ.build+farmConstr'] = phys_dict.get('pd_Cement').T.loc['Commercial buildings PCA Kapur & web']*100 + \
    phys_dict.get('pd_Cement').T.loc['Public Buildings PCA Kapur & web']*100 + phys_dict.get('pd_Cement').T.loc['Farm construction PCA Kapur & web']*100
cement_nonRes_df.plot(kind='line',marker='o', title= 'Cement in Non-residential STRUCTURES' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

cement_CE_df = pd.DataFrame([], index=list(range(1963,2017)), columns=method_names)
for method_name in method_names:
    cement_CE_df[method_name] = cement_dict.get(method_name).loc['Infrastructure'] + cement_dict.get(method_name).loc['Other construction']
cement_CE_df['PCA_civ.eng+streets'] = phys_dict.get('pd_Cement').T.loc['Civil engineering/Infra']*100 + phys_dict.get('pd_Cement').T.loc['Highways & Streets']*100
cement_CE_df['Cao_civ.eng'] = phys_dict.get('pd_Cement').T.loc['Civil Engineering Cao']*100
cement_CE_df['PCAKapur_util.+streets+other'] = phys_dict.get('pd_Cement').T.loc['Utilities PCA Kapur & web']*100 + \
    phys_dict.get('pd_Cement').T.loc['Streets and Highways PCA Kapur & web']*100 + phys_dict.get('pd_Cement').T.loc['Others PCA Kapur & web']*100\
        + phys_dict.get('pd_Cement').T.loc['Water and waste management PCA Kapur & web']*100
cement_CE_df.plot(kind='line',marker='o', title= 'Cement in Civil Engineering' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()

#make one for highways & streets

# PLASTIC
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
plastic_construction_df['Euromap_constr'] = phys_dict.get('pd_Plastics').T.loc['Construction industry Euromap USA']*100
plastic_construction_df['PlasticsEurope_EU_constr'] = phys_dict.get('pd_Plastics').T.loc['Building and construction PE']*100
plastic_construction_df['Exio_HTwio'] = region_dict.get('US').get('Plastic').loc['Construction']
plastic_construction_df.plot(kind='line',marker='o', title= 'Plastics in Construction' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()



#packaging (assuming that also material in 'food products' is packaging)
plastic_packaging_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    plastic_packaging_df[method_name] = plastic_dict.get(method_name).loc['Packaging'] + plastic_dict.get(method_name).loc['Food products'] 
plastic_packaging_df['Euromap_packag.'] = phys_dict.get('pd_Plastics').T.loc['Packaging Euromap USA']*100
plastic_packaging_df['PlasticsEurope_EU_packag.'] = phys_dict.get('pd_Plastics').T.loc['Packaging PE']*100
plastic_packaging_df['Exio_HTwio'] = region_dict.get('US').get('Plastic').loc['Food']
plastic_packaging_df.plot(kind='line',marker='o', title= 'Plastics in Packaging/Food' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()



#transport (assuming that also material in 'food products' is transport)
plastic_transport_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    plastic_transport_df[method_name] = plastic_dict.get(method_name).loc['Motor vehicles'] + plastic_dict.get(method_name).loc['Other transport equipment'] 
plastic_transport_df['Euromap_automotive'] = phys_dict.get('pd_Plastics').T.loc['Automotive Euromap USA']*100
plastic_transport_df['PlasticsEurope_EU_autom.'] = phys_dict.get('pd_Plastics').T.loc['Automotive PE']*100
plastic_transport_df['Exio_HTwio'] = region_dict.get('US').get('Plastic').loc['Motor vehicles, trailers and semi-trailers'] +\
    region_dict.get('US').get('Plastic').loc['Other transport equipment']
plastic_transport_df.plot(kind='line',marker='o', title= 'Plastics in Transport/Automotive' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()


#electronics (assuming that also material in 'food products' is transport)
plastic_elect_df = pd.DataFrame([], index=list(range(1963,2013)), columns=method_names)
for method_name in method_names:
    plastic_elect_df[method_name] = plastic_dict.get(method_name).loc['Electronic machinery']  
plastic_elect_df['Euromap_electr.'] = phys_dict.get('pd_Plastics').T.loc['Electrical, electronics & telecom Euromap USA']*100
plastic_elect_df['PlasticsEurope_EU_electr.'] = phys_dict.get('pd_Plastics').T.loc['Electrical&Electronic PE']*100
plastic_elect_df.plot(kind='line',marker='o', title= 'Plastics in Electronics' )
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.xticks(years)
plt.ylabel('%')
plt.show()





'''
 #plot above U.S dataframes into multi-plot
 
 '''
plastic_packaging_df
plastic_transport_df
plastic_construction_df
plastic_elect_df

alu_transport_df
alu_construction_df
alu_packaging_df
alu_machinery_df

alu_machineryElectric_df
alu_machineryOther_df

cement_residential_df
cement_nonRes_df
cement_CE_df 

copper_construction_df
copper_transport_df
copper_machinery_df
copper_machineryElectric_df 
copper_machineryOther_df

steel_construction_df
steel_transportation_df
steel_packaging_df
steel_machinery_df
steel_remainder_df

wood_construction_df
wood_residential_df
wood_nonresidential_df
wood_furniture_df
wood_packaging_df




color_dict = {'CBA':pal[0], 'WIO': pal[1], 'Ghosh':pal[2],  \
              'ParGhosh': pal[3], 'HT-WIO': pal[5], 'Exio_HTwio': pal[4]}

marker_dict = {'HT-WIO': 'v'}



pal = sns.color_palette("colorblind") 
fig, axs = plt.subplots(7,3 ,sharex=False, sharey=False, figsize=(14,22))


axs[6,2].axis('off')

wood_construction_df.plot( ax=axs[0,0], color = [color_dict.get(r, pal[7]) for r in wood_construction_df], style = [marker_dict.get(r, '*') for r in wood_construction_df], kind='line', title= 'Wood in Construction', legend = False)
wood_furniture_df.plot(ax=axs[0,1],color = [color_dict.get(r, pal[7]) for r in wood_furniture_df], kind='line',marker='o',title= 'Wood in Furniture', legend = False)
wood_packaging_df.plot(ax=axs[0,2],color = [color_dict.get(r, pal[7]) for r in wood_packaging_df], kind='line',marker='o', title= 'Wood in Packaging', legend = False)
steel_construction_df.plot(ax=axs[1,0],color = [color_dict.get(r, pal[7]) for r in steel_construction_df], kind='line',marker='o', title= 'Steel in Construction', legend = False)
steel_transportation_df.plot(ax=axs[1,1],color = [color_dict.get(r, pal[7]) for r in steel_transportation_df], kind='line',marker='o', title= 'Steel in Transport', legend = False)
steel_machinery_df.plot(ax=axs[1,2],color = [color_dict.get(r, pal[7]) for r in steel_machinery_df], kind='line',marker='o', title= 'Steel in Machinery', legend = False)
steel_packaging_df.plot(ax=axs[2,0], color = [color_dict.get(r, pal[7]) for r in steel_packaging_df], kind='line',marker='o', title= 'Steel in Packaging', legend = False)
alu_construction_df.plot(ax=axs[2,1], color = [color_dict.get(r, pal[7]) for r in alu_construction_df], kind='line',marker='o', title= 'Alu in Construction', legend = False)
alu_transport_df.plot(ax=axs[2,2], color = [color_dict.get(r, pal[7]) for r in alu_transport_df],kind='line',marker='o', title= 'Alu in Transport', legend = False)
alu_machinery_df.plot(ax=axs[3,0], color = [color_dict.get(r, pal[7]) for r in alu_machinery_df],kind='line',marker='o', title= 'Alu in Machinery', legend = False)
alu_packaging_df.plot(ax=axs[3,1], color = [color_dict.get(r, pal[7]) for r in alu_packaging_df],kind='line',marker='o', title= 'Alu in Packaging', legend = False)
copper_construction_df.plot(ax=axs[3,2], color = [color_dict.get(r, pal[7]) for r in copper_construction_df],kind='line',marker='o', title= 'Copper in Construction', legend = False)
copper_transport_df.plot(ax=axs[4,0], color = [color_dict.get(r, pal[7]) for r in copper_transport_df],kind='line',marker='o', title= 'Copper in Transport', legend = False)
copper_machinery_df.plot(ax=axs[4,1], color = [color_dict.get(r, pal[7]) for r in copper_machinery_df],kind='line',marker='o', title= 'Copper in Machinery', legend = False)
plastic_construction_df.plot(ax=axs[4,2], color = [color_dict.get(r, pal[7]) for r in plastic_construction_df],kind='line',marker='o', title= 'Plastic in Construction', legend = False)
plastic_transport_df.plot(ax=axs[5,0], color = [color_dict.get(r, pal[7]) for r in plastic_transport_df],kind='line',marker='o', title= 'Plastic in Packaging', legend = False)
plastic_packaging_df.plot(ax=axs[5,1], color = [color_dict.get(r, pal[7]) for r in plastic_packaging_df],kind='line',marker='o', title= 'Plastic in Transport', legend = False)
plastic_elect_df.plot(ax=axs[5,2], color = [color_dict.get(r, pal[7]) for r in plastic_elect_df],kind='line',marker='o', title= 'Plastic in Electrical', legend = False)


#-->need to give different names to dataframes
axs[0,1].annotate(label='lala',xy=(1990, 0.5),text='lala') #write text in plot

lgd = axs[6,2].legend(loc='center left', bbox_to_anchor=(0.01, 0.5),fontsize=12)

def add_line(legend):
    ax1 = legend.axes
    from matplotlib.lines import Line2D

    import matplotlib.patches as mpatches
    handles, labels = axs[0,0].get_legend_handles_labels()
    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)
    legend.set_title(legend.get_title().get_text())
    
           
add_line(lgd)
fig.tight_layout()


    import matplotlib.patches as mpatches
    handles, labels = axs[2,2].get_legend_handles_labels()
    
    handles.append(mpatches.Patch(color=pal[0], label='Final Waste'))
    labels.append('EoL, final waste')
    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)
    legend.set_title(legend.get_title().get_text())
       
    handles.append(mpatches.Patch(color=pal[1], label='EoL Export'))
    labels.append('EoL, export')
    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)
    legend.set_title(legend.get_title().get_text())
    
    handles.append(mpatches.Patch(color=pal[2], label='Domestic EoL Recycling'))
    labels.append('EoL, domestic recycling')
    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)
    legend.set_title(legend.get_title().get_text())
    
    handles.append(mpatches.Patch(color=pal[3], label='EoL Downcycling'))
    labels.append('EoL, domestic downcycling')
    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)
    legend.set_title(legend.get_title().get_text())



cement_residential_df
cement_nonRes_df
cement_CE_df 

wood_residential_df.plot(ax=axs[0,1], kind='line',marker='o', title= 'Wood in Residential', legend = False)
wood_nonresidential_df.plot(ax=axs[0,2], kind='line',marker='o', title= 'Wood in Non-residential', legend = False)

'''
 #try detailed plots for US selected materrials
 '''
 
 # detail
 Wood_detail_dict = {}
 Wood_detail_df = pd.DataFrame([], index=HTWio_detail_dict.get(year).index.get_level_values(1), columns=years)
 for year in years:
     wood_detail_single = HTWio_detail_dict.get(year).iloc[:,HTWio_detail_dict.get(year).columns.get_level_values(1).map(lambda t: ('Sawmill' or 'Wood') in t).to_list()]
     Wood_detail_df[year] = wood_detail_single.values
 Wood_detail_dict['HT-WIO_detail'] = Wood_df
 #every sheet has different number of sectors --> cannot really assemble that in one frame
 #-- am besten wohl durch Aggregation Matrices
 # für welche end-uses? Construction, Transportation
 # Stahl - 2004 sehr detailliert (vergleihcen mit 2002/007) --> excel
 # plastic - automotive 2006-2015 - IO 2007/2012 -_> excel
 # wood - construction, furniture 1950-2006 --> iloc constr & furniture in allen & ausschneiden, FURNITURE HABEN WUR
 #cement - construction
 constr_1963 = HTWio_detail_dict.get(1963).iloc[19:26,:]
 constr_1967 = HTWio_detail_dict.get(1967).iloc[26:76,:]
 constr_1972 = HTWio_detail_dict.get(1972).iloc[26:76,:]
 constr_1977 = HTWio_detail_dict.get(1977).iloc[30:83,:]
 constr_1982 = HTWio_detail_dict.get(1982).iloc[30:83,:]
 constr_1987 = HTWio_detail_dict.get(1987).iloc[30:83,:]
 constr_1992 = HTWio_detail_dict.get(1992).iloc[30:45,:] #checl if to add to this and the above minign stuff
 constr_1997 = HTWio_detail_dict.get(1997).iloc[26:45,:]
 constr_2002 = HTWio_detail_dict.get(2002).iloc[27:40,:]
 constr_2007 = HTWio_detail_dict.get(2007).iloc[19:36,:] 
 constr_2012 = HTWio_detail_dict.get(2012).iloc[19:36,:] 

 # save to Excel, including used filter matrices
 writer = pd.ExcelWriter(data_path_usa + '/Construction_detail' + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
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


 constr_detail = np.zeros((500,500))
 constr_detail[:,0] = constr_1963.iloc[:,0].values
 count_constr_detail = 0
 for year in years:
     constr_detail[:,count_constr_detail] = constr_ +year
     
 #all of these might still not include some sector assigned to total construciton
 constr_1963.iloc[:,0].values.plot(x=years, kind='line',marker='o', title= 'Wood in Construction', linewidth =0 )
 constr_1967.iloc[:,0].T.plot(kind='line',marker='o', title= 'Wood in Construction', linewidth =0 )

 fig, ((ax1, ax3), (ax5, ax7)) = plt.subplots(nrows=2, ncols=2, sharex=False, sharey=False, figsize=(12,8))
 ax1 = constr_1963
 fig.tight_layout(h_pad=2.5)
 plt.show()

 x = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007]
 y = list(range(0,100,10))
 plt.scatter(x, constr_1963.iloc[:,0].values)
 for i, txt in enumerate(n):
     plt.annotate(txt, (z[i], y[i]))

 for i, txt in enumerate(n):
     ax.annotate(txt, (x[i], y[i]))
     
     import numpy as np
 from matplotlib import griddata

 x = np.array([0,0,1,1])
 y = np.array([0,1,0,1])
 z = np.array([0,10,20,30])
 xi = np.arange(x.min(),x.max()+1)
 yi = np.arange(y.min(),y.max()+1)
 ar = griddata(x,y,z,xi,yi)

 # ar is now
 # array([[  0.,  20.],
 #        [ 10.,  30.]])

     
     
 fig, axs = plt.subplots(3,2 ,sharex=False, sharey=False, figsize=(12,10))
 
 
 
 
 



'''
    #4 Assemble comparison of Exiobase countries and sectors (selected method)
    --> add global end-use data!!
'''

load_path = 'C:/Users/jstreeck/Desktop/EndUse_shortTermSave/SectorSplit_WasteFilter_physical/Global'

#Intern = many countries, global = resl. for whole globe, country_name = data only for that country
physSplit_cement_Intern = pd.read_excel(load_path + '/2017_Cao_Cement_Split data.xlsx', sheet_name='Data_manip') #not applicable for Exiobase (only if using GLORIA)
physSplit_plastics_Intern  = pd.read_excel(load_path + '/EUROMAP.xlsx', sheet_name='clean data manip')
physSplit_plastics_China  = pd.read_excel(load_path + '/Plastics_ChinaEU28.xlsx', sheet_name='China').set_index('Year')*100
physSplit_plastics_EU28  = pd.read_excel(load_path + '/Plastics_ChinaEU28.xlsx', sheet_name='EU28').set_index('Year')*100

physSplit_steel_China = pd.read_excel(load_path + '/IronSteel.xlsx', sheet_name='China').set_index('Year')*100
physSplit_steel_India = pd.read_excel(load_path + '/IronSteel.xlsx', sheet_name='India').set_index('Year')*100
physSplit_steel_UK = pd.read_excel(load_path + '/IronSteel.xlsx', sheet_name='UK').set_index('Year')*100
physSplit_copper_EU28 = pd.read_excel(load_path + '/Copper.xlsx', sheet_name='EU').set_index('Year')*100
EU28 = ['GB', 'FR','IT','DE', 'PT', 'RU'] #might require expansion

physSplit_alu_intern = data from Liu




#Plot SELECTED COUNTRIES and MATERIALS, ALL END USES
plotRegions = ['CN', 'IN','GB']#['US', 'JP', 'GB', 'FR','IT','DE', 'PT', 'RU', 'IN','CN', 'ID', 'ZA']
region_transl = {'PT':'Portugal', 'US':'USA', 'GB':'Great Britain', 'FR':'France','IT':'Italy','DE':'Germany','IN':'India','CN':'China','RU':'Russia','ZA':'South Africa' }
plotMaterials = [ 'Plastic', 'steel', 'Copper']
#plotMaterials = ['steel', 'wood', 'Plastic', 'glass', 'alumin', 'tin', 'Copper']

for plotMaterial in plotMaterials:
    for plotRegion in plotRegions:
        region_dict.get(plotRegion).get(plotMaterial).T.plot(kind='line',marker='o', title= (plotRegion + ' ' +plotMaterial) )
        plt.legend(bbox_to_anchor=(1,1), loc="upper left")
        plt.show()



##--> include the physical split data into plots:
    ##--> info for ALU from LIU 2013 missing 

for plotMaterial in plotMaterials:
    for plotRegion in plotRegions:
        randomlist = []
        plot_frame = region_dict.get(plotRegion).get(plotMaterial).T
        if plotMaterial == 'Plastic':
            try:
                plot_frame['Packaging_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Packaging']
                plot_frame['Automotive_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Automotive']
                plot_frame['Electrical_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Construction industry']
                plot_frame['Construction_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Electrical, electronics & telecom']
                plot_frame['Other_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Others']
            except:
                continue
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
                plot_frame['Wang_Machinery'] = physSplit_steel_China['RFSM']
                plot_frame['Wang_Appliances'] = physSplit_steel_China['RFSA']
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
        style=['+-', 'o-', '.--', 's:']
        for i in range(0,plot_frame.shape[1]):
            n = random.randint(0,3)
            randomlist.append(n)
        c = [style[i] for i in randomlist]
        plot_frame.plot(kind='line',style=c, title= (plotRegion + ' ' +plotMaterial) )
        plt.legend(bbox_to_anchor=(1,1), loc="upper left")
        plt.show()

style=['+-', 'o-', '.--', 's:']
marker = range(plot_frame.shape[1]
import random
randomlist = []
for i in range(0,plot_frame.shape[1]):
    n = random.randint(0,3)
    randomlist.append(n)
style[randomlist]
c = [style[i] for i in randomlist]
#Plot VIOLIN PLOTS for ONE MATERIAL, ONE END-USE, ALL COUNTRIES
#COPPER

end_use_all =  pd.DataFrame([])# index=years_exio, columns=regions)
for region in regions:
    end_use_region = pd.DataFrame(region_dict.get(region).get('Copper').loc['Construction']).rename(columns = {'Construction':region})
    end_use_all[region] = end_use_region
#end_use_all.T.plot( kind='box', title= 'Copper to Construction')
ax = sns.boxplot(data=end_use_all.T,whis=[0, 100], width=.6, palette="vlag")
ax = sns.swarmplot(data=end_use_all.T)
ax.set_xticklabels(years_exio,fontsize = 7.5)
ax.set( ylabel = "%", title = 'Copper to Construction')


#'Construction', 'Machinery and equipment n.e.c. ','Office machinery and computers (30)',
# 'Electrical machinery and apparatus n.e.c. (31)','Radio, television and communication equipment and apparatus (32)',
# 'Medical, precision and optical instruments, watches and clocks (33)','Motor vehicles, trailers and semi-trailers (34)',
# 'Other transport equipment (35)','Furniture; other manufactured goods n.e.c. (36)', 'Textiles (17)',
# 'Printed matter and recorded media (22)', 'Food', 'Other raw materials','Secondary materials', 
# 'Energy carriers', 'Energy carriers.1', 'Other','Products nec', 'Services']#

end_uses = ['Construction', 'Machinery and equipment n.e.c. ', 'Electrical machinery and apparatus n.e.c. (31)', \
          'Motor vehicles, trailers and semi-trailers (34)', 'Other transport equipment (35)', 'Furniture; other manufactured goods n.e.c. (36)' ]

for material in materials:
    end_use_all =  pd.DataFrame([])
    for end_use in end_uses:
        for region in regions:
            end_use_region = pd.DataFrame(region_dict.get(region).get(material).loc[end_use ])#.rename(columns = {'Construction':region})
            end_use_all[region] = end_use_region
        ax = sns.boxplot(data=end_use_all.T,whis=[0, 100], width=.6, palette="vlag", fliersize =0)
        ax = sns.swarmplot(data=end_use_all.T)
        ax.set_xticklabels(years_exio,fontsize = 7.5)
        #ax.set_ylim(0,100)
        ax.set(ylabel = "%", title = (material + ' ' + end_use))
        plt.show()
#end_use_all.T.plot( kind='box', title= 'Copper to Construction')



#plt.annotate('BLABLA', (1995,90))
#plt.annotate()
#ax.text(1995, 80, 'lala')


for i, j in enumerate(end_use_all['% of Squad pass']):
    plt.annotate(df['Player'][i],
                xy=(df['% of Squad pass'][i],0),
                xytext=(df['% of Squad pass'][i], random.uniform(0.2,0.4)),
                arrowprops=dict(arrowstyle="->"))

end_use_all.T.max()
ax.plot.show()

#STEEL
end_use_all =  pd.DataFrame([], index=years_exio, columns=regions)
for region in regions:
    end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Construction'])
    end_use_all[region] =end_use_region.values
end_use_all.T.plot( kind='box', title= 'Steel to Construction')
sns.violinplot(data=end_use_all.T)









#region_dict.get('US').get('steel').T.plot(kind='line',marker='o', title= material)
#plt.legend(bbox_to_anchor=(1,1), loc="upper left")
#plt.show()



end_use_all =  pd.DataFrame([], index=years_exio, columns=regions)
for region in regions:
    end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Construction'])
    end_use_all[region] =end_use_region.values
end_use_all.plot( kind='line',marker='o', title= material, linewidth=0, legend=False)
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.show()
end_use_all.T.plot( kind='box', title= 'Steel to Construction')

end_use_all =  pd.DataFrame([], index=years, columns=regions)
for region in regions:
    end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Motor vehicles, trailers and semi-trailers (34)'])
    end_use_all[region] =end_use_region.values
end_use_all.plot( kind='line',marker='o', title= material, linewidth=0, legend=False)
end_use_all.T.plot( kind='box', title= 'Steel to Motor vehicles and trailers')

end_use_all =  pd.DataFrame([], index=years, columns=regions)
for region in regions:
    end_use_region = pd.DataFrame(region_dict.get(region).get('steel').loc['Machinery and equipment n.e.c. '])
    end_use_all[region] =end_use_region.values
end_use_all.plot( kind='box',marker='o', title= material, linewidth=0, legend=False)
end_use_all.T.plot( kind='box', title= material)



#copper
end_use_all =  pd.DataFrame([], index=years_exio, columns=regions)
for region in regions:
    end_use_region = pd.DataFrame(region_dict.get(region).get('Plastic').loc['Construction'])
    end_use_all[region] =end_use_region.values
end_use_all.T.plot( kind='box', title= 'Copper to Construction')
sns.violinplot(data=end_use_all.T)

.T.plot(kind='line',marker='o', title= material)
#for material in materials:
#    material_single = []
#    material_df = pd.DataFrame([], index=Exio_dict.get(year).index.get_level_values(1), columns=years)
#    for year in years:
#        material_single = Exio_dict.get(year).iloc[:,Exio_dict.get(year).columns.get_level_values(0).map(lambda t: (material) in t).to_list()]
#      material_df[year] = material_single.values
#    material_dict[(material)] = material_df
    
    

