import os
import subprocess
import json
import warnings
import pprint as pp
from netCDF4 import Dataset
import numpy as np

def simulation_setup(case):
    """
    generate namelist and paramlist files for scampy
    choose the name of the output folder
    """
    # Filter annoying Cython warnings that serve no good purpose.
    # see https://stackoverflow.com/questions/40845304/runtimewarning-numpy-dtype-size-changed-may-indicate-binary-incompatibility
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

    # simulation related parameters
    os.system("python ../generate_namelist.py " + case)
    file_case = open(case + '.in').read()
    namelist  = json.loads(file_case)
    # fh = open(namelist['meta']['casename']+ ".in", 'w')
    # add here changes to namelist file:
    namelist['output']['output_root'] = "./Tests."
    namelist['meta']['uuid'] = case
    write_file(case+".in",namelist)
    #pp.pprint(namelist)

    os.system("python ../generate_paramlist.py " +  case)
    file_params = open('paramlist_' + case + '.in').read()
    paramlist = json.loads(file_params)
    # add here changes to paramlist file such as:
    #paramlist['turbulence']['EDMF_PrognosticTKE']['entrainment_factor'] = 0.15
    write_file("paramlist_"+case+".in",paramlist)
    #pp.pprint(paramlist)

    # TODO - copied from NetCDFIO
    # ugly way to know the name of the folder where the data is saved
    uuid = str(namelist['meta']['uuid'])
    outpath = str(
        os.path.join(
            namelist['output']['output_root'] +
            'Output.' +
            namelist['meta']['simname'] +
            '.' +
            uuid[len(uuid )-5:len(uuid)]
        )
    )
    outfile = outpath + "/stats/Stats." + case + ".nc"

    res = {"namelist"  : namelist,
           "paramlist" : paramlist,
           "outfile"   : outfile}
    return res

def removing_files():
    """
    Remove the folder with netcdf files from tests.
    Remove the in files generated by scampy.
    """
    cmd = "rm -r Tests.Output.*"
    subprocess.call(cmd , shell=True)
    cmd = "rm *.in"
    subprocess.call(cmd , shell=True)

def write_file(name, list):
    fh = open(name, 'w')
    json.dump(list, fh, sort_keys=True, indent=4)
    fh.close()

    return

def read_scm_data(scm_data):
    """
    Read data from netcdf file into a dictionary that can be used for plots
    Input:
    scm_data  - scampy netcdf dataset with simulation results
    """
    variables = ["temperature_mean", "thetal_mean", "qt_mean", "ql_mean", "qr_mean",\
                 "buoyancy_mean", "b_mix","u_mean", "v_mean", "tke_mean",\
                 "updraft_buoyancy", "updraft_area", "env_qt", "updraft_qt", "env_ql", "updraft_ql", "updraft_thetal",\
                 "env_qr", "updraft_qr", "env_RH", "updraft_RH", "updraft_w", "env_w", "env_thetal",\
                 "massflux_h", "diffusive_flux_h", "total_flux_h", "diffusive_flux_u", "diffusive_flux_v",\
                 "massflux_qt","diffusive_flux_qt","total_flux_qt","turbulent_entrainment",\
                 "eddy_viscosity", "eddy_diffusivity", "mixing_length", "mixing_length_ratio",\
                 "entrainment_sc", "detrainment_sc", "massflux", "nh_pressure", "nh_pressure_b", "nh_pressure_adv", "nh_pressure_drag", "eddy_diffusivity",\
                 "Hvar_mean", "QTvar_mean", "HQTcov_mean", "env_Hvar", "env_QTvar", "env_HQTcov",\
                 "Hvar_dissipation", "QTvar_dissipation", "HQTcov_dissipation",\
                 "Hvar_entr_gain", "QTvar_entr_gain", "HQTcov_entr_gain",\
                 "Hvar_detr_loss", "QTvar_detr_loss", "HQTcov_detr_loss",\
                 "Hvar_shear", "QTvar_shear", "HQTcov_shear", "H_third_m", "QT_third_m", "W_third_m",\
                 "Hvar_rain", "QTvar_rain", "HQTcov_rain","tke_entr_gain","tke_detr_loss",\
                 "tke_advection","tke_buoy","tke_dissipation","tke_pressure","tke_transport","tke_shear"\
                ]

    data = {"z_half" : np.divide(np.array(scm_data["profiles/z_half"][:]),1000.0),\
            "t" : np.divide(np.array(scm_data["profiles/t"][:]),3600.0),\
            "rho_half": np.array(scm_data["reference/rho0_half"][:])}

    for var in variables:
        data[var] = []
        if (var=="QT_third_m"):
            data[var] = np.transpose(np.array(scm_data["profiles/"  + var][:, :]))*1e9  #g^3/kg^3
        elif ("qt" in var or "ql" in var or "qr" in var):
            try:
                data[var] = np.transpose(np.array(scm_data["profiles/"  + var][:, :])) * 1000  #g/kg
            except:
                data[var] = np.transpose(np.array(scm_data["profiles/w_mean" ][:, :])) * 0  #g/kg
        else:
            data[var] = np.transpose(np.array(scm_data["profiles/"  + var][:, :]))

    return data


