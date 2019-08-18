import sys
sys.path.insert(0, "./")
sys.path.insert(0, "../")

import numpy as np

import matplotlib as mpl
mpl.use('Agg')  # To allow plotting when display is off
import matplotlib.pyplot as plt
from matplotlib import ticker

def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map"""

    # Taken from https://gist.github.com/jakevdp/91077b0cae40f8f8244a

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)


def plot_mean(data, les, tmin, tmax, folder="plots/output/Bomex/"):
    """
    Plots mean profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = len(data["t"])-1
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = len(les["t"])-1

    qv_mean = np.array(data["qt_mean"]) - np.array(data["ql_mean"])
    qv_mean_les = np.array(les["qt_mean"]) - np.array(les["ql_mean"])
    # data to plot x labels
    x_labels  =  [r'$q_{t} mean [\mathrm{g/kg}]$',
                  r'$q_{l} mean [\mathrm{g/kg}]$',
                  r'$q_{r} mean [\mathrm{g/kg}]$',
                  r'$q_{v} mean [\mathrm{g/kg}]$',
                  r'$\theta_{l} [\mathrm{K}]$',
                  r'$TKE [\mathrm{m^2/s^2}]$',
                  'u [m/s]',
                  'v [m/s]',
                  r'$\bar{w}_{upd} [\mathrm{m/s}]$',
                  r'$\bar{b}_{upd} [\mathrm{m/s^2}]$',
                  r'$\bar{q}_{l,env} [\mathrm{g/kg}]$',
                  r'$\bar{q}_{r,env} [\mathrm{g/kg}]$',
                  "updraft area [%]",
                  r'$\bar{q}_{l,env} [\mathrm{g/kg}]$',
                  r'$\bar{q}_{r,env} [\mathrm{g/kg}]$']

    fig_name  =  ["qt_mean",
                   "ql_mean",
                   "qr_mean",
                   "qr_mean",
                   "thetal_mean",
                   "TKE",
                   "u_mean",
                   "v_mean",
                   "updraft_w",
                   "updraft_buoyancy",
                   "updraft_ql",
                   "updraft_qr",
                   "updraft_area",
                   "env_ql",
                   "env_qr"]

    plot_x =     [data["qt_mean"],
                  data["ql_mean"],
                  data["qr_mean"],
                  qv_mean,
                  data["thetal_mean"],
                  data["tke_mean"],
                  data["u_mean"],
                  data["v_mean"],
                  data["updraft_w"],
                  data["updraft_buoyancy"],
                  data["updraft_ql"],
                  data["updraft_qr"],
                  data["updraft_area"],
                  data["env_ql"],
                  data["env_qr"]]

    plot_x_les = [les["qt_mean"],
                  les["ql_mean"],
                  les["qr_mean"],
                  qv_mean_les,
                  les["thetali_mean"],
                  les["tke_mean"],
                  les["u_translational_mean"],
                  les["v_translational_mean"],
                  les["updraft_w"],
                  les["updraft_buoyancy"],
                  les["updraft_ql"],
                  les["updraft_qr"],
                  les["updraft_fraction"],
                  les["env_ql"],
                  les["env_qr"] ]

    color  = ["navy", "darkorange"]
    label  = ["ini", "end"]

    # iteration over plots
    plots = []
    for plot_it in range(len(x_labels)):
        # customize defaults
        fig = plt.figure(fig_name[plot_it])
        fig.set_figheight(12)
        fig.set_figwidth(14)
        mpl.rcParams.update({'font.size': 18})
        mpl.rc('lines', linewidth=4, markersize=10)
                               #(rows, columns, number)
        plt.xlabel(x_labels[plot_it])
        plt.ylabel('z [m]')
        plt.ylim([0, data["z_half"][-1] + (data["z_half"][1] - data["z_half"][0]) * 0.5])
        plt.grid(True)
        plt.plot(np.nanmean(plot_x_les[plot_it][:,t_start_les:t_end_les],axis=1), les["z_half"], '-', color='k', label='les', linewidth = 2)
        plt.plot(np.nanmean(plot_x[plot_it][:,t_start:t_end],axis=1), data["z_half"], '-', color = '#157CC7', label='scm', linewidth = 2)

        plt.legend()
        plt.tight_layout()
        plt.savefig(folder + fig_name[plot_it]+".pdf")
        plt.clf()


