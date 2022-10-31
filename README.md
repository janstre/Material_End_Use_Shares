# Material_End_Use_Shares

This repository documents code and data for tracing material flows into final products using 
industry shipment data in physical units and monetary input-output tables.

Underlying methods and documentation can be found in the two related journal articles
that are currently in revision:

Streeck, Jan; Pauliuk, Stefan; Wieland, Hanspeter; Wiedenhofer, Dominik (in revision_): 
A review of methods to trace material flows into final products in dynamic material flow 
analysis - from industry shipments in physical units to monetary input-output tables. 
Journal of Industrial Ecology.

Streeck, Jan; Wieland, Hanspeter; Pauliuk, Stefan; Plank, Barbara; Nakajima, Kenichi; 
Wiedenhofer, Dominik (in revision_): A review of methods to trace material flows into 
final products in dynamic material flow analysis: a comparative application of methods 
to the USA and EXIOBASE3 regions. Journal of Industrial Ecology.

Below follows a brief description of the information contained in this repository. For
any questions please write to jan.streeck@boku.ac.at

- Python scripts (v1):
   
  - EndUseShares_USA_main_vx.py calculates end-use shares from U.S. national benchmark 
    input-output tables (IOTs) 1963-2012 and for the five IOT-based methods described
    in above publications. Related input data can be found under ./input_data/USA

  - EndUseShares_Exiobase_main_vx.py calculates end-use shares from EXIOBASE IOTs with the
    method End-Use Transfer Waste Input Output MFA. EXIOBASE input data needs to be
    downloaded separately.

  - EndUseShares_Stats_vx.py calculates some basic statistics for relations among the results
    of different IOT-based methods, industry shipments in physical units; as well as the
    two IOTs from U.S national tables and EXIOBASE

  - EndUseShares_Graphs_Outputs_vx.py assembles data frames required to do in paper plots and
    saves data frames to spreadsheets

  - under ./modules functions used in above data frames are defined in two scripts (one for actual
    calculations and one for graph-related functions)

- Input data (./input)
  
  - contains yield filter according to waste input-output MFA for application to both EXIOBASE and USA
    tables; folder for USA IOT-related data; and a folder for industry shipment data in physical units

  - ./USA contains all matrices required for calculating end-use shares for the USA (obtained from U.S.
    Bureau of Economic Analysis' website) A, Z, Y, _Base refers to default tables while _ExtAgg indicates that
    certain sectors were aggregated before calculations; Filters that were used to 1) aggregate individual
    IOT sectors to sector groups and 2) define all kind of filters for mass, yield, ...; spreadsheets documenting
    the ratios between intermediate and final demand (only for non-service sectors, see filter for definition) that
    were used to make a decision to destine sectors as intermediate or end-use in the Partial Ghosh-IO method 
    (see documentation in papers)

  - ./Industry_Shipments contains collection of end-use shares based on data in physical units for the USA
    (Shipments_USA) and globally (in folder ./Other_Countries)

- Output data (./output) - for GitHub too large to be stored, see Zenodo
  
  - ./USA contains end-use share results for different IOT-based methods for base case (_Base) and aggregation of
    selection extension sectors (_Extagg)

  - ./Exiobase contains end-use share results with method End-Use Transfer Waste Input Output MFA for all EXIOBASE
    regions and years
  	
  - ./FigureStats as subfolder of both the above contains aggregate results, see ReadMe therein for description

	