def read_les_data(les_data):
    """
    Read data from netcdf file into a dictionary that can be used for plots
    Input:
    les_data - pycles netcdf dataset with specific fileds taken from LES stats file
    """
    variables = ["temperature_mean", "thetali_mean", "qt_mean", "ql_mean", "buoyancy_mean",\
                 "u_mean", "v_mean", "tke_mean","v_translational_mean", "u_translational_mean",\
                 "updraft_buoyancy", "updraft_fraction", "env_thetali", "updraft_thetali",\
                 "env_qt", "updraft_qt","env_RH", "updraft_RH", "env_ql", "updraft_ql",\
                 "diffusive_flux_u", "diffusive_flux_v","massflux","massflux_u", "massflux_v","total_flux_u", "total_flux_v",\
                 "qr_mean", "env_qr", "updraft_qr", "updraft_w", "env_w",  "env_buoyancy", "updraft_ddz_p_alpha",\
                 "thetali_mean2", "qt_mean2", "env_thetali2", "env_qt2", "env_qt_thetali",\
                 "tke_prod_A" ,"tke_prod_B" ,"tke_prod_D" ,"tke_prod_P" ,"tke_prod_T" ,"tke_prod_S",\
                 "Hvar_mean" ,"QTvar_mean" ,"env_Hvar" ,"env_QTvar" ,"env_HQTcov", "H_third_m", "QT_third_m", "W_third_m",\
                 "massflux_h" ,"massflux_qt" ,"total_flux_h" ,"total_flux_qt" ,"diffusive_flux_h" ,"diffusive_flux_qt"]

    data = {"z_half" : np.divide(np.array(les_data["z_half"][:]),1000.0),\
            "t" : np.divide(np.array(les_data["t"][:]),3600.0),\
            "rho": np.array(les_data["profiles/rho"][:]),\
            "p0": np.divide(np.array(les_data["profiles/p0"][:]),100.0)}

    for var in variables:
        data[var] = []
        if ("QT_third_m" in var ):
            data[var] = np.transpose(np.array(les_data["profiles/"  + var][:, :]))*1e9  #g^3/kg^3
        elif ("qt" in var or "ql" in var or "qr" in var):
            try:
                data[var] = np.transpose(np.array(les_data["profiles/"  + var][:, :])) * 1000  #g/kg
            except:
                data[var] = np.transpose(np.array(les_data["profiles/w_mean" ][:, :])) * 0  #g/kg
        else:
            data[var] = np.transpose(np.array(les_data["profiles/"  + var][:, :]))


    return data

def read_scm_data_timeseries(scm_data):
    """
    Read 1D data from netcdf file into a dictionary that can be used for plots
    Input:
    scm_data - scampy netcdf dataset with simulation results
    """
    variables = ["cloud_cover_mean", "cloud_base_mean", "cloud_top_mean",\
                 "ustar", "lwp_mean", "rwp_mean", "shf", "lhf", "Tsurface", "rd"]

    data = {"z_half" : np.array(scm_data["profiles/z_half"][:]),\
            "t" : np.array(scm_data["profiles/t"][:])}
    maxz = np.max(data['z_half'])

    for var in variables:
        data[var] = np.array(scm_data["timeseries/" + var][:])

    data["cloud_top_mean"][np.where(data["cloud_top_mean"] <= 0.0)] = np.nan
    data["cloud_base_mean"][np.where(data["cloud_base_mean"] >= maxz)] = np.nan

    return data

def read_les_data_timeseries(les_data):
    """
    Read 1D data from netcdf file into a dictionary that can be used for plots
    Input:
    les_data - netcdf Dataset with specific fileds taken from LES stats file
    """
    data = {"z_half_les" : np.array(les_data["z_half"][:]),\
            "t" : np.array(les_data["t"][:])}
    maxz = np.max(data['z_half_les'])

    CF = np.array(les_data["timeseries/cloud_fraction_mean"][:])
    CF[np.where(CF<=0.0)] = np.nan
    data["cloud_cover_mean"] = CF

    CT = np.array(les_data["timeseries/cloud_top_mean"][:])
    CT[np.where(CT<=0.0)] = np.nan
    data["cloud_top_mean"] = CT

    CB = np.array(les_data["timeseries/cloud_base_mean"][:])
    CB[np.where(CB>maxz)] = np.nan
    data["cloud_base_mean"] = CB

    data["ustar"] = np.array(les_data["timeseries/friction_velocity_mean"][:])
    data["shf"] = np.array(les_data["timeseries/shf_surface_mean"][:])
    data["lhf"] = np.array(les_data["timeseries/lhf_surface_mean"][:])
    data["lwp_mean"] = np.array(les_data["timeseries/lwp_mean"][:])
    data["rwp_mean"] = np.zeros_like(data["lwp_mean"]) #TODO - add rwp to les stats

    return data
