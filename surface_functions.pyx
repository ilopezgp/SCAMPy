import numpy as np
from thermodynamic_functions cimport latent_heat, pd_c, pv_c, sd_c, sv_c, cpm_c
include "parameters.pxi"




cdef inline double psi_m_unstable(double zeta, double zeta0):
    cdef double x = (1.0 - gamma_m * zeta)**0.25
    cdef double x0 = (1.0 - gamma_m * zeta0)**0.25
    cdef double psi_m = (2.0 * np.log((1.0 + x)/(1.0 + x0)) + np.log((1.0 + x*x)/(1.0 + x0 * x0))
                         -2.0 * np.arctan(x) + 2.0 * np.arctan(x0))
    return psi_m

cdef  inline double psi_h_unstable(double zeta, double zeta0):
    cdef double y = np.sqrt(1.0 - gamma_h * zeta )
    cdef double y0 = np.sqrt(1.0 - gamma_h * zeta0 )
    cdef double psi_h = 2.0 * np.log((1.0 + y)/(1.0 + y0))
    return psi_h


cdef inline double psi_m_stable(double zeta, double zeta0):
    cdef double psi_m = -beta_m * (zeta - zeta0)
    return  psi_m

cdef inline double psi_h_stable(double zeta, double zeta0):
    cdef double psi_h = -beta_h * (zeta - zeta0)
    return  psi_h



# The two below are fillers for putting in the full formulation

cpdef double entropy_flux(tflux,qtflux, p0_1, T_1, qt_1):
        cdef:
            double cp_1 = cpm_c(qt_1)
            double pd_1 = pd_c(p0_1, qt_1, qt_1)
            double pv_1 = pv_c(p0_1, qt_1, qt_1)
            double sd_1 = sd_c(pd_1, T_1)
            double sv_1 = sv_c(pv_1, T_1)
        return cp_1*tflux/T_1 + qtflux*(sv_1-sd_1)




cpdef double compute_ustar(double windspeed, double buoyancy_flux, double z0, double z1) :

    cdef:
        double lmo, zeta, zeta0, psi_m,ustar
        double ustar0, ustar1, ustar_new, f0, f1, delta_ustar
        double logz = np.log(z1 / z0)
    #use neutral condition as first guess
    ustar0 = windspeed * vkb / logz
    ustar = ustar0
    if (np.abs(buoyancy_flux) > 1.0e-20):
        lmo = -ustar0 * ustar0 * ustar0 / (buoyancy_flux * vkb)
        zeta = z1 / lmo
        zeta0 = z0 / lmo
        if (zeta >= 0.0):
            f0 = windspeed - ustar0 / vkb * (logz - psi_m_stable(zeta, zeta0))
            ustar1 = windspeed * vkb / (logz - psi_m_stable(zeta, zeta0))
            lmo = -ustar1 * ustar1 * ustar1 / (buoyancy_flux * vkb)
            zeta = z1 / lmo
            zeta0 = z0 / lmo
            f1 = windspeed - ustar1 / vkb * (logz - psi_m_stable(zeta, zeta0))
            ustar = ustar1
            delta_ustar = ustar1 -ustar0
            while np.abs(delta_ustar) > 1e-10:
                ustar_new = ustar1 - f1 * delta_ustar / (f1-f0)
                f0 = f1
                ustar0 = ustar1
                ustar1 = ustar_new
                lmo = -ustar1 * ustar1 * ustar1 / (buoyancy_flux * vkb)
                zeta = z1 / lmo
                zeta0 = z0 / lmo
                f1 = windspeed - ustar1 / vkb * (logz - psi_m_stable(zeta, zeta0))
                delta_ustar = ustar1 -ustar0
        else: # b_flux nonzero, zeta  is negative
            f0 = windspeed - ustar0 / vkb * (logz - psi_m_unstable(zeta, zeta0))
            ustar1 = windspeed * vkb / (logz - psi_m_unstable(zeta, zeta0))
            lmo = -ustar1 * ustar1 * ustar1 / (buoyancy_flux * vkb)
            zeta = z1 / lmo
            zeta0 = z0 / lmo
            f1 = windspeed - ustar1 / vkb * (logz - psi_m_unstable(zeta, zeta0))
            ustar = ustar1
            delta_ustar = ustar1 - ustar0
            while np.abs(delta_ustar) > 1e-10:
                ustar_new = ustar1 - f1 * delta_ustar / (f1 - f0)
                f0 = f1
                ustar0 = ustar1
                ustar1 = ustar_new
                lmo = -ustar1 * ustar1 * ustar1 / (buoyancy_flux * vkb)
                zeta = z1 / lmo
                zeta0 = z0 / lmo
                f1 = windspeed - ustar1 / vkb * (logz - psi_m_unstable(zeta, zeta0))
                delta_ustar = ustar1 - ustar


    return ustar
