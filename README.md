# IO_End_Use_Splits

File to calculate the destination of crude materials (e.g. apparent consumption of crude steel) to product end-uses.

1) The Python script contained in this repository first reads the prepared matrices from Excel files (also in this repository) and 
     derives technology matrix A, total requirements L and total commodity output x from those.
     Afterwards, three different methodologies are applied to calculate product end-uses:
#
A) Leontief-type approaches
#
A.1) Consumption-based approach to product end-uses - methodology as applied to calculate footprints
#
A.2) WIO-MFA approach to product end-uses - Waste Input-Output Approach to Material Flow Analysis - here the technology matrix A is filtered to represent only physical flows
   #
   A.2.1-A.2.2) intermediate steps (see script)
   #
   A.2.3) application of WIO-MFA together with HEM (Hypothetical Extraction Method), in order to determine intermediate processing stages contained in products delivered to final           demand
#   
B) Ghosh-type approach
#
 B.1) Ghosh-type approach to product end-uses - based on the technology matrix A_icc, market shares are calculated and crude materials are distributed downstream the supply chain
      according to these shares