def plot_drafts(data, les, tmin, tmax, title, folder="plots/output/"):
    """
    Plots updraft and environment profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])
    # customize defaults

    fig = plt.figure(1)
    fig.set_figheight(12)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)

    # read data
    qv_mean    = np.array(data["qt_mean"])    - np.array(data["ql_mean"])
    env_qv     = np.array(data["env_qt"])     - np.array(data["env_ql"])
    updraft_qv = np.array(data["updraft_qt"]) - np.array(data["updraft_ql"])

    # data to plot
    x_lab    = ["QV [g/kg]", "QL [g/kg]",        "QR [g/kg]",        "w [m/s]",         "updraft buoyancy [cm2/s3]",  "updraft area [%]"]
    plot_upd = [qv_mean,     data["updraft_ql"], data["updraft_qr"], data["updraft_w"], data["updraft_buoyancy"],     data["updraft_area"]]
    plot_env = [env_qv,      data["env_ql"],     data["env_qr"],     data["env_w"]]
    plot_mean= [updraft_qv,  data["ql_mean"],    data["qr_mean"]]

    qv_mean_les    = np.array(les["qt_mean"])    - np.array(les["ql_mean"])
    env_qv_les     = np.array(les["env_qt"])     - np.array(les["env_ql"])
    updraft_qv_les = np.array(les["updraft_qt"]) - np.array(les["updraft_ql"])
    les_plot_upd = [qv_mean_les,     les["updraft_ql"], les["updraft_qr"], les["updraft_w"], les["updraft_buoyancy"], les["updraft_fraction"] ]
    les_plot_env = [env_qv_les,      les["env_ql"],     les["env_qr"],     les["env_w"]]
    les_plot_mean= [updraft_qv_les,  les["ql_mean"],    les["qr_mean"]]

    # iteration over plots
    plots = []
    for plot_it in range(6):
        plots.append(plt.subplot(2,3,plot_it+1))
                               #(rows, columns, number)
        plots[plot_it].set_xlabel(x_lab[plot_it])
        plots[plot_it].set_ylabel('z [m]')
        plots[plot_it].set_ylim([0, data["z_half"][-1] + (data["z_half"][1] - data["z_half"][0]) * 0.5])
        plots[plot_it].grid(True)
        #plot updrafts
        if (plot_it != 5):
            plots[plot_it].plot(np.nanmean(les_plot_upd[plot_it][:,t_start:t_end],axis=1), les["z_half"], ':', color='gray', label='les upd', linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_upd[plot_it][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue", label="upd", linewidth = 2)
        if (plot_it == 5):
            plots[plot_it].plot(np.nanmean(les_plot_upd[plot_it][:,t_start:t_end],axis=1)* 100, les["z_half"], ':', color='gray', label='les upd', linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_upd[plot_it][:,t_start:t_end],axis=1) * 100, data["z_half"], "-", color="royalblue", label="upd", linewidth = 2)
        # plot environment
        if (plot_it < 4):
            plots[plot_it].plot(np.nanmean(les_plot_env[plot_it][:,t_start:t_end],axis=1), les["z_half"], '--', color='gray', label='les env', linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_env[plot_it][:,t_start:t_end],axis=1), data["z_half"], "-", color="darkred", label="env", linewidth = 2)
        # plot mean
        if (plot_it < 3):
            plots[plot_it].plot(np.nanmean(les_plot_upd[plot_it][:,t_start:t_end],axis=1), les["z_half"], '-', color='gray', label='les mean', linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_mean[plot_it][:,t_start:t_end],axis=1), data["z_half"], "-", color="purple", label="mean", linewidth = 2)

    plots[0].legend()
    plt.savefig(folder + title)
    plt.clf()


def plot_closures(data, les,tmin, tmax,  title, folder="plots/output/"):
    """
    Plots updraft and environment profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """

    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])
    # customize defaults

    fig = plt.figure(1)
    fig.set_figheight(12)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)
    nh_pressure = -np.multiply(les["updraft_fraction"],les["updraft_ddz_p_alpha"])

    # data to plot
    x_lab    =  ["eddy_diffusivity",        "mixing_length_ratio",         "mixing_length",         "nonhydro_pressure",      "turbulent_entrainment",         "entrainment",             "detrainment"        ]
    plot_vars = [data["eddy_diffusivity"]   ,data["mixing_length_ratio"],  data["mixing_length"],   data["nh_pressure"],       data["turbulent_entrainment"],  data["entrainment_sc"],    data["detrainment_sc"]]
    xmax = np.max(data["detrainment_sc"])
    if xmax == 0.0:
        xmax = np.max(data["entrainment_sc"])
    # iteration over plots
    plots = []
    for plot_it in range(6):
        plots.append(plt.subplot(2,3,plot_it+1))
                               #(rows, columns, number)
        plots[plot_it].set_ylabel('z [m]')
        plots[plot_it].set_ylim([0, data["z_half"][-1] + (data["z_half"][1] - data["z_half"][0]) * 0.5])
        plots[plot_it].grid(True)
        #plot updrafts
        if (plot_it < 5):
            if x_lab[plot_it] =="nonhydro_pressure":
                plots[plot_it].plot(np.multiply(les["rho"],np.nanmean(nh_pressure[:,t_start_les:t_end_les],axis=1)), les["z_half"], "-", color="gray", linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_vars[plot_it][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue", linewidth = 2)
            plots[plot_it].set_xlabel(x_lab[plot_it])
        if (plot_it == 5):
            plots[plot_it].plot(np.nanmean(plot_vars[5][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue", label="entr", linewidth = 2)
            plots[plot_it].plot(np.nanmean(plot_vars[6][:,t_start:t_end],axis=1), data["z_half"], "-", color="darkorange", label="detr", linewidth = 2)
            plots[plot_it].set_xlabel("entr/detr")
            plots[5].set_xlim([-0.1*xmax, xmax])
            plots[5].legend()

    plt.savefig(folder + title)
    plt.clf()


def plot_velocities(data, les, tmin, tmax, title, folder="plots/output/"):
    """
    Plots updraft and environment profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """

    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])

    fig = plt.figure(1)
    fig.set_figheight(12)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)
    plt.subplot(1,2,1)
    plt.plot(np.nanmean(les["u_translational_mean"][:,t_start:t_end],axis = 1), les["z_half"], color='gray', label='les upd', linewidth = 4)
    plt.plot(np.nanmean(data["u_mean"][:,t_start:t_end],axis = 1),data["z_half"], color="royalblue", label="scm", linewidth = 2)
    plt.xlabel('u [m/s]')
    plt.ylabel('z [m]')
    plt.subplot(1,2,2)
    plt.plot(np.nanmean(les["v_translational_mean"][:,t_start:t_end],axis=1) , les["z_half"],  color='gray', label='les upd', linewidth = 4)
    plt.plot(np.nanmean(data["v_mean"][:,t_start:t_end],axis=1) ,data["z_half"],  color="royalblue", label="scm", linewidth = 2)
    plt.xlabel('v [m/s]')
    plt.savefig(folder + title)
    plt.clf()

def plot_main(data, les,tmin, tmax, title,  folder="plots/output/"):
    """
    Plots updraft and environment profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    # customize defaults
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])

    fig = plt.figure(1)
    fig.set_figheight(12)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)

    # data to plot
    x_lab    =  ["qt_mean",        "ql_mean",         "thetal_mean",         "updraft_w",        "updraft_area"]
    plot_vars = [data["qt_mean"]   ,data["ql_mean"],  data["thetal_mean"],   data["updraft_w"],  data["updraft_area"]]
    plot_x_les = [les["qt_mean"],      les["ql_mean"],  les["thetali_mean"], les["updraft_w"],  les["updraft_fraction"]]
    xmax = 5*np.max(np.nanmean(data["entrainment_sc"][3:,t_start:t_end],axis=1))
    # xmax = 1e-2
    # iteration over plots
    plots = []
    for plot_it in range(6):
        plots.append(plt.subplot(2,3,plot_it+1))
                               #(rows, columns, number)
        plots[plot_it].set_ylabel('z [m]')
        plots[plot_it].grid(True)
        if plot_it<5:
            plots[plot_it].plot(np.nanmean(plot_x_les[plot_it][:,t_start_les:t_end_les],axis=1), les["z_half"], '-', color='gray', label='les', linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_vars[plot_it][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue", label='les', linewidth = 2)
            plots[plot_it].set_xlabel(x_lab[plot_it])
            plots[plot_it].set_ylim([0, np.max(data["z_half"])])

        else:
            plots[plot_it].plot(np.nanmean(data["entrainment_sc"][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue",  label="d. entr", linewidth = 2)
            plots[plot_it].plot(np.nanmean(data["detrainment_sc"][:,t_start:t_end],axis=1), data["z_half"], "-", color="darkorange", label="d. detr", linewidth = 2)
            plots[plot_it].plot(np.add(np.nanmean(data["entrainment_sc"][:,t_start:t_end],axis=1),np.nanmean(data["turbulent_entrainment"][:,t_start:t_end],axis=1)), data["z_half"], "--", color="royalblue",  label="tot entr", linewidth = 2)
            plots[plot_it].plot(np.add(np.nanmean(data["detrainment_sc"][:,t_start:t_end],axis=1),np.nanmean(data["turbulent_entrainment"][:,t_start:t_end],axis=1)), data["z_half"], "--", color="darkorange", label="tot detr", linewidth = 2)
            plots[plot_it].set_xlabel('entr detr [1/m]')
            # plots[plot_it].set_xlim([-1e-4, xmax])
            plots[plot_it].set_xlim([-1e-4, xmax])
            plots[plot_it].set_ylim([0, np.max(data["z_half"])])
            plots[plot_it].legend()

    plt.savefig(folder + title)
    plt.clf()

def plot_tke_components(data, les,tmin, tmax, title,  folder="plots/output/"):
    """
    Plots updraft and environment profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    # customize defaults
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])

    fig = plt.figure(1)
    fig.set_figheight(12)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)

    # data to plot
    x_lab    =  ["tke_advection","tke_buoy","tke_dissipation","tke_pressure","tke_transport","tke_shear"]
    # ["tke_entr_gain","tke_detr_loss","tke_interdomain"]
    plot_vars =  [data["tke_advection"], data["tke_buoy"],  data["tke_dissipation"], data["tke_pressure"],  data["tke_transport"], data["tke_shear"]]
    plot_x_les = [les["tke_prod_A"],     les["tke_prod_B"], les["tke_prod_D"]      , les["tke_prod_P"],     les["tke_prod_T"],     les["tke_prod_S"]]
    xmax = 5*np.max(np.nanmean(data["tke_entr_gain"][3:,t_start:t_end],axis=1))
    # xmax = 1e-2
    # iteration over plots
    plots = []
    for plot_it in range(6):
        plots.append(plt.subplot(2,3,plot_it+1))
                               #(rows, columns, number)
        plots[plot_it].set_ylabel('z [m]')
        plots[plot_it].grid(True)
        if plot_it<6:
            plots[plot_it].plot(np.nanmean(plot_x_les[plot_it][:,t_start_les:t_end_les],axis=1), les["z_half"], '-', color='gray', label='les', linewidth = 4)
            plots[plot_it].plot(np.nanmean(plot_vars[plot_it][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue", label='les', linewidth = 2)
            plots[plot_it].set_xlabel(x_lab[plot_it])
            plots[plot_it].set_ylim([0, np.max(data["z_half"])])

        else:
            plots[plot_it].plot(np.nanmean(data["tke_entr_gain"][:,t_start:t_end],axis=1), data["z_half"], "-", color="royalblue",  label="tke entr", linewidth = 2)
            plots[plot_it].plot(np.nanmean(data["tke_detr_loss"][:,t_start:t_end],axis=1), data["z_half"], "-", color="darkorange", label="tke detr", linewidth = 2)
            plots[plot_it].set_xlabel('tke entr detr [1/m]')
            # plots[plot_it].set_xlim([-1e-4, xmax])
            plots[plot_it].set_xlim([-1e-4, xmax])
            plots[plot_it].set_ylim([0, np.max(data["z_half"])])
            plots[plot_it].legend()

    plt.savefig(folder + title)
    plt.clf()

def plot_tke_breakdown(data, les,tmin, tmax, title,  folder="plots/output/"):
    """
    Plots updraft and environment profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    # customize defaults
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])

    ig = plt.figure(1)
    plt.subplot(121)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)
    # plt.plot(np.nanmean(data["tke_mean"][:,t_start:t_end],axis=1),        data["z_half"], "-", color="gray",       label="tke_mean",        linewidth = 4)
    plt.plot(np.nanmean(data["tke_advection"][:,t_start:t_end],axis=1),   data["z_half"], "-", color="royalblue",  label="tke_advection",   linewidth = 2)
    plt.plot(np.nanmean(data["tke_buoy"][:,t_start:t_end],axis=1),        data["z_half"], "-", color="darkorange", label="tke_buoy",        linewidth = 2)
    plt.plot(np.nanmean(data["tke_dissipation"][:,t_start:t_end],axis=1), data["z_half"], "-", color="k",          label="tke_dissipation", linewidth = 2)
    plt.plot(np.nanmean(data["tke_pressure"][:,t_start:t_end],axis=1),    data["z_half"], "-", color="darkgreen",  label="tke_pressure",    linewidth = 2)
    plt.plot(np.nanmean(data["tke_transport"][:,t_start:t_end],axis=1),   data["z_half"], "-", color="red",        label="tke_transport",   linewidth = 2)
    plt.plot(np.nanmean(data["tke_shear"][:,t_start:t_end],axis=1),       data["z_half"], "-", color="purple",     label="tke_shear",       linewidth = 2)
    plt.xlabel('tke componenets scm')
    plt.legend()
    plt.ylim([0, np.max(data["z_half"])])
    plt.subplot(122)
    mpl.rcParams.update({'font.size': 18})
    mpl.rc('lines', linewidth=4, markersize=10)
    # plt.plot(np.nanmean(les["tke_mean"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-", color="gray",       label="tke_mean", linewidth = 4)
    plt.plot(np.nanmean(les["tke_prod_A"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-",    color="royalblue",  label="tke_A",    linewidth = 2)
    plt.plot(np.nanmean(les["tke_prod_B"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-",    color="darkorange", label="tke_B",    linewidth = 2)
    plt.plot(np.nanmean(les["tke_prod_D"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-",    color="k",          label="tke_D",    linewidth = 2)
    plt.plot(np.nanmean(les["tke_prod_P"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-",    color="darkgreen",  label="tke_P",    linewidth = 2)
    plt.plot(np.nanmean(les["tke_prod_T"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-",    color="red",        label="tke_T",    linewidth = 2)
    plt.plot(np.nanmean(les["tke_prod_S"][:,t_start_les:t_end_les],axis=1), les["z_half"], "-",    color="purple",     label="tke_S",    linewidth = 2)
    plt.xlabel('tke componenets les')
    plt.ylim([0, np.max(les["z_half"])])
    plt.savefig(folder + title)
    plt.clf()

def plot_var_covar_mean(data, les, tmin, tmax, title, folder="plots/output/"):
    """
    Plots variance and covariance profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    t_start_les = int(np.where(les["t"] > tmin)[0][0])
    t_start_les = 0
    t_end_les   = int(np.where(les["t"] <= tmax)[0][0])
    t_end_les   = int(np.where(les["t"] == les["t"][-1] )[0][0])
    # customize defaults
    fig = plt.figure(1)
    fig.set_figheight(8)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 16})
    mpl.rc('lines', linewidth=4, markersize=10)

    # data to plot
    x_lab         = ["Hvar",       "QTvar",       "HQTcov"]
    plot_var_mean = ["Hvar_mean",  "QTvar_mean",  "HQTcov_mean"]
    plot_var_env  = ["env_Hvar",   "env_QTvar",   "env_HQTcov"]

    # iteration over plots
    plots = []
    for plot_it in range(3):
        plots.append(plt.subplot(1,3,plot_it+1))
                               #(rows, columns, number)
        plots[plot_it].set_xlabel(x_lab[plot_it])
        plots[plot_it].set_ylabel('z [m]')
        plots[plot_it].set_ylim([0, data["z_half"][-1] + (data["z_half"][1] - data["z_half"][0]) * 0.5])
        plots[plot_it].grid(True)
        plots[plot_it].xaxis.set_major_locator(ticker.MaxNLocator(2))

        plots[plot_it].plot(np.nanmean(les[plot_var_env[plot_it]][:,t_start_les:t_end_les],axis=1),   les["z_half"],  "-", label= '_les',              c="gray",linewidth = 4)
        plots[plot_it].plot(np.nanmean(data[plot_var_mean[plot_it]][:,t_start:t_end],axis=1), data["z_half"], "-", label= plot_var_mean[plot_it], c="crimson", linewidth = 2)
        plots[plot_it].plot(np.nanmean(data[plot_var_env[plot_it]][:,t_start:t_end],axis=1),  data["z_half"], "-", label= plot_var_env[plot_it],  c="forestgreen", linewidth = 2)

    plots[0].legend()
    plt.tight_layout()
    plt.savefig(folder + title)
    plt.clf()


def plot_var_covar_components(data, tmin, tmax, title, folder="plots/output/"):
    """
    Plots variance and covariance components profiles from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    if tmax==-1:
        tmax = np.max(data["t"])
    else:
        tmax = tmax*3600.0
    tmin = tmin*3600.0
    t_start = int(np.where(data["t"] > tmin)[0][0])
    t_start = 0
    t_end   = int(np.where(data["t"] <= tmax)[0][0])
    t_end   = int(np.where(data["t"]  == data["t"][-1] )[0][0])
    # customize defaults
    fig = plt.figure(1)
    fig.set_figheight(8)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 16})
    mpl.rc('lines', linewidth=4, markersize=10)

    # data to plot
    plot_Hvar_c   = ["Hvar_dissipation",   "Hvar_entr_gain",   "Hvar_detr_loss",   "Hvar_shear",   "Hvar_rain"]
    plot_QTvar_c  = ["QTvar_dissipation",  "QTvar_entr_gain",  "QTvar_detr_loss",  "QTvar_shear",  "QTvar_rain"]
    plot_HQTcov_c = ["HQTcov_dissipation", "HQTcov_entr_gain", "HQTcov_detr_loss", "HQTcov_shear", "HQTcov_rain"]
    color_c       = ['darkgreen',              'purple',             'purple',           'darkorange',       'royalblue']

    x_lab         = ["Hvar",      "QTvar",      "HQTcov"]
    plot_var_data = [plot_Hvar_c, plot_QTvar_c, plot_HQTcov_c]

    # iteration over plots
    plots = []
    for plot_it in range(3):
        plots.append(plt.subplot(1,3,plot_it+1))
                               #(rows, columns, number)
        plots[plot_it].set_xlabel(x_lab[plot_it])
        plots[plot_it].set_ylabel('z [m]')
        plots[plot_it].set_ylim([0, data["z_half"][-1] + (data["z_half"][1] - data["z_half"][0]) * 0.5])
        plots[plot_it].grid(True)
        plots[plot_it].xaxis.set_major_locator(ticker.MaxNLocator(2))

        for var in range(5):
            plots[plot_it].plot(np.nanmean(data[plot_var_data[plot_it][var]][:,t_start:t_end],axis=1),   data["z_half"], "-", label=plot_Hvar_c[var],  c=color_c[var])

    plots[0].legend()
    plt.tight_layout()
    plt.savefig(folder + title)
    plt.clf()


def plot_timeseries_1D(data,  les, title, folder="plots/output/"):
    """
    Plots timeseries from Scampy

    Input:
    data   - dictionary with previousely read it data
    title  - name for the created plot
    folder - folder where to save the created plot
    """
    # customize defaults
    fig = plt.figure(1)
    fig.set_figheight(8)
    fig.set_figwidth(14)
    mpl.rcParams.update({'font.size': 12})
    mpl.rc('lines', linewidth=2, markersize=6)

    # data to plot
    plot_y     = [data["updraft_cloud_cover"],  data["lwp"], data["lhf"], data["shf"], data["rd"],      data["updraft_cloud_top"], data["updraft_cloud_base"]]
    plot_les_y = [les["updraft_cloud_cover"],   les["lwp"],  les["lhf"],  les["shf"],  les["shf"],  les["updraft_cloud_top"],  les["updraft_cloud_base"]]
    y_lab  =     ['updr cl. cover',                 'lwp',       'lhf',       'shf',       'rd [m]',                      'updr CB, CT']

    # iteration over plots
    plots = []
    for plot_it in range(6):
        plots.append(plt.subplot(2,3,plot_it+1))
                               #(rows, columns, number)
        if plot_it < 4:
            plots[plot_it].set_xlabel('t [s]')
            plots[plot_it].set_ylabel(y_lab[plot_it])
            plots[plot_it].set_xlim([0, data["t"][-1]])
            plots[plot_it].grid(True)
            plots[plot_it].plot(les["t"][1:] , plot_les_y[plot_it][1:], '-', color="gray",linewidth = 4)
            plots[plot_it].plot(data["t"][1:], plot_y[plot_it][1:], '-', color="b")
            plots[plot_it].legend()
        elif plot_it == 4:
            plots[plot_it].set_xlabel('t [s]')
            plots[plot_it].set_ylabel(y_lab[plot_it])
            plots[plot_it].set_xlim([0, data["t"][-1]])
            plots[plot_it].grid(True)
            plots[plot_it].plot(data["t"][1:], plot_y[plot_it][1:], '-', color="b")
            plots[plot_it].legend()
        else:
            plots[5].set_xlabel('t [s]')
            plots[5].set_ylabel(y_lab[5])
            plots[5].set_xlim([0, data["t"][-1]])
            plots[5].grid(True)
            plots[5].plot(les["t"][1:], les["updraft_cloud_base"][1:], '-', color="gray",   label="CB_les",  linewidth = 4)
            plots[5].plot(les["t"][1:], les["updraft_cloud_top"][1:],  '-', color="gray",   label="CT_les",  linewidth = 4)
            plots[5].plot(data["t"][1:], data["updraft_cloud_base"][1:], '-', color="crimson", label="CB",  linewidth = 2)
            plots[5].plot(data["t"][1:], data["updraft_cloud_top"][1:],  '-', color="royalblue", label="CT",  linewidth = 2)

    plt.tight_layout()
    plt.savefig(folder + title)
    plt.clf()


    # fig = plt.figure(1)
    # fig.set_figheight(8)
    # fig.set_figwidth(14)
    # mpl.rcParams.update({'font.size': 12})
    # mpl.rc('lines', linewidth=2, markersize=6)

    # # data to plot
    # plot_y     = [data["updraft_cloud_cover"],  data["lwp"], data["lhf"], data["shf"], data["rd"],      data["updraft_cloud_top"], data["updraft_cloud_base"]]
    # plot_les_y = [les["updraft_cloud_cover"],   les["lwp"],  les["lhf"],  les["shf"],  les["shf"],  les["updraft_cloud_top"],  les["updraft_cloud_base"]]
    # y_lab  =     ['updr cl. cover',                 'lwp',       'lhf',       'shf',       'rd [m]',                      'updr CB, CT']

    # # iteration over plots
    # plots = []
    # for plot_it in range(np.shape(plot_y)):
    #     plots[plot_it].set_xlabel('t [s]')
    #     plots[plot_it].set_ylabel(y_lab[plot_it])
    #     plots[plot_it].set_xlim([0, data["t"][-1]])
    #     plots[plot_it].grid(True)
    #     plots[plot_it].plot(les["t"][1:] , plot_les_y[plot_it][1:], '-', color="gray",linewidth = 4)
    #     plots[plot_it].plot(data["t"][1:], plot_y[plot_it][1:], '-', color="b")
    #     plots[plot_it].legend()
    #     elif plot_it == 4:
    #         plots[plot_it].set_xlabel('t [s]')
    #         plots[plot_it].set_ylabel(y_lab[plot_it])
    #         plots[plot_it].set_xlim([0, data["t"][-1]])
    #         plots[plot_it].grid(True)
    #         plots[plot_it].plot(data["t"][1:], plot_y[plot_it][1:], '-', color="b")
    #         plots[plot_it].legend()
    #     else:
    #         plots[5].set_xlabel('t [s]')
    #         plots[5].set_ylabel(y_lab[5])
    #         plots[5].set_xlim([0, data["t"][-1]])
    #         plots[5].grid(True)
    #         plots[5].plot(les["t"][1:], les["updraft_cloud_base"][1:], '-', color="gray",   label="CB_les",  linewidth = 4)
    #         plots[5].plot(les["t"][1:], les["updraft_cloud_top"][1:],  '-', color="gray",   label="CT_les",  linewidth = 4)
    #         plots[5].plot(data["t"][1:], data["updraft_cloud_base"][1:], '-', color="crimson", label="CB",  linewidth = 2)
    #         plots[5].plot(data["t"][1:], data["updraft_cloud_top"][1:],  '-', color="royalblue", label="CT",  linewidth = 2)

    # plt.tight_layout()
    # plt.savefig(folder + title)
    # plt.clf()



def plot_timeseries(data,  les, folder="plots/output/"):
    """
    Plots the time series of Scampy simulations

    Input:
    data   - dictionary with previousely read it data
    case   - name for the tested simulation (to be used in the plot name)
    folder - folder where to save the created plot
    """
    # customize figure parameters
    # read data
    z_half    = data["z_half"]
    time      = data["t"] / 60. / 60.
    data["qv_mean"]  = data["qt_mean"]    - data["ql_mean"]
    data["updr_qv"] = data["updraft_qt"] - data["updraft_ql"]
    data["env_qv"]  = data["env_qt"]     - data["env_ql"]

    les_z_half     = les["z_half"]
    les_time       = les["t"] / 60. / 60.
    les["qv_mean"] = les["qt_mean"]     - les["ql_mean"]
    les["upd_qv"]  = les["updraft_qt"]  - les["updraft_ql"]
    les["env_qv"]  = les["env_qt"]      - les["env_ql"]

    # data to plot "qt_mean",
    les_vars  = ["thetali_mean", "tke_mean", "qv_mean", "ql_mean", "qr_mean", "qt_mean", "env_thetali", "env_w", "env_qt", "env_ql","env_qr",
                 "updraft_thetali", "updraft_fraction", "updraft_buoyancy", "updraft_w", "updraft_qt", "updraft_ql","updraft_qr",
                 "massflux_h", "diffusive_flux_h", "total_flux_h", "massflux_qt", "diffusive_flux_qt", "total_flux_qt"]

    scm_vars  = ["thetal_mean", "tke_mean", "qv_mean", "ql_mean", "qr_mean", "qt_mean", "env_thetal", "env_w", "env_qt", "env_ql", "env_qr",
                 "updraft_thetal", "updraft_area", "updraft_buoyancy", "updraft_w", "updraft_qt", "updraft_ql", "updraft_qr",
                 "massflux_h", "diffusive_flux_h", "total_flux_h", "massflux_qt", "diffusive_flux_qt", "total_flux_qt"]

    labels    = ["mean thl [K]", "mean TKE [m2/s2]", "mean qv [g/kg]", "mean ql [g/kg]", "mean qr [g/kg]", "mean qt [g/kg]", "env thl [K]", "env w [m/s]",
                 "env qt [g/kg]", "env ql [g/kg]", "env qr [g/kg]", "updr thl [K]", "updr area [%]", "updr buoyancy [m/s^2]", "updr w [m/s]",
                 "updr qt [g/kg]", "updr ql [g/kg]", "updr qr [g/kg", "massflux_h [kg*K/ms^2]", "diffusive_flux_h [kg*K/ms^2]", "total_flux_h [kg*K/ms^2]",
                 "massflux_qt [g*/ms^2]", "diffusive_flux_qt [g*/ms^2]", "total_flux_qt [g*/ms^2]"]

    fig_name =  ["contour_thl_mean", "contour_TKE_mean", "contour_qv_mean", "contour_ql_mean", "contour_qr_mean", "contour_qt_mean", "contour_env_thl", "contour_env_w",
                 "contour_env_qt", "contour_env_ql", "contour_env_qr", "contour_upd_thl", "contour_upd_area", "contour_upd_buoyancy", "contour_upd_w", "contour_upd_qt",
                 "contour_upd_ql", "contour_upd_qr", "contour_massflux_h", "contour_diffusive_flux_h", "contour_total_flux_h", "contour_massflux_qt", "contour_diffusive_flux_qt",
                 "contour_total_flux_qt]"]

    # iteration over plots
    plots = []
    for plot_it in range(len(labels)):
        fig = plt.figure(fig_name[plot_it])
        if scm_vars[plot_it]=="env_thetal":
            data[scm_vars[plot_it]][:,0] = data[scm_vars[plot_it]][:,1]
        scm_field = np.multiply(data[scm_vars[plot_it]],1.0)
        les_field = np.multiply(les[les_vars[plot_it]],1.0)
        a_scm = np.multiply(data['updraft_area'],1.0)
        a_les = np.multiply(les['updraft_fraction'],1.0)
        if ("updraft" in scm_vars[plot_it]):
            scm_field[np.where(a_scm==0.0)] = np.nan
            scm_field[np.where(np.isnan(a_scm))] = np.nan

        if ("updraft" in les_vars[plot_it]):
            les_field[np.where(a_les==0.0)] = np.nan
            les_field[np.where(np.isnan(a_les))] = np.nan
        plt.subplot(211)
        plt.ylabel('z [m]')
        plt.contourf(les_time, les_z_half, les_field, cmap='RdBu_r')
        plt.colorbar()
        plt.subplot(212)
        plt.xlabel('t [h]')
        plt.ylabel('z [m]')
        plt.contourf(time, z_half, scm_field, cmap='RdBu_r')
        plt.colorbar()
        plt.savefig(folder + fig_name[plot_it]+".pdf")
        plt.clf()
        plt.close()