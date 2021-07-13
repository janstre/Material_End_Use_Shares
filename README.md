# IO_End_Use_Splits

File to calculate the destination of crude materials (e.g. apparent consumption of crude steel) to product end-uses.

0.0) The Python script contained in this repository first reads the prepared matrices from Excel files (also in this repository) and 
     derives technology matrix A_icc, total requirements L_icc and total commodity output x_icc from those.
     Afterwards, three different methodologies are applied to calculate product end-uses:
#
1.1) Consumption-based approach to product end-uses - methodology as applied to calculate footprints
#
1.2) WIO-MFA approach to product end-uses - Waste Input-Output Approach to Material Flow Analysis - here the technology matrix A_icc is filtered to represent only physical flows
   #1.2.1-1.2.3) intermediate steps (see script)
   #1.2.4) application of WIO-MFA together with HEM (Hypothetical Extraction Method), in order to determine intermediate processing stages contained in products delivered to final           demand
#    
 1.3) Ghosh-type approach to product end-uses - based on the technology matrix A_icc, market shares are calculated and crude materials are distributed downstream the supply chain
      according to these shares
