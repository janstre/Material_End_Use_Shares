# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 14:51:52 2020

@author: jstreeck
"""

import os
import sys
import numpy as np
import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt

#define working directory and data paths
main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
path_input_data =  os.path.join(main_path, 'input_data/') 
data_path_usa = os.path.join(main_path, 'output/USA/')
data_path_exio = os.path.join(main_path, 'output/Exiobase/')

from EndUseShares_GraphsStatistics_functions_v1 import save_list2Excel, save_dict2Excel, calc_relDeviation, assemble_materialEndUse_df


'''
    #1 Assemble end-use share dataframes for USA (national tables and EXIOBASE) and save if required
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


#SAVE method dictionaries to Excel (and calculate sum of all end-use shares to check if 100%)
##sum doesn't make sense for industry shipments
# methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, phys_dict] 
# method_names = ['CBA', 'WIO-MFA', 'Ghosh-IO AMC', 'Partial Ghosh-IO', 'EUT-WIO', 'Industry_Shipments' ]
# k=0
# for k in range(0,len(methods)):
#     for e,f in methods[k].items():
#         f.loc['sum'] = f.sum(axis=0)
#     path = './output/USA/FiguresStats/' + method_names[k] + '_fullResults_USA'  
#     save_dict2Excel(path, methods[k] )
#     k = k+1



'''
    #2 Assemble material end-use dataframes for comparison of USA national MIOTs + EXIOBASE MIOTs + industry shipments
'''

years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]

methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict] 
method_names = ['CBA', 'WIO-MFA', 'Ghosh-IO AMC', 'Partial Ghosh-IO', 'EUT-WIO' ]

#optionally with ExtAgg and WIO_filter diff (choose this instead of two lines above if assembling FIGURE 2 SENSITIVITY; only works for this single plot!)
# methods = [ Wio_dict, Wio_ext_dict , Wio_withServiceInput_dict,  EUTWio_dict, EUTWio_ext_dict] 
# method_names = [ 'WIO-MFA', 'WIO-MFA_extAgg','WIO-MFA_filtDif', 'EUT-WIO', 'EUT-WIO_extAgg' ]


# re-assemble data to dataframes per material and end-use
plastic_packaging_food_df, plastic_transport_df, plastic_construction_df, plastic_electrical_df, plastic_furniture_df, alu_transport_df, \
    alu_construction_df, alu_packaging_food_df, alu_machinery_df, alu_machineryElectric_df, alu_machineryOther_df, alu_furniture_df, copper_construction_df, copper_transport_df,\
    copper_machinery_df, copper_furniture_df, steel_construction_df, steel_transport_df, steel_packaging_food_df, steel_machinery_df, steel_remainder_df,\
    steel_furniture_df, wood_construction_df, wood_residential_df, wood_nonresidential_df, wood_furniture_df, wood_packaging_food_df, wood_transport_df, wood_machinery_df,\
    cement_residential_df, cement_nonresidential_df, cement_civil_engineering_df  = assemble_materialEndUse_df(methods, method_names, years, CBA_dict, phys_dict, region_dict)


#####
    

#assemble material dictionary time series - #! move to FUNCTIONS
year = 1963

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

bricks_dict = {}
count = -1
for method in methods:
    bricks_single = []
    bricks_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
    count= count +1
    for year in years:
        bricks_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Brick' in t or 'Clay product' in t).to_list()]
        bricks_df[year] = bricks_single.values
    bricks_dict[(method_names[count])] = bricks_df

years =  [1963, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002]
#only do for these years as for 2007/12 all glass is aggregated
flat_dict = {}
count = -1
for method in methods:
    flat_single = []
    flat_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
    count= count +1
    for year in years:
        flat_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Flat glass' in t or 'glass products' in t).to_list()]
        flat_df[year] = flat_single.values
    flat_dict[(method_names[count])] = flat_df
     


years =  [1963, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007, 2012]
paper_dict = {}
count = -1
for method in methods:
    paper_single = []
    paper_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
    count= count +1
    for year in years:
        paper_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Pulp' in t or 'Paper' in t).to_list()]
        paper_df[year] = paper_single.values
    paper_dict[(method_names[count])] = paper_df

years =  [1963, 1967, 1972, 1977, 1982]
lead_dict = {}
count = -1
for method in methods:
    lead_single = []
    lead_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
    count= count +1
    for year in years:
        lead_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'Lead' in t or 'lead' in t).to_list()]
        lead_df[year] = lead_single.values
    lead_dict[(method_names[count])] = lead_df


years =  [1963, 1967, 1972, 1977, 1982]
zinc_dict = {}
count = -1
for method in methods:
    zinc_single = []
    zinc_df = pd.DataFrame([], index=CBA_dict.get(year).index.get_level_values(1), columns=years)
    count= count +1
    for year in years:
        zinc_single = method.get(year).iloc[:,method.get(year).columns.get_level_values(1).map(lambda t: 'zinc' in t or 'zinc' in t).to_list()]
        zinc_df[year] = zinc_single.values
    zinc_dict[(method_names[count])] = zinc_df

years =  [1963, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007, 2012]

# #SAVE method dictionaries to Excel (and calculate sum of all end-use shares to check if 100%)
# path = './output/USA/USA_time_series_per_material' 
# mat_names = ['zinc_dict', 'lead_dict', 'paper_dict', 'flat_dict', 'bricks_dict', \
#              'Wood_dict', 'alu_dict', 'copper_dict', 'steel_dict','cement_dict', 'plastic_dict']
# mat_items = [eval(e) for e in mat_names]
# list2dict = dict(zip(mat_names, mat_items))
# writer = pd.ExcelWriter(path + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
# for df_name, df in  list2dict.items():
#     df.get('EUT-WIO').to_excel(writer, sheet_name=df_name)
# writer.save()


# figure_4_plotNames = ['china_steel', 'india_steel', 'britain_steel', 'china_alumin', 'india_alumin', 'britain_alumin', 'china_Plastic',\
#                  'india_Plastic', 'britain_Plastic', 'end_use_all_aluConst', 'end_use_all_steelConst', 'end_use_all_steelMotor']
# figure_4_plots = [eval(e) for e in figure_4_plotNames]
'''

    FIGURE2: low end-use resolution

'''
dummy_df = plastic_electrical_df.copy()
dummy_df[:] = 0

pal = sns.color_palette("colorblind") 

color_dict = {'CBA':pal[0], 'WIO-MFA': pal[1], 'Ghosh-IO AMC':pal[2],  \
              'Partial Ghosh-IO': pal[3], 'EUT-WIO': 'maroon', 'Exio_EUT-WIO': pal[4],\
            'Shipment_1':pal[7], 'Shipment_2':pal[0],'Shipment_3':pal[3]}

marker_dict = {'CBA':'o', 'WIO-MFA': 'o', 'Ghosh-IO AMC':'o',  \
              'Partial Ghosh-IO': 'o', 'EUT-WIO': 'v', 'Exio_EUT-WIO': '.'}

name_list1 = ['(a) wood_construction_df','(b) wood_transport_df','(c) wood_packaging_food_df', '(d) wood_machinery_df', '(e) wood_furniture_df',\
              '(f) steel_construction_df', '(g) steel_transport_df',  '(h) steel_packaging_food_df', '(i) steel_machinery_df',  '(j) steel_furniture_df',\
              '(k) copper_construction_df', '(l) copper_transport_df',  '(x) dummy_df', '(m) copper_machinery_df', '(n) copper_furniture_df',\
              '(o) alu_construction_df', '(p) alu_transport_df', '(q) alu_packaging_food_df', '(r) alu_machinery_df', '(s) alu_furniture_df', \
              '(t) plastic_construction_df', '(u) plastic_transport_df',  '(v) plastic_packaging_food_df', '(w) plastic_electrical_df', '(x) plastic_furniture_df']

plot_list1 = [eval(e[4:]) for e in name_list1]

k,i,j = 0,0,0     
fig, axs = plt.subplots(5,5 ,sharex=False, sharey=False, figsize=(33,20))

for i in range(0,5):
    for j in range (0,5):
        plot_list1[k].plot(ax=axs[i,j], color = [color_dict.get(r) for r in plot_list1[k]], style = [marker_dict.get(r, '*') for r in plot_list1[k]], kind='line', title= name_list1[k][:-3], fontsize=16, legend = False)
        plot_list1[k].xs('EUT-WIO',axis=1).dropna().plot(ax=axs[i,j], color = 'maroon', style =  'v', kind='line', legend = False, linestyle='--')
        axs[i,j].set_ylabel('%')
        axs[i,j].set_xticks([1963,1972,1982,1992,2002,2012])
        axs[i,j].title.set_fontsize(18)
        median = []
        try:
            median, minim, maxim = calc_relDeviation(plot_list1[k])
            axs[i,j].annotate(str(round(median,2)) + ', ' + str(round( minim,2)) + ', ' + str(round(maxim ,2)) , ((2002.5, axs[i,j].get_ylim()[1]-axs[i,j].get_ylim()[1]*0.04)))
        except Exception:
            pass
        k = k+1

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
fig.savefig('Figure2.pdf', format='pdf', dpi =1200, bbox_inches='tight', pad_inches=0)

# #SAVE plot data to Excel (optional)
# path = './output/USA/FiguresStats/' + 'Data_Figure2'   
# save_list2Excel(path, name_list1, plot_list1)

##

'''

OPTIONAL: FIGURE2 SENSITIVITY : sensitivity to extension and filter matrix choice at low end-use resolution
variables methods & method_names need to be changed above for this plot to work

'''
# pal = sns.color_palette("colorblind") 
# dummy_df = plastic_electrical_df.copy()
# dummy_df[:] = 0

# #optionally with ExtAgg and WIO_filter diff
# color_dict = {'WIO-MFA': pal[3], 'EUT-WIO': 'maroon', 'WIO-MFA_extAgg': pal[3],'WIO-MFA_filtDif': pal[3], \
#             'EUT-WIO_extAgg': 'maroon','Exio_EUT-WIO': pal[4], 'Shipment_1':pal[7], 'Shipment_2':pal[0],'Shipment_3':pal[3]}

# marker_dict = {'WIO-MFA': 'o', 'EUT-WIO': 'v', 'WIO-MFA_extAgg': 'X','WIO-MFA_filtDif': '+' ,\
#             'EUT-WIO_extAgg': 'X'}


# name_list1 = ['(a) wood_construction_df','(b) wood_transport_df','(c) wood_packaging_food_df', '(d) wood_machinery_df', '(e) wood_furniture_df',\
#               '(f) steel_construction_df', '(g) steel_transport_df',  '(h) steel_packaging_food_df', '(i) steel_machinery_df',  '(j) steel_furniture_df',\
#               '(k) copper_construction_df', '(l) copper_transport_df',  '(x) dummy_df', '(m) copper_machinery_df', '(n) copper_furniture_df',\
#               '(o) alu_construction_df', '(p) alu_transport_df', '(q) alu_packaging_food_df', '(r) alu_machinery_df', '(s) alu_furniture_df', \
#               '(t) plastic_construction_df', '(u) plastic_transport_df',  '(v) plastic_packaging_food_df', '(w) plastic_electrical_df', '(x) plastic_furniture_df']

# plot_list1 = [eval(e[4:]) for e in name_list1]

# k,i,j = 0,0,0     
# fig, axs = plt.subplots(5,5 ,sharex=False, sharey=False, figsize=(33,22))
           
# for i in range(0,5):
#     for j in range (0,5):
#         plot_list1[k].plot(ax=axs[i,j], color = [color_dict.get(r) for r in plot_list1[k]], style = [marker_dict.get(r, '*') for r in plot_list1[k]], kind='line', title= name_list1[k][:-3], legend = False)
#         plot_list1[k].xs('EUT-WIO',axis=1).dropna().plot(ax=axs[i,j], color = 'maroon', kind='line', legend = False, linestyle='--')
#         k = k+1
#         axs[i,j].set_ylabel('%')
#         axs[i,j].set_xticks([1963,1972,1982,1992,2002,2012])
             
# axs[2,2].clear()
# axs[2,2].axis('off')
# lgd = axs[2,2].legend(loc='center',fontsize=18, ncol=5) #, ,fontsize=14)# bbox_to_anchor=(0.145, -0.02)

# def add_line(legend):
#     a = axs[1,0].get_legend_handles_labels()[0][:-1] 
#     b = axs[1,0].get_legend_handles_labels()[1][:-1]
#     c = tuple((a,b))
#     handles, labels = c
#     legend._legend_box = None
#     legend._init_legend_box(handles, labels)
#     legend._set_loc(legend._loc)
#     legend.set_title(legend.get_title().get_text())
    
# add_line(lgd)
# fig.suptitle('Sensitivity to extension choice & filter design (WIO-MFA, EUT-WIO) - high sector aggregation', y=1, fontsize = 16)
# fig.tight_layout()

# ### ADD differences of sensitivity and base cases and SAVE to EXCEL
# analysis_list_eval = [eval(x[4:]) for x in name_list1]
# for frame in analysis_list_eval:
#     try:
#         frame['Diff_WIO-MFA_extAgg'] = frame['WIO-MFA'] - frame['WIO-MFA_extAgg']
#         frame['Diff_EUT-WIO_extAgg'] = frame['EUT-WIO'] - frame['EUT-WIO_extAgg']
#         frame['Diff_WIO-MFA_filtDif'] = frame['WIO-MFA'] - frame['WIO-MFA_filtDif']
#         frame['rel_Diff_WIO-MFA_extAgg'] = (frame['WIO-MFA'] - frame['WIO-MFA_extAgg']) / frame['WIO-MFA'] 
#         frame['rel_Diff_EUT-WIO_extAgg'] = (frame['EUT-WIO'] - frame['EUT-WIO_extAgg']) / frame['EUT-WIO']
#         frame['rel_Diff_WIO-MFA_filtDif'] = (frame['WIO-MFA'] - frame['WIO-MFA_filtDif']) / frame['WIO-MFA'] 
#     except:
#         pass

# #SAVE plot data with differences to Excel (optional)
# path = './output/USA/FiguresStats/' + 'Data_Figure2_Sensitivity'   
# save_list2Excel(path, name_list1, plot_list1)
# #######


'''

 Create data for detailed plots for WOOD and CEMENT in the CONSTRUCTION SECTOR for FIGURE3
 (needs to be manually processed due to differing sector labels over years)

'''
# isolate construction sector sub-sectors and save in excel for manual processing
# (no automatic processing as different for each year)
# constr_1963 = EUTWio_detail_dict.get(1963).iloc[19:26,:]
# constr_1967 = EUTWio_detail_dict.get(1967).iloc[26:76,:]
# constr_1972 = EUTWio_detail_dict.get(1972).iloc[26:76,:]
# constr_1977 = EUTWio_detail_dict.get(1977).iloc[30:83,:]
# constr_1982 = EUTWio_detail_dict.get(1982).iloc[30:83,:]
# constr_1987 = EUTWio_detail_dict.get(1987).iloc[30:83,:]
# constr_1992 = EUTWio_detail_dict.get(1992).iloc[30:45,:] #checl if to add to this and the above minign stuff
# constr_1997 = EUTWio_detail_dict.get(1997).iloc[26:45,:]
# constr_2002 = EUTWio_detail_dict.get(2002).iloc[27:40,:]
# constr_2007 = EUTWio_detail_dict.get(2007).iloc[19:36,:] 
# constr_2012 = EUTWio_detail_dict.get(2012).iloc[19:36,:] 

# # save to Excel, including used filter matrices
# writer = pd.ExcelWriter(data_path_usa + '/Construction_detail' + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
# constr_1963.to_excel(writer,'1963')
# constr_1967.to_excel(writer,'1967')
# constr_1972.to_excel(writer,'1972')
# constr_1977.to_excel(writer,'1977')
# constr_1982.to_excel(writer,'1982')
# constr_1987.to_excel(writer,'1987')
# constr_1992.to_excel(writer,'1992')
# constr_1997.to_excel(writer,'1997')
# constr_2002.to_excel(writer,'2002')
# constr_2007.to_excel(writer,'2007')
# constr_2012.to_excel(writer,'2012')
# writer.save()
# save these dataframes, manupipulate them and read for FIGURE 3

####



'''

FIGURE 3: combine high, medium and low sector aggregation

'''
dummy_df = plastic_electrical_df.copy()
dummy_df[:] = 0

wood_detail = pd.read_excel(data_path_usa + 'Construction_detail_Run_220317-102202_manualEdit.xlsx',sheet_name='Wood_out', index_col=[0])
cement_detail = pd.read_excel(data_path_usa + 'Construction_detail_Run_220317-102202_manualEdit.xlsx',sheet_name='Cement_out', index_col=[0])


pal = sns.color_palette("colorblind") 
color_dict = {'CBA':pal[0], 'WIO-MFA': pal[1], 'Ghosh-IO AMC':pal[2],  \
              'Partial Ghosh-IO': pal[3], 'EUT-WIO': 'maroon', 'Exio_EUT-WIO': pal[4],\
            'Shipment_1':pal[7], 'Shipment_2':pal[0],'Shipment_3':pal[3]}
marker_dict = {'CBA':'o', 'WIO-MFA': 'o', 'Ghosh-IO AMC':'o',  \
              'Partial Ghosh-IO': 'o', 'EUT-WIO': 'v', 'Exio_EUT-WIO': '.'}
name_list1 = ['(a) wood_construction_df', '(b) wood_nonresidential_df','(a) wood_residential_df', '(x) dummy_df',
              '(x) dummy_df', '(x) dummy_df', '(e) cement_civil_engineering_df' , '(d) cement_nonresidential_df', '(c) cement_residential_df', '(x) dummy_df']
plot_list1 = [eval(e[4:]) for e in name_list1]

annotation_spot = [2000,2000,2000,2004,2004,2004,2004,2004,2004,2004,2004,2004]

k,i,j = 0,0,0     
fig, axs = plt.subplots(5,2 ,sharex=False, sharey=False, figsize=(11,15),gridspec_kw={'height_ratios':[1,1,0.6,1,1]}) # gridspec_kw={'height_ratios':[1,1,1.4]} 'width_ratios': [2,0.08],

for i in range(0,5):
    for j in range (0,2):
        try:
            plot_list1[k].plot(ax=axs[i,j], color = [color_dict.get(r,pal[0]) for r in plot_list1[k]], style = [marker_dict.get(r, '*') for r in plot_list1[k]], kind='line', title= name_list1[k][:-3], legend = False)
            plot_list1[k].xs('EUT-WIO',axis=1).dropna().plot(ax=axs[i,j], color = 'maroon', style =  'v', kind='line', legend = False, linestyle='--')
            axs[i,j].set_ylabel('%')
            axs[i,j].set_xticks([1963,1972,1982,1992,2002,2012])
        except:
            pass
        median = []
        try:
            median, minim, maxim = calc_relDeviation(plot_list1[k])
            axs[i,j].annotate(str(round(median,2)) + ', ' + str(round( minim,2)) + ', ' + str(round(maxim ,2)) , ((annotation_spot[k], axs[i,j].get_ylim()[1]-axs[i,j].get_ylim()[1]*0.06)))
        except Exception:
            pass
        k = k+1
             
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

name_list1_low = [ '(g) wood_detail','(f) cement_detail']
plot_list1_low = [eval(e[4:]) for e in name_list1_low]

i_list = [(1,1),(4,1)]

k = 0
for i,j in i_list:
        try:
            plot_list1_low[k].plot(ax=axs[i,j], color = [color_dict_low.get(r,pal[0]) for r in plot_list1_low[k]], style = [marker_dict_low.get(r, '*') for r in plot_list1_low[k]], kind='line', title= name_list1_low [k][:-7], legend = False)
            k = k+1
            axs[i,j].set_ylabel('%')
        except:
            continue
        
plot_list1_low[1].iloc[np.r_[1:9,13],:].plot(ax=axs[4,1], color = [color_dict_low.get(r) for r in plot_list1_low[1].iloc[np.r_[1:9,13],:]], style = [marker_dict_low.get(r, '*') for r in plot_list1_low[1]], kind='line', title= name_list1_low [1][:-7], legend = False)
plot_list1_low[0].iloc[np.r_[0:7,8],:3].plot(ax=axs[1,1], color = [color_dict_low.get(r) for r in plot_list1_low[0].iloc[np.r_[0:7,8],:3]], style = [marker_dict_low.get(r, '*') for r in plot_list1_low[0]], kind='line', title= name_list1_low [0][:-7], legend = False)
plot_list1_low[0].iloc[np.r_[0:6,8],3].plot(ax=axs[1,1], color = pal[3], style = [marker_dict_low.get(r, '*') for r in plot_list1_low[0]], kind='line', title= name_list1_low [0][:-7], legend = False)
                  
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
    a = axs[1,1].get_legend_handles_labels()[0][:9] + axs[4,1].get_legend_handles_labels()[0][4:8]
    b = axs[1,1].get_legend_handles_labels()[1][:9] + axs[4,1].get_legend_handles_labels()[1][4:8]
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
fig.savefig('Figure3.pdf', format='pdf', dpi =1200, bbox_inches='tight', pad_inches=0)

# #SAVE FIGURE 3 data to Excel (optional)
# path = './output/USA/FiguresStats/' + 'Data_Figure3'   
# save_list2Excel(path, (name_list1 + name_list1_low), (plot_list1 + plot_list1_low))




#########

# END OF USA FIGURES 

#########



'''

    #4 Assemble comparison of EXIOBASE countries and sectors (for multiple countries / regions)
    
'''

### DATASSEMBLY FOR EXIOBASE PLOTS

data_path_exio = os.path.join(main_path, 'output/Exiobase/')

year = 1995
years_exio = list(range(1995,2012))

regions = ['AT',  'AU', 'BE', 'BG', 'BR', 'CA', 'CH', 'CN', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 
           'FR', 'GB', 'GR', 'HR', 'HU', 'ID', 'IE', 'IN', 'IT', 'JP', 'KR', 'LT', 'LU', 'LV', 'MT', 
           'MX', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE', 'SI', 'SK', 'TR', 'TW', 'US', 'WA', 'WE', 
           'WF', 'WL', 'WM', 'ZA']

    
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


# #SAVE dictionary for selected regions and all defined materials (optional)
# save_regions = ['PT']
# save_materials = materials
# path = 'C:/Users/jstreeck/Desktop/2021_Portugal/'
# writer = pd.ExcelWriter(path + 'EXIOBASE_EndUse_Portugal' + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
# for region in save_regions:
#     for material in  save_materials:
#         df = region_dict.get(region).get(material)
#         df.to_excel(writer, sheet_name = material)
#     writer.save() 


### LOAD PHYSICAL SHIPMENT DATA FOR COUNTRIES OTHER THAN USA
load_path = path_input_data + '/Industry_Shipments/Other_Countries/'
physSplit_plastics_Intern  = pd.read_excel(load_path + '/Shipments_Plastics_EUROMAP.xlsx', sheet_name='clean data manip')
physSplit_plastics_China  = pd.read_excel(load_path + '/Shipments_Plastics_ChinaEU28.xlsx', sheet_name='China').set_index('Year')*100
physSplit_plastics_EU28  = pd.read_excel(load_path + '/Shipments_Plastics_ChinaEU28.xlsx', sheet_name='EU28').set_index('Year')*100
physSplit_steel_China = pd.read_excel(load_path + '/Shipments_IronSteel.xlsx', sheet_name='China').set_index('Year')*100
physSplit_steel_India = pd.read_excel(load_path + '/Shipments_IronSteel.xlsx', sheet_name='India').set_index('Year')*100
physSplit_steel_UK = pd.read_excel(load_path + '/Shipments_IronSteel.xlsx', sheet_name='UK').set_index('Year')*100
physSplit_alu_intern = pd.read_excel(load_path + '/Shipments_Alu_LiuMüller2013.xlsx', sheet_name='Liu_out', index_col=[0], header=[0,1])*100
physSplit_copper_EU28 = pd.read_excel(load_path + '/Shipments_Copper.xlsx', sheet_name='EU').set_index('Year')*100


##AGGREGATED: assemble dictionary for single countries to structure material end-uses for calling in plots and statistics
plotRegions = ['CN', 'IN','GB', 'AT', 'AU', 'DE', 'BE', 'BR', 'JP', 'IT', 'ZA', 'PT', 'RU', 'NL', 'FR', 'NO', 'ES', 'CH']#['US', 'JP', 'GB', 'FR','IT','DE', 'PT', 'RU', 'IN','CN', 'ID', 'ZA']
EU28 = ['GB', 'AT', 'DE', 'BE', 'IT', 'PT', 'NL', 'FR', 'NO', 'ES'] #might require expansion
plotMaterials = [ 'Plastic', 'steel', 'Copper', 'alumin']

material_region_dict = {}
for plotMaterial in plotMaterials:
    Exio_region_plotDict = []
    for plotRegion in plotRegions:
        randomlist = []
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
    
    

# ## FULL DETAIL material_region DICT: assemble dictionary for single countries to structure material end-uses for calling in plots and statistics
# plotRegions = ['CN', 'IN','GB', 'AT', 'AU', 'DE', 'BE', 'BR', 'JP', 'IT', 'ZA', 'PT', 'RU', 'NL', 'FR', 'NO', 'ES', 'CH']#['US', 'JP', 'GB', 'FR','IT','DE', 'PT', 'RU', 'IN','CN', 'ID', 'ZA']
# EU28 = ['GB', 'AT', 'DE', 'BE', 'IT', 'PT', 'NL', 'FR', 'NO', 'ES'] #might require expansion
# plotMaterials = [ 'Plastic', 'steel', 'Copper', 'alumin']

# material_region_dict = {}
# for plotMaterial in plotMaterials:
#     Exio_region_plotDict = []
#     for plotRegion in plotRegions:
#         randomlist = []
#         dict_2={}
#         plot_frame = region_dict.get(plotRegion).get(plotMaterial).T
#         plot_frame['Other machinery & appliances'] =  plot_frame['Machinery and equipment n.e.c. '] + \
#             plot_frame['Medical, precision and optical instruments, watches and clocks']
#         plot_frame['Electrical machinery & appliances'] =  plot_frame['Office machinery and computers'] + \
#             plot_frame['Radio, television and communication equipment and apparatus']+ \
#                 plot_frame['Electrical machinery and apparatus n.e.c.']
#         plot_frame['Transportation'] = plot_frame['Motor vehicles, trailers and semi-trailers'] + \
#             plot_frame['Other transport equipment']
#         plot_frame['All other'] = plot_frame['Printed matter and recorded media'] + plot_frame['Other raw materials']+\
#               + plot_frame['Secondary materials'] + plot_frame['Energy carriers']  \
#                   + plot_frame[ 'Other'] + plot_frame[ 'Products nec'] + plot_frame['Services']
        
#         if plotMaterial == 'Plastic':
#             try:
#                 plot_frame['Packaging_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Packaging']
#                 plot_frame['Automotive_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Automotive']
#                 plot_frame['Electrical_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Construction industry']
#                 plot_frame['Construction_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Electrical, electronics & telecom']
#                 plot_frame['Other_Euromap'] = physSplit_plastics_Intern.loc[physSplit_plastics_Intern['Country'] == region_transl.get(plotRegion)].iloc[:,1:].set_index('Application').transpose()['Others']
#             except:
#                 pass
#             if plotRegion == 'CN':
#                 plot_frame['Jiang_Packaging'] = physSplit_plastics_China['Packaging']
#                 plot_frame['Jiang_B&C'] = physSplit_plastics_China['B&C']
#                 plot_frame['Jiang_Automobile'] = physSplit_plastics_China['Automobile']
#                 plot_frame['Jiang_Electronics'] = physSplit_plastics_China['Electronics']
#                 plot_frame['Jiang_Agriculture'] = physSplit_plastics_China['Agriculture']
#                 plot_frame['Jiang_Others'] = physSplit_plastics_China['Others']
#             if plotRegion in EU28: #watch out: EU28 list not complete
#                 plot_frame['PlastEU_Packaging'] = physSplit_plastics_EU28['Packaging PE']
#                 plot_frame['PlastEU_B&C'] = physSplit_plastics_EU28['Building and construction PE']
#                 plot_frame['PlastEU_Automotive'] = physSplit_plastics_EU28['Automotive PE']
#                 plot_frame['PlastEU_Electrical'] = physSplit_plastics_EU28['Electrical&Electronic PE']
#                 plot_frame['PlastEU_Agriculture'] = physSplit_plastics_EU28['Agriculture PE']
#                 plot_frame['PlastEU_Others'] = physSplit_plastics_EU28['Others PE']
                
#         if plotMaterial == 'steel':
#             if plotRegion == 'CN':
#                 plot_frame['Wang_Construction'] = physSplit_steel_China['RFSCon']
#                 plot_frame['Wang_Transportation'] = physSplit_steel_China['RFSTra']
#                 plot_frame['Wang_Machinery&Appliances'] = physSplit_steel_China['RFSM']
#                 plot_frame['Wang_Other'] = physSplit_steel_China['RFSOth']
#             if plotRegion == 'IN':
#                 plot_frame['Pauliuk_Construction'] = physSplit_steel_India['construction']
#                 plot_frame['Pauliuk_Transportation'] = physSplit_steel_India['transportation']
#                 plot_frame['Pauliuk_Machinery'] = physSplit_steel_India['machinery']
#                 plot_frame['Pauliuk_Products'] = physSplit_steel_India['products']
#             if plotRegion == 'GB':
#                 plot_frame['Pauliuk_Construction'] = physSplit_steel_UK['Construction']
#                 plot_frame['Pauliuk_Transportation'] = physSplit_steel_UK['Transportation']
#                 plot_frame['Pauliuk_Machinery'] = physSplit_steel_UK['Machinery']
#                 plot_frame['Pauliuk_Products'] = physSplit_steel_UK['Products']
        
#         if plotMaterial == 'Copper':
#             if plotRegion in EU28: #watch out: EU28 list not complete
#                 plot_frame['Ciacci_B&C'] = physSplit_copper_EU28['Building and construction']
#                 plot_frame['Ciacci_Electrical'] = physSplit_copper_EU28['Electrical and Electronic Goods']
#                 plot_frame['Ciacci_Machinery'] = physSplit_copper_EU28['Industrial Machinery and Equipment']
#                 plot_frame['Ciacci_Transportation'] = physSplit_copper_EU28['Transportation Equipment']
#                 plot_frame['Ciacci_Products'] = physSplit_copper_EU28['Consumer and General Products']
        
#         if plotMaterial == 'alumin':
#             try:
#                 alu_shipment = physSplit_alu_intern.xs(region_transl.get(plotRegion), level=0, axis=1)
#                 plot_frame['Liu_building&construction'] = alu_shipment['B&C']
#                 plot_frame['Liu_Transport'] = alu_shipment['Trans']
#                 plot_frame['Liu_Machinery&equipment'] = alu_shipment['M&E']
#                 plot_frame['Liu_Electric&electronics'] = alu_shipment['EE']
#                 plot_frame['Liu_Containers&packaging']= alu_shipment['C&P']
#                 plot_frame['Liu_Consumer Durables'] = alu_shipment['ConDur']
#                 plot_frame['Liu_Others'] = alu_shipment['Others']
#             except:
#                 pass
        
#         Exio_region_plotDict.append(plot_frame) 
#         dict_2 = dict(zip(plotRegions,Exio_region_plotDict))
#     material_region_dict.update({plotMaterial:dict_2})   
    
    
# #SAVE dictionary for selected materials and all defined countries (optional)
# comp_mats = ['alumin', 'Plastic']
# path = './output/Exiobase/FiguresStats/' + 'Exiobase_18Countries_Alu_Plastic'
# writer = pd.ExcelWriter(path + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
# for material in comp_mats:
#     for region, df in  material_region_dict.get(material).items():
#         df.to_excel(writer, sheet_name= material + '_' + region)
#     writer.save()   


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


#######  


'''

FIGURE4 : EXIOBASE - combined region-level with all-region plots, swarmplots annotated

'''
   
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

# ##FULL material_region DICTIONARY    
# dropped_sectors = ['Machinery and equipment n.e.c. ', 'Medical, precision and optical instruments, watches and clocks', \
#                     'Office machinery and computers','Radio, television and communication equipment and apparatus',\
#                     'Electrical machinery and apparatus n.e.c.', 'Office machinery and computers',  'Motor vehicles, trailers and semi-trailers',
#                     'Other transport equipment', 'Secondary materials', 'Printed matter and recorded media', 'Other raw materials',\
#                       'Energy carriers','Other','Products nec', 'Services' ]

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

# # ##FULL material_region DICTIONARY    
# china_steel = material_region_dict.get('steel').get('CN').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Wang_Other',axis=1)
# india_steel = material_region_dict.get('steel').get('IN').replace(0,np.nan).drop(dropped_sectors,axis=1)
# britain_steel= material_region_dict.get('steel').get('GB').replace(0,np.nan).drop(dropped_sectors,axis=1) 
# china_alumin = material_region_dict.get('alumin').get('CN').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Liu_Others',axis=1)
# india_alumin = material_region_dict.get('alumin').get('IN').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Liu_Others',axis=1)
# britain_alumin= material_region_dict.get('alumin').get('GB').replace(0,np.nan).drop(dropped_sectors,axis=1).drop('Liu_Others',axis=1)
# china_Plastic = material_region_dict.get('Plastic').get('CN').replace(0,np.nan).drop(dropped_sectors,axis=1)
# india_Plastic = material_region_dict.get('Plastic').get('IN').replace(0,np.nan).drop(dropped_sectors,axis=1)
# britain_Plastic= material_region_dict.get('Plastic').get('GB').replace(0,np.nan).drop(dropped_sectors,axis=1) 
dummy_df = china_steel.copy()
dummy_df[:] = 0
########

          
fig, axs = plt.subplots(5,3 ,sharex=False, sharey=False, figsize=(14,18),gridspec_kw={'height_ratios':[1,1,0.6,1,1]})
#axs[3,2].axis('off')

#check if summing up to 100%
#lafa = material_region_dict.get('steel').get('CN').drop(dropped_sectors,axis=1)

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
# axs[0,0].set_ylim(5,material_region_dict.get('steel').get('CN').max().max()+5)
# axs[0,1].set_ylim(5,material_region_dict.get('steel').get('IN').max().max()+5)
# axs[0,2].set_ylim(5,material_region_dict.get('steel').get('GB').max().max()+5)


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
 
lgd = fig.legend(loc='center', bbox_to_anchor=(0.5, 0.48),fontsize=14, ncol=3) #, bbox_to_anchor=(0.01, 0.5),fontsize=14)
#0.12, -0.12)
def add_line(legend):
    ax1 = legend.axes
    from matplotlib.lines import Line2D

    import matplotlib.patches as mpatches
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
fig.suptitle('Exiobase all end-uses for selected regions and all regions for selected end-uses', y=1, fontsize = 16)
#fig.suptitle('Comparison of end-use shares - high sector aggregation', y=1, fontsize = 16)
fig.tight_layout()
#fig.savefig('Figure4.pdf', format='pdf', dpi =1200, bbox_inches='tight', pad_inches=0)


#SAVE FIGURE 4 data to Excel (option 2: save after added the difference between MIOT and shipment results (below))
# figure_4_plotNames = ['china_steel', 'india_steel', 'britain_steel', 'china_alumin', 'india_alumin', 'britain_alumin', 'china_Plastic',\
#                  'india_Plastic', 'britain_Plastic', 'end_use_all_aluConst', 'end_use_all_steelConst', 'end_use_all_steelMotor']
# figure_4_plots = [eval(e) for e in figure_4_plotNames]
# path = './output/USA/FiguresStats/' + 'Data_Figure4'   
# save_list2Excel(path, figure_4_plotNames, figure_4_plots)
###################



''' 

CALCULATE DIFFERENCES between MIOT-based and shipment results for EXIOBASE FIGURE 4

'''

#save figure 4 data to Excel 
figure_4_plotNames = ['china_steel', 'india_steel', 'britain_steel', 'china_alumin', 'india_alumin', 'britain_alumin', 'china_Plastic',\
                 'india_Plastic', 'britain_Plastic', 'end_use_all_aluConst', 'end_use_all_steelConst', 'end_use_all_steelMotor']

#####################    
analysis_list_eval = [eval(x) for x in figure_4_plotNames]
   
for frame in analysis_list_eval:
    try:
        frame['ExioConstruct-Construction_Euromap'] = frame['Construction'] - frame['Construction_Euromap']
        frame['ExioTransport-Automotive_Euromap'] = frame['Transportation'] - frame['Automotive_Euromap']
        frame['ExioMachElectric-Electrical_Euromap'] = frame['Electrical machinery & appliances'] + frame['Other machinery & appliances']  - frame['Electrical_Euromap']
        frame['rel_Construction_Euromap'] = frame['ExioConstruct-Construction_Euromap'] / frame['Construction_Euromap']
        frame['rel_Automotive_Euromap'] = frame['ExioTransport-Automotive_Euromap'] / frame['Automotive_Euromap']
        frame['rel_Electrical_Euromap'] = frame['ExioMachElectric-Electrical_Euromap'] / frame['Electrical_Euromap']
    except:
        pass      
    try:
        frame['ExioConstruct-Jiang_B&C'] = frame['Construction'] - frame['Jiang_B&C']
        frame['ExioTransport-Jiang_Automobile'] = frame['Transportation'] - frame['Jiang_Automobile']
        frame['ExioMachElectric-Jiang_Electronics'] = frame['Electrical machinery & appliances'] + frame['Other machinery & appliances']  - frame['Jiang_Electronics']
        frame['rel_Jiang_B&C'] = frame['ExioConstruct-Jiang_B&C'] / frame['Jiang_B&C']
        frame['rel_Jiang_Automobile'] = frame['ExioTransport-Jiang_Automobile'] / frame['Jiang_Automobile']
        frame['rel_Jiang_Electronics'] = frame['ExioMachElectric-Jiang_Electronics'] / frame['Jiang_Electronics']
    except:
        pass     
    try:
        frame['ExioConstruct-PlastEU_B&C'] = frame['Construction'] - frame['PlastEU_B&C']
        frame['ExioTransport-PlastEU_Automotive'] = frame['Transportation'] - frame['PlastEU_Automotive']
        frame['ExioMachElectric-PlastEU_Electrical'] = frame['Electrical machinery & appliances'] + frame['Other machinery & appliances']  - frame['PlastEU_Electrical']
        frame['rel_PlastEU_B&C'] = frame['ExioConstruct-PlastEU_B&C'] / frame['PlastEU_B&C']
        frame['rel_PlastEU_Automotive'] = frame['ExioTransport-PlastEU_Automotive'] / frame['PlastEU_Automotive']
        frame['rel_PlastEU_Electrical'] = frame['ExioMachElectric-PlastEU_Electrical'] / frame['PlastEU_Electrical']
    except:
        pass  
    try:
        frame['ExioConstruct-Wang_Construction'] = frame['Construction'] - frame['Wang_Construction']
        frame['ExioTransport-Wang_Transportation'] = frame['Transportation'] - frame['Wang_Transportation']
        frame['ExioMachElectric-Wang_Mach&Appliances'] = frame['Electrical machinery & appliances'] + frame['Other machinery & appliances']  - frame['Wang_Machinery'] - frame['Wang_Appliances']
        frame['rel_Wang_Construction'] = frame['ExioConstruct-Wang_Construction'] / frame['Wang_Construction']
        frame['rel_Wang_Transportation'] = frame['ExioTransport-Wang_Transportation'] / frame['Wang_Transportation']
        frame['rel_Wang_Mach&Appliances'] = frame['ExioMachElectric-Wang_Mach&Appliances'] / (frame['Wang_Machinery'] - frame['Wang_Appliances'])
    except:
        pass  
    try:
        frame['ExioConstruct-Pauliuk_Construction'] = frame['Construction'] - frame['Pauliuk_Construction']
        frame['ExioTransport-Pauliuk_Transportation'] = frame['Transportation'] - frame['Pauliuk_Transportation']
        frame['ExioMachElectric-Pauliuk_Machinery'] = frame['Electrical machinery & appliances'] + frame['Other machinery & appliances']  - frame['Pauliuk_Machinery']
        frame['rel_Pauliuk_Construction'] = frame['ExioConstruct-Pauliuk_Construction'] / frame['Pauliuk_Construction']
        frame['rel_Pauliuk_Transportation'] = frame['ExioTransport-Pauliuk_Transportation'] / frame['Pauliuk_Transportation']
        frame['rel_Pauliuk_Machinery'] = frame['ExioMachElectric-Pauliuk_Machinery'] / frame['Pauliuk_Machinery']
        # not working for britain_Steel??????
    except:
        pass
    try:
        frame['ExioConstruct-Liu_building&construction'] = frame['Construction'] - frame['Liu_building&construction']
        frame['ExioTransport-Liu_Transport'] = frame['Transportation'] - frame['Liu_Transport']
        frame['ExioOtherMach-Liu_Machinery&equipment'] =  frame['Other machinery & appliances']  - frame['Liu_Machinery&equipment']
        frame['ExioElectric-Liu_Electric&electronics'] =   frame['Electrical machinery & appliances']   -  frame['Liu_Electric&electronics']
        frame['rel_Liu_building&construction'] = frame['ExioConstruct-Liu_building&construction'] / frame['Liu_building&construction']
        frame['rel_Liu_Transport'] = frame['ExioTransport-Liu_Transport'] / frame['Liu_Transport']
        frame['rel_Liu_Machinery&equipment'] = frame['ExioOtherMach-Liu_Machinery&equipment'] / frame['Liu_Machinery&equipment']
        frame['rel_Liu_Electric&electronics'] = frame['ExioElectric-Liu_Electric&electronics'] / frame['Liu_Electric&electronics']
    except:
        pass
    
#SAVE (optional)
figure_4_plots = [eval(e) for e in figure_4_plotNames]
path = './output/Exiobase/FiguresStats/' + 'Data_Figure4'   
save_list2Excel(path, figure_4_plotNames, figure_4_plots)

'''

ADDITIONAL PLOTS: EXIOBASE plots in SI 1.3.3 (comparison of country-level industry shipments with MIOT-based results for aluminum and plastics
                                              
'''
##to be run with FULL DETAIL material_region DICTIONARY (lines 835-933) and figure 4 implementation with full dictionary (lines 982-987, 1017-1026)
dropped_sectors = ['Machinery and equipment n.e.c. ', 'Medical, precision and optical instruments, watches and clocks', \
                    'Office machinery and computers','Radio, television and communication equipment and apparatus',\
                    'Electrical machinery and apparatus n.e.c.', 'Office machinery and computers',  'Motor vehicles, trailers and semi-trailers',
                    'Other transport equipment', 'Secondary materials', 'Printed matter and recorded media', 'Other raw materials',\
                      'Energy carriers','Other','Products nec', 'Services' ]

comp_mats = ['alumin', 'Plastic']
for material in comp_mats:
    for region, df in  material_region_dict.get(material).items():
        df = df.replace(0,np.nan).drop(dropped_sectors,axis=1)
        df.plot( ylabel = '%', title= material + '_' + region, kind='line', color= [color_dict.get(r) for r in df], style=[marker_dict.get(r, '*') for r in df], legend=False)
