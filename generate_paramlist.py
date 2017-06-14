import argparse
import json
import pprint
from sys import exit
import uuid
import ast

def main():
    parser = argparse.ArgumentParser(prog='Paramlist Generator')
    parser.add_argument('case_name')

    args = parser.parse_args()

    case_name = args.case_name

    if case_name == 'defaults':
        paramlist = defaults()
    else:
        print('Not a valid case name')
        exit()

    write_file(paramlist)

def defaults():

    paramlist = {}

    paramlist['turbulence'] = {}
    paramlist['turbulence']['prandtl_number'] = 1.0
    paramlist['turbulence']['Ri_bulk_crit'] = 0.0

    paramlist['turbulence']['EDMF_PrognosticTKE'] = {}
    paramlist['turbulence']['EDMF_PrognosticTKE']['surface_area'] = 0.1
    paramlist['turbulence']['EDMF_PrognosticTKE']['surface_scalar_coeff'] = 0.3
    paramlist['turbulence']['EDMF_PrognosticTKE']['tke_ed_coeff'] = 0.25
    paramlist['turbulence']['EDMF_PrognosticTKE']['w_entr_coeff'] = 2.5 # "b1"
    paramlist['turbulence']['EDMF_PrognosticTKE']['w_buoy_coeff'] =  2.0 # "b2"
    paramlist['turbulence']['EDMF_PrognosticTKE']['tke_diss_coeff'] = 0.304

    paramlist['turbulence']['EDMF_BulkSteady'] = {}
    paramlist['turbulence']['EDMF_BulkSteady']['surface_area'] = 0.1
    paramlist['turbulence']['EDMF_BulkSteady']['surface_scalar_coeff'] = 0.3
    paramlist['turbulence']['EDMF_BulkSteady']['w_entr_coeff'] = 2.0  #"w_b"
    paramlist['turbulence']['EDMF_BulkSteady']['w_buoy_coeff'] = 1.0
    paramlist['turbulence']['EDMF_BulkSteady']['max_area_factor'] = 2.0

    paramlist['turbulence']['updraft_microphysics'] = {}
    paramlist['turbulence']['updraft_microphysics']['max_supersaturation'] = 0.1

    return  paramlist



def write_file(paramlist):


    fh = open('paramlist.in', 'w')
    pprint.pprint(paramlist)
    json.dump(paramlist, fh, sort_keys=True, indent=4)
    fh.close()

    return


if __name__ == '__main__':
    main()