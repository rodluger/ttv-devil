"""Interface to the C code."""
from __future__ import division, print_function, absolute_import, \
    unicode_literals
import ctypes
import numpy as np
import os
import sysconfig
MAXTRANSITS = 5000
SECOND = 1. / 86400.
MINUTE = 1. / 1440.
HOUR = 1. / 24.

# Find system suffix and import the shared library
suffix = sysconfig.get_config_var('EXT_SUFFIX')
if suffix is None:
    suffix = ".so"
dn = os.path.dirname
liborbit = ctypes.cdll.LoadLibrary(os.path.join(dn(dn(
                                   os.path.abspath(__file__))),
    "liborbit" + suffix))


class Body(ctypes.Structure):
    """Class containing all the input planet/star parameters."""

    #: All the fields
    _fields_ = [("m", ctypes.c_double),
                ("x", ctypes.c_double),
                ("y", ctypes.c_double),
                ("z", ctypes.c_double),
                ("vx", ctypes.c_double),
                ("vy", ctypes.c_double),
                ("vz", ctypes.c_double),
                ("nt", ctypes.c_int),
                ("_ptr_transit_times", ctypes.POINTER(ctypes.c_double)),
                ]

    def __init__(self, name, m, x, y, z, vx, vy, vz):
        """Init."""
        self.name = name
        self.m = m
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

    @property
    def transit_times(self):
        """List of all transit times in days."""
        try:
            self._transit_times
            self.nt
        except:
            return np.array([], dtype=float)
        return self._transit_times[:self.nt]

    @property
    def ttvs(self):
        """Array of TTV measurements in days."""
        # Based on http://rebound.readthedocs.io/en/latest/
        #          ipython/TransitTimingVariations.html
        A = np.vstack([np.ones(self.nt), range(self.nt)]).T
        c, m = np.linalg.lstsq(A, self.transit_times)[0]
        return self.transit_times - m * np.array(range(self.nt)) - c


class System(object):
    r"""
    The planetary system class.

    :param bodies: Any number of :py:class:`BODY` instances.
    :param float dt_reb: Timestep in days for the N-body solver. \
           Default `0.01`
    :param str integrator: The N-body integrator \
           (:py:obj:`whfast` | :py:obj:`ias15`) to use. \
           Default :py:obj:`ias15`
    """

    def __init__(self, *bodies, dt_reb=0.01, dt_trn=0.5,
                 tol=1e-7, integrator='ias15'):
        """Init."""
        # Initialize
        self.bodies = bodies
        self.dt_reb = dt_reb
        self.dt_trn = dt_trn
        self.tol = tol
        self.integrator = integrator
        self._reset()

    def _reset(self):
        """Reset the system and allocate memory."""
        # Make planets accessible as properties
        for body in self.bodies:
            setattr(self, body.name, body)
        self._names = np.array([p.name for p in self.bodies])

        # Initialize the C interface
        self._Compute = liborbit.Compute
        self._Compute.argtypes = [ctypes.c_int,
                                  ctypes.POINTER(ctypes.POINTER(Body)),
                                  ctypes.c_double,
                                  ctypes.c_double,
                                  ctypes.c_double,
                                  ctypes.c_double,
                                  ctypes.c_double,
                                  ctypes.c_int]

        # Allocate memory for all the arrays
        for body in self.bodies:
            body.nt = 0
            body._transit_times = np.zeros(MAXTRANSITS)
            body._ptr_transit_times = \
                np.ctypeslib.as_ctypes(body._transit_times)

        # A pointer to a pointer to `BODY`. This is an array of `n`
        # `BODY` instances, passed by reference. The contents can all be
        # accessed through `bodies`
        # NOTE: Before I subclassed BODY, this used to be
        # >>> self._ptr_bodies = (ctypes.POINTER(BODY) * \
        # >>> len(self.bodies))(*[ctypes.pointer(p) for p in self.bodies])
        # I now cast the `Planet`, `Star`, and `Moon` instances as `BODY`
        # pointers, as per https://stackoverflow.com/a/37827528
        self._ptr_bodies = (ctypes.POINTER(Body) * len(self.bodies))(
            *[ctypes.cast(ctypes.byref(p),
                          ctypes.POINTER(Body)) for p in self.bodies])

    def compute(self, tstart, tend):
        """Compute the positions of all bodies over the `time` array."""
        # Reset
        self._reset()
        if self.integrator.lower() == 'whfast':
            integrator = 1
        elif self.integrator.lower() == 'ias15':
            integrator = 0
        else:
            raise ValueError("Unsupported integrator.")

        # Call the light curve routine
        self._Compute(len(self.bodies), self._ptr_bodies,
                      tstart, tend, self.dt_reb, self.dt_trn, self.tol,
                      integrator)
