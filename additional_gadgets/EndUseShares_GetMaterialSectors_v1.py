# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 11:48:11 2022

@author: jstreeck
"""


import os
import sys
import numpy as np
import pandas as pd

main_path = os.getcwd()
module_path = os.path.join(main_path, 'modules')
sys.path.insert(0, module_path)
data_path = os.path.join(main_path, 'input_data/USA/')

extensions = ['_ExtAgg']#, '_ExtAgg'] # choose scenario out of ['_Base','_ExtAgg']; _Base = Z,A,Y matrices as derived from Information of US BEA, _ExtAgg = in comparison to _Base, some IOT sectors were aggregated  (e.g. paper mills + paperboard mills), filter matrix _Base
years =  ['1963', '1967', '1972', '1977', '1982', '1987', '1992', '1997', '2002','2007', '2012'] # year has to be a string

extension_bunker = []
for extension in extensions:
    for year in years:
        filter_matrix = pd.read_excel(data_path + 'Filter_' + year  + extension + '.xlsx',index_col=[0,1],header=[0,1],sheet_name='mass_&_aggreg') # filter and aggregation matrix
        materials  = filter_matrix.loc[:,(['All'],['Materials'])]
        extension_bunker.append(materials.replace(0,np.nan).dropna()) 
    
writer = pd.ExcelWriter('./output/USA/' + 'MaterialExtensionSectors' + extension + '_Run_{}.xlsx'.format(pd.datetime.today().strftime('%y%m%d-%H%M%S')))
for i in range(len(years)):
    extension_bunker[i].to_excel(writer,years[i])
writer.save()