# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 15:52:32 2022

@author: jstreeck
"""
import os
import sys
import pandas as pd

#define working directory and data paths
main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
path_input_data =  os.path.join(main_path, 'input_data/') 
data_path_usa = os.path.join(main_path, 'output/USA/')
data_path_exio = os.path.join(main_path, 'output/Exiobase/')

from EndUseShares_GraphsStatistics_functions_v1 import load_data_USA, load_data_USA_sensitivity, save_method_dictionaries, \
    plot_USA_low_resolution, assemble_materialEndUse_df, plot_USA_low_resolution_sensitivity, \
    save_construction_detail, plot_USA_medium_resolution, assemble_exiobase_results, assemble_exiobase_comparison_agg, \
     assemble_exiobase_comparison_full, plot_exiobase_agg, save_dict2Excel, save_exiobase_country_results, save_exiobase_shipment_results,\
         plots_exiobase_shipment_add_countries


##########################


''' Load data for end-use share results for USA;
optional: save dictionaries with end-use shares for
different materials and MIOT-based methods'''

CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, EUTWio_detail_dict, phys_dict, region_dict = load_data_USA(path_input_data, data_path_usa,data_path_exio)
# #save
# methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, phys_dict] 
# method_names = ['CBA', 'WIO-MFA', 'Ghosh-IO AMC', 'Partial Ghosh-IO', 'EUT-WIO', 'Industry_Shipments' ]
# path_1 = './output/USA/FiguresStats/' 
# path_2 =  '_fullResults_USA_test1'
# save_method_dictionaries(methods, method_names, path_1, path_2)

##########################


''' Plot Figure 2 standard (as in paper);
optional: save figure data'''

CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, EUTWio_detail_dict, phys_dict, region_dict = load_data_USA(path_input_data, data_path_usa,data_path_exio)
years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]
methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict] 
method_names = ['CBA', 'WIO-MFA', 'Ghosh-IO AMC', 'Partial Ghosh-IO', 'EUT-WIO' ]
fig, element_dict = plot_USA_low_resolution(methods, method_names, CBA_dict, phys_dict, region_dict, years)

##save figure (to working directory)
fig.savefig('Figure2.pdf', format='pdf', dpi =600, bbox_inches='tight', pad_inches=0)

##SAVE plot data to Excel
# path = './output/USA/FiguresStats/' + 'Data_Figure2'   
# save_dict2Excel(path, element_dict)

##########################


''' Plot Figure 2 sensitivity (as in paper SI);
optional: save figure data'''

Wio_dict, Wio_ext_dict, Wio_withServiceInput_dict, EUTWio_dict, EUTWio_ext_dict, phys_dict, region_dict = load_data_USA_sensitivity(path_input_data, data_path_usa,data_path_exio)
years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]
methods = [ Wio_dict, Wio_ext_dict , Wio_withServiceInput_dict,  EUTWio_dict, EUTWio_ext_dict] 
method_names = [ 'WIO-MFA', 'WIO-MFA_extAgg','WIO-MFA_filtDif', 'EUT-WIO', 'EUT-WIO_extAgg' ]
fig, element_dict = plot_USA_low_resolution_sensitivity(methods, method_names, Wio_dict, phys_dict, region_dict, years)

##save figure (to working directory)
fig.savefig('Figure2_Sensitivity.pdf', format='pdf', dpi =600, bbox_inches='tight', pad_inches=0)

##SAVE plot data to Excel (includes deviation of sensitivity scenarios)
# path = './output/USA/FiguresStats/' + 'Data_Figure2_Sensitivity'   
# save_dict2Excel(path, element_dict)

##########################


''' Assemble data for detailed plots for wood and cement
in the construction sector for Figure 3 (needs to be manually 
processed due to differing sector labels over years)'''

CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, EUTWio_detail_dict, phys_dict, region_dict = load_data_USA(path_input_data, data_path_usa,data_path_exio)
save_construction_detail(data_path_usa, EUTWio_detail_dict)
#save these dataframes, manupipulate them and read for assembling FIGURE 3 (only necessary if not created already)

##########################


''' Plot Figure 3 (as in paper);
optional: save figure data'''

CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict, EUTWio_detail_dict, phys_dict, region_dict = load_data_USA(path_input_data, data_path_usa,data_path_exio)
years = [1963,1967,1972,1977,1982,1987,1992,1997,2002,2007,2012]
methods = [CBA_dict, Wio_dict, Ghosh_dict, ParGhosh_dict, EUTWio_dict] 
method_names = ['CBA', 'WIO-MFA', 'Ghosh-IO AMC', 'Partial Ghosh-IO', 'EUT-WIO' ]
wood_detail = pd.read_excel(data_path_usa + 'Construction_detail_Run_220317-102202_manualEdit.xlsx',sheet_name='Wood_out', index_col=[0])
cement_detail = pd.read_excel(data_path_usa + 'Construction_detail_Run_220317-102202_manualEdit.xlsx',sheet_name='Cement_out', index_col=[0])
fig, element_dict = plot_USA_medium_resolution(methods, method_names, CBA_dict, phys_dict, region_dict, years, wood_detail, cement_detail)

##save figure (to working directory)
fig.savefig('Figure3.pdf', format='pdf', dpi =600, bbox_inches='tight', pad_inches=0)

##SAVE plot data to Excel (includes deviation of sensitivity scenarios)
# path = './output/USA/FiguresStats/' + 'Data_Figure3'   
# save_dict2Excel(path, element_dict)

##########################


''' Assemble EXBIOASE end-use shares for method
EUT-WIO for selected countries and save'''

data_path_exio = os.path.join(main_path, 'output/Exiobase/')
data_path_shipments = path_input_data + '/Industry_Shipments/Other_Countries/'
years_exio = list(range(1995,2012))
plotMaterials = ['Plastic', 'steel', 'Copper', 'alumin']
save_regions = ['PT']
materials, region_transl, region_dict = assemble_exiobase_results(data_path_exio, years_exio, save_regions)
file_name = 'EXIOBASE_EndUse_Portugal'
save_exiobase_country_results(data_path_exio, file_name, materials, region_dict, save_regions)

##########################


''' Plot Figure 4 with aggregate sector resolution (as in paper);
optional: save figure data'''

data_path_exio = os.path.join(main_path, 'output/Exiobase/')
data_path_shipments = path_input_data + '/Industry_Shipments/Other_Countries/'
years_exio = list(range(1995,2012))
plotMaterials = ['Plastic', 'steel', 'Copper', 'alumin']
regions = ['AT',  'AU', 'BE', 'BG', 'BR', 'CA', 'CH', 'CN', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 
           'FR', 'GB', 'GR', 'HR', 'HU', 'ID', 'IE', 'IN', 'IT', 'JP', 'KR', 'LT', 'LU', 'LV', 'MT', 
           'MX', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE', 'SI', 'SK', 'TR', 'TW', 'US', 'WA', 'WE', 
           'WF', 'WL', 'WM', 'ZA']
materials, region_transl, region_dict = assemble_exiobase_results(data_path_exio, years_exio, regions)
material_region_dict, end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor = \
    assemble_exiobase_comparison_agg(data_path_exio, data_path_shipments, years_exio, regions, region_transl, region_dict, plotMaterials)
fig, figure_4_frames = plot_exiobase_agg(data_path_exio, data_path_shipments, years_exio, regions, material_region_dict,\
                        end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor)
    
##save figure (to working directory)
fig.savefig('Figure4.pdf', format='pdf', dpi =600, bbox_inches='tight', pad_inches=0)
fig.savefig('Figure4.png', format='png', dpi =600, bbox_inches='tight', pad_inches=0)

##SAVE plot data to Excel (includes deviation of monetary vs. physical data)
# path = './output/Exiobase/FiguresStats/' + 'Data_Figure4'   
# save_dict2Excel(path, figure_4_frames)

##########################


'''EXIOBASE results for EUT-WIO - shipment comparison 
for additional countries'''

data_path_exio = os.path.join(main_path, 'output/Exiobase/')
data_path_shipments = path_input_data + '/Industry_Shipments/Other_Countries/'
years_exio = list(range(1995,2012))
target_materials = ['alumin', 'Plastic']
regions = ['CN', 'IN','GB', 'AT', 'AU', 'DE', 'BE', 'BR', 'JP', 'IT', 'ZA', 'PT', 'RU', 'NL', 'FR', 'NO', 'ES', 'CH']
materials, region_transl, region_dict = assemble_exiobase_results(data_path_exio, years_exio, regions)
material_region_dict, end_use_all_aluConst, end_use_all_steelConst, end_use_all_steelMotor = \
    assemble_exiobase_comparison_full(data_path_exio, data_path_shipments, years_exio, regions, region_transl, region_dict, target_materials)
plots_exiobase_shipment_add_countries(material_region_dict, target_materials)

#save plot data to spreadsheet
file_name = '/FiguresStats/Exiobase_18Countries_Alu_Plastic'
save_exiobase_shipment_results(data_path_exio, file_name, target_materials, material_region_dict)