#!python
#cython: boundscheck=True
#cython: wraparound=False
#cython: initializedcheck=True
#cython: cdivision=False

import numpy as np
include "parameters.pxi"
include "parameters_edmf.pxi"
from thermodynamic_functions cimport  *
# eos_struct, eos, t_to_entropy_c, t_to_thetali_c, eos_first_guess_thetal, \
# eos_first_guess_entropy, alpha_c, buoyancy_c, latent_heat


import cython
cimport Grid
cimport ReferenceState
from Variables cimport GridMeanVariables
from NetCDFIO cimport NetCDFIO_Stats
from libc.math cimport fmax
import pylab as plt


cdef class UpdraftVariable:
    def __init__(self, nu, nz, loc, kind, name, units):
        self.values = np.zeros((nu,nz),dtype=np.double, order='c')
        self.tendencies = np.zeros((nu,nz),dtype=np.double, order='c')
        self.flux = np.zeros((nu,nz),dtype=np.double, order='c')
        self.bulkvalues = np.zeros((nz,), dtype=np.double, order = 'c')
        if loc != 'half' and loc != 'full':
            print('Invalid location setting for variable! Must be half or full')
        self.loc = loc
        if kind != 'scalar' and kind != 'velocity':
            print ('Invalid kind setting for variable! Must be scalar or velocity')
        self.kind = kind
        self.name = name
        self.units = units

    cpdef set_bcs(self,Grid.Grid Gr):
        # cdef:
        #     Py_ssize_t i,k
        #     Py_ssize_t start_low = Gr.gw - 1
        #     Py_ssize_t start_high = Gr.nzg - Gr.gw - 1
        #
        # n_updrafts = np.shape(self.values)[0]
        #
        # if self.name == 'w':
        #     for i in xrange(n_updrafts):
        #         self.values[i,start_high] = 0.0
        #         self.values[i,start_low] = 0.0
        #         for k in xrange(1,Gr.gw):
        #             self.values[i,start_high+ k] = -self.values[i,start_high - k ]
        #             self.values[i,start_low- k] = -self.values[i,start_low + k  ]
        # else:
        #     for k in xrange(Gr.gw):
        #         for i in xrange(n_updrafts):
        #             self.values[i,start_high + k +1] = self.values[i,start_high  - k]
        #             self.values[i,start_low - k] = self.values[i,start_low + 1 + k]

        return




cdef class UpdraftVariables:
    def __init__(self, nu, namelist, Grid.Grid Gr):
        self.Gr = Gr
        self.n_updrafts = nu
        cdef:
            Py_ssize_t nzg = Gr.nzg
            Py_ssize_t i, k

        self.W = UpdraftVariable(nu, nzg, 'full', 'velocity', 'w','m/s' )
        self.Area = UpdraftVariable(nu, nzg, 'full', 'scalar', 'area_fraction','[-]' )
        self.QT = UpdraftVariable(nu, nzg, 'half', 'scalar', 'qt','kg/kg' )
        self.QL = UpdraftVariable(nu, nzg, 'half', 'scalar', 'ql','kg/kg' )
        if namelist['thermodynamics']['thermal_variable'] == 'entropy':
            self.H = UpdraftVariable(nu, nzg, 'half', 'scalar', 's','J/kg/K' )
        elif namelist['thermodynamics']['thermal_variable'] == 'thetal':
            self.H = UpdraftVariable(nu, nzg, 'half', 'scalar', 'thetal','K' )

        self.T = UpdraftVariable(nu, nzg, 'half', 'scalar', 'temperature','K' )
        self.B = UpdraftVariable(nu, nzg, 'half', 'scalar', 'buoyancy','m^2/s^3' )

        return

    cpdef initialize(self, GridMeanVariables GMV):
        cdef:
            Py_ssize_t i,k


        with nogil:
            for k in xrange(self.Gr.nzg):
                for i in xrange(self.n_updrafts):
                    self.W.values[i,k] = 0.0
                    self.Area.values[i,k] = 0.1
                    self.QT.values[i,k] = GMV.QT.values[k]
                    self.QL.values[i,k] = GMV.QL.values[k]
                    self.H.values[i,k] = GMV.H.values[k]
                    self.T.values[i,k] = GMV.T.values[k]
                    self.B.values[i,k] = GMV.B.values[k]

        return

    cpdef initialize_io(self, NetCDFIO_Stats Stats):
        Stats.add_profile('updraft_area')
        Stats.add_profile('updraft_w')
        Stats.add_profile('updraft_qt')
        Stats.add_profile('updraft_ql')
        if self.H.name == 'thetal':
            Stats.add_profile('updraft_thetal')
        else:
            Stats.add_profile('updraft_thetal')
            Stats.add_profile('updraft_s')
        Stats.add_profile('updraft_temperature')
        Stats.add_profile('updraft_buoyancy')

        return

    cpdef set_means(self, GridMeanVariables GMV):

        cdef:
            Py_ssize_t i, k

        self.Area.bulkvalues = np.sum(self.Area.values,axis=0)
        self.W.bulkvalues[:] = 0.0
        self.QT.bulkvalues[:] = 0.0
        self.QL.bulkvalues[:] = 0.0
        self.H.bulkvalues[:] = 0.0
        self.T.bulkvalues[:] = 0.0
        self.B.bulkvalues[:] = 0.0


        with nogil:
            for k in xrange(self.Gr.gw, self.Gr.nzg-self.Gr.gw):
                if self.Area.bulkvalues[k] > 1.0e-3:
                    for i in xrange(self.n_updrafts):
                        self.QT.bulkvalues[k] += self.Area.values[i,k] * self.QT.values[i,k]/self.Area.bulkvalues[k]
                        self.QL.bulkvalues[k] += self.Area.values[i,k] * self.QL.values[i,k]/self.Area.bulkvalues[k]
                        self.H.bulkvalues[k] += self.Area.values[i,k] * self.H.values[i,k]/self.Area.bulkvalues[k]
                        self.T.bulkvalues[k] += self.Area.values[i,k] * self.T.values[i,k]/self.Area.bulkvalues[k]
                        self.B.bulkvalues[k] += self.Area.values[i,k] * self.B.values[i,k]/self.Area.bulkvalues[k]
                        self.W.bulkvalues[k] += ((self.Area.values[i,k] + self.Area.values[i,k+1]) * self.W.values[i,k]
                                            /(self.Area.bulkvalues[k] + self.Area.bulkvalues[k+1]))
                else:
                    self.QT.bulkvalues[k] = GMV.QT.values[k]
                    self.QL.bulkvalues[k] = GMV.QL.values[k]
                    self.H.bulkvalues[k] = GMV.H.values[k]
                    self.T.bulkvalues[k] = GMV.T.values[k]
                    self.B.bulkvalues[k] = GMV.B.values[k]
                    self.W.bulkvalues[k] = 0.0

        return

    cpdef io(self, NetCDFIO_Stats Stats):
        Stats.write_profile('updraft_area', self.Area.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        Stats.write_profile('updraft_w', self.W.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        Stats.write_profile('updraft_qt', self.QT.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        Stats.write_profile('updraft_ql', self.QL.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        if self.H.name == 'thetal':
            Stats.write_profile('updraft_thetal', self.H.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        else:
            Stats.write_profile('updraft_s', self.H.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
            Stats.write_profile('updraft_thetal', self.THL.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        Stats.write_profile('updraft_temperature', self.T.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])
        Stats.write_profile('updraft_buoyancy', self.B.bulkvalues[self.Gr.gw:self.Gr.nzg-self.Gr.gw])

        return

cdef class UpdraftThermodynamics:
    def __init__(self, n_updraft, Grid.Grid Gr, ReferenceState.ReferenceState Ref, UpdraftVariables UpdVar):
        self.Gr = Gr
        self.Ref = Ref
        self.n_updraft = n_updraft
        if UpdVar.H.name == 's':
            self.t_to_prog_fp = t_to_entropy_c
            self.prog_to_t_fp = eos_first_guess_entropy
        elif UpdVar.H.name == 'thetal':
            self.t_to_prog_fp = t_to_thetali_c
            self.prog_to_t_fp = eos_first_guess_thetal

        return
    cpdef satadjust(self, UpdraftVariables UpdVar):
        #Update T, QL
        cdef:
            Py_ssize_t k, i
            eos_struct sa

        with nogil:
            for i in xrange(self.n_updraft):
                for k in xrange(self.Gr.nzg):
                    sa = eos(self.t_to_prog_fp,self.prog_to_t_fp, self.Ref.p0_half[k],
                             UpdVar.QT.values[i,k], UpdVar.H.values[i,k])
                    UpdVar.QL.values[i,k] = sa.ql
                    UpdVar.T.values[i,k] = sa.T
        return

    cpdef buoyancy(self,  UpdraftVariables UpdVar, GridMeanVariables GMV):
        cdef:
            Py_ssize_t k, i
            double alpha, qv


        with nogil:
            for i in xrange(self.n_updraft):
                for k in xrange(self.Gr.nzg):
                    qv = UpdVar.QT.values[i,k] - UpdVar.QL.values[i,k]
                    alpha = alpha_c(self.Ref.p0_half[k], UpdVar.T.values[i,k], UpdVar.QT.values[i,k], qv)
                    UpdVar.B.values[i,k] = buoyancy_c(self.Ref.alpha0_half[k], alpha) - GMV.B.values[k]
        return



cdef class UpdraftMicrophysics:
    def __init__(self, n_updraft, Grid.Grid Gr, ReferenceState.ReferenceState Ref):
        self.Gr = Gr
        self.Ref = Ref
        self.n_updraft = n_updraft
        self.f_prec = 0.02 # precipitation conversion fraction
        self.prec_source_h = np.zeros((n_updraft, Gr.nzg), dtype=np.double, order='c')
        self.prec_source_qt = np.zeros((n_updraft, Gr.nzg), dtype=np.double, order='c')
        self.prec_source_h_tot = np.zeros((Gr.nzg,), dtype=np.double, order='c')
        self.prec_source_qt_tot = np.zeros((Gr.nzg,), dtype=np.double, order='c')
        return
    cpdef compute_sources(self, UpdraftVariables UpdVar):
        cdef:
            Py_ssize_t k, i
            double psat, qsat, lh

        # with nogil:
        #     for i in xrange(self.n_updraft):
        #         for k in xrange(self.Gr.nzg):
        #             lh = latent_heat(UpdVar.T.values[i,k])
        #             psat = pv_star(UpdVar.T.values[i,k])
        #             qsat = qv_star_c(self.Ref.p0_half[k], UpdVar.QT.values[i,k], psat)
        #
        #             self.prec_source_qt[i,k] = -fmax(0.0, UpdVar.QL.values[i,k] - self.f_prec*qsat )
        #             self.prec_source_h[i,k] = -self.prec_source_qt[i,k] /exner_c(self.Ref.p0_half[k]) * lh/cpd
        #
        #
        # self.prec_source_h_tot = np.sum(np.multiply(self.prec_source_h,UpdVar.Area.values), axis=0)
        # self.prec_source_qt_tot = np.sum(np.multiply(self.prec_source_qt,UpdVar.Area.values), axis=0)

        return

    cpdef update_updraftvars(self, UpdraftVariables UpdVar):
        cdef:
            Py_ssize_t k, i

        with nogil:
            for i in xrange(self.n_updraft):
                for k in xrange(self.Gr.nzg):
                    UpdVar.QT.values[i,k] += self.prec_source_qt[i,k]
                    UpdVar.H.values[i,k] += self.prec_source_h[i,k]

        return









# Functions
cdef inline double entr_inverse_z(double z_):
    return entr_c1/z_











