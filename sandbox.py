#from html_report import load_data_mult
from collections import namedtuple
import pandas as pd
import yaml

paths = [
        # River Flows
        "/CALSIM/C_LWSTN/.*//.*/.*/",
        "/CALSIM/D_LWSTN_CCT011/.*//.*/.*/",
        "/CALSIM/C_WKYTN/.*//.*/.*/",
        "/CALSIM/C_KSWCK/.*//.*/.*/",
        "/CALSIM/C_SAC097/.*//.*/.*/",
        "/CALSIM/C_FTR059/.*//.*/.*/",
        "/CALSIM/C_FTR003/.*//.*/.*/",
        "/CALSIM/C_YUB006/.*//.*/.*/",
        "/CALSIM/C_SAC083/.*//.*/.*/",
        "/CALSIM/C_NTOMA/.*//.*/.*/",
        "/CALSIM/C_AMR004/.*//.*/.*/",
        "/CALSIM/GP_SACWBA/.*//.*/.*/",
        #Exports
        "/CALSIM/C_CAA003/.*//.*/.*/",
        "/CALSIM/C_CAA003_SWP/.*//.*/.*/",
        "/CALSIM/C_CAA003_CVP/.*//.*/.*/",
        "/CALSIM/C_CAA003_WTS/.*//.*/.*/",
        "/CALSIM/C_DMC000/.*//.*/.*/",
        "/CALSIM/C_DMC000_CVP/.*//.*/.*/",
        "/CALSIM/C_DMC000_WTS/.*//.*/.*/",
        #Deliveries
        "/CALSIM/SWP_TA_TOTAL/.*//.*/.*/",
        "/CALSIM/SWP_IN_TOTAL/.*//.*/.*/",
        "/CALSIM/SWP_CO_TOTAL/.*//.*/.*/",
        ]

for p in paths:
    b = p.split('/')[2]

    print(
    f"{b}:\n\
    bpart: {b}\n\
    pathname: {p}\n\
    alias:\n\
    table_convert: cfs_taf\n\
    table_display: wy\n\
    type: Flow\n\
      ")
   