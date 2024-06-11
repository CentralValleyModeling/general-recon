import pandas as pd
import pandss as pdss
import yaml
import os
import csv

a_list = [
["SWP_TA_ACFC","Alameda County FC&WCD, Zone 7","Delivery - TA"],
["SWP_TA_ACWD","Alameda County WD","Delivery - TA"],
["SWP_TA_AVEK","Antelope Valley-East Kern WA","Delivery - TA"],
["SWP_TA_CLWA1","Santa Clarita WA (San Joaquin)","Delivery - TA"],
["SWP_TA_CLWA2","Santa Clarita WA (South Coast)","Delivery - TA"],
["SWP_TA_CVWD","Coachella Valley WD","Delivery - TA"],
["SWP_TA_KINGS","County of Kings","Delivery - TA"],
["SWP_TA_CLA","Crestline-Line Arrowhead WA","Delivery - TA"],
["SWP_TA_DESERT","Desert WA","Delivery - TA"],
["SWP_TA_DUDLEY","Dudley Ridge WD","Delivery - TA"],
["SWP_TA_EMPIRE","Empire West Side ID","Delivery - TA"],
["SWP_TA_KERNAG","Kern County WA (Ag)","Delivery - TA"],
["SWP_TA_KERNMI","Kern County WA (MI)","Delivery - TA"],
["SWP_TA_LCID","Littlerock Creek ID","Delivery - TA"],
["SWP_TA_MWD","Metropolitan WDSC","Delivery - TA"],
["SWP_TA_MWA","Mojave WA","Delivery - TA"],
["SWP_TA_NAPA","Napa County FC&WCD","Delivery - TA"],
["SWP_TA_OAK","Oak Flat WD","Delivery - TA"],
["SWP_TA_PWD","Palmdale WD","Delivery - TA"],
["SWP_TA_SBV","San Bernadino Valley MWD","Delivery - TA"],
["SWP_TA_SGV","San Gabriel Valley MWD","Delivery - TA"],
["SWP_TA_SGP","San Gorgonio Pass WA","Delivery - TA"],
["SWP_TA_SLO","San Luis Obispo County FC&WCD","Delivery - TA"],
["SWP_TA_SB","Santa Barbara County FC&WCD","Delivery - TA"],
["SWP_TA_SCV","Santa Clara Valley WD","Delivery - TA"],
["SWP_TA_SOLANO","Solano County WA","Delivery - TA"],
["SWP_TA_TULARE","Tulare Lake Basin WSD","Delivery - TA"],
["SWP_TA_VC","Ventura County FCD","Delivery - TA"],
["SWP_CO_ACFC","Alameda County FC&WCD, Zone 7","Delivery - CO"],
["SWP_CO_ACWD","Alameda County WD","Delivery - CO"],
["SWP_CO_AVEK","Antelope Valley-East Kern WA","Delivery - CO"],
["SWP_CO_CLWA2","Santa Clarita WA (South Coast)","Delivery - CO"],
["SWP_CO_CVWD","Coachella Valley WD","Delivery - CO"],
["SWP_CO_KINGS","County of Kings","Delivery - CO"],
["SWP_CO_CLA","Crestline-Line Arrowhead WA","Delivery - CO"],
["SWP_CO_DESERT","Desert WA","Delivery - CO"],
["SWP_CO_DUDLEY","Dudley Ridge WD","Delivery - CO"],
["SWP_CO_EMPIRE","Empire West Side ID","Delivery - CO"],
["SWP_CO_KERN","Kern Counta WA","Delivery - CO"],
["SWP_CO_LCID","Littlerock Creek ID","Delivery - CO"],
["SWP_CO_MWD","Metropolitan WDSC","Delivery - CO"],
["SWP_CO_MWA","Mojave WA","Delivery - CO"],
["SWP_CO_NAPA","Napa County FC&WCD","Delivery - CO"],
["SWP_CO_OAK","Oak Flat WD","Delivery - CO"],
["SWP_CO_PWD","Palmdale WD","Delivery - CO"],
["SWP_CO_SBV","San Bernadino Valley MWD","Delivery - CO"],
["SWP_CO_SGV","San Gabriel Valley MWD","Delivery - CO"],
["SWP_CO_SGP","San Gorgonio Pass WA","Delivery - CO"],
["SWP_CO_SLO","San Luis Obispo County FC&WCD","Delivery - CO"],
["SWP_CO_SB","Santa Barbara County FC&WCD","Delivery - CO"],
["SWP_CO_SCV","Santa Clara Valley WD","Delivery - CO"],
["SWP_CO_SOLANO","Solano County WA","Delivery - CO"],
["SWP_CO_TULARE","Tulare Lake Basin WSD","Delivery - CO"],
["SWP_CO_VC","Ventura County FCD","Delivery - CO"],
["SWP_CO_CLWA1","Santa Clarita WA (San Joaquin)","Delivery - CO"],
["SWP_IN_ACFC","Alameda County FC&WCD, Zone 7","Delivery - IN"],
["SWP_IN_ACWD","Alameda County WD","Delivery - IN"],
["SWP_IN_AVEK","Antelope Valley-East Kern WA","Delivery - IN"],
["SWP_IN_CLWA2","Santa Clarita WA (South Coast)","Delivery - IN"],
["SWP_IN_CVWD","Coachella Valley WD","Delivery - IN"],
["SWP_IN_KINGS","County of Kings","Delivery - IN"],
["SWP_IN_CLA","Crestline-Line Arrowhead WA","Delivery - IN"],
["SWP_IN_DESERT","Desert WA","Delivery - IN"],
["SWP_IN_DUDLEY","Dudley Ridge WD","Delivery - IN"],
["SWP_IN_EMPIRE","Empire West Side ID","Delivery - IN"],
["SWP_IN_KERN","Kern Counta WA","Delivery - IN"],
["SWP_IN_LCID","Littlerock Creek ID","Delivery - IN"],
["SWP_IN_MWD","Metropolitan WDSC","Delivery - IN"],
["SWP_IN_MWA","Mojave WA","Delivery - IN"],
["SWP_IN_NAPA","Napa County FC&WCD","Delivery - IN"],
["SWP_IN_OAK","Oak Flat WD","Delivery - IN"],
["SWP_IN_PWD","Palmdale WD","Delivery - IN"],
["SWP_IN_SBV","San Bernadino Valley MWD","Delivery - IN"],
["SWP_IN_SGV","San Gabriel Valley MWD","Delivery - IN"],
["SWP_IN_SGP","San Gorgonio Pass WA","Delivery - IN"],
["SWP_IN_SLO","San Luis Obispo County FC&WCD","Delivery - IN"],
["SWP_IN_SB","Santa Barbara County FC&WCD","Delivery - IN"],
["SWP_IN_SCV","Santa Clara Valley WD","Delivery - IN"],
["SWP_IN_SOLANO","Solano County WA","Delivery - IN"],
["SWP_IN_TULARE","Tulare Lake Basin WSD","Delivery - IN"],
["SWP_IN_VC","Ventura County FCD","Delivery - IN"],
["SWP_IN_CLWA1","Santa Clarita WA (San Joaquin)","Delivery - IN"],
]



def generate_yaml_file(varlist, filename):
    """
    Generate a YAML file with given data.

    Args:
    - data: Dictionary containing the data to be written to the YAML file.
    - filename: Name of the YAML file to be generated.
    """
    data = {}

    for var in varlist:
        data[var[0]] = {
            'bpart': var[0],
            'pathname': f'/CALSIM/{var[0]}/.*//.*/.*/',
            'alias': var[1],
            'table_convert': 'cfs_taf',
            'table_display': 'wy',
            'type': var[2]
        }    

    with open(filename, 'w') as file:
        yaml.dump(data, file)
    print(f"YAML file '{filename}' generated successfully.")


generate_yaml_file(a_list,'swp_contractors.yaml')
