# test_AVL.py
# 
# Created:  May 2017, M. Clarke
#
""" setup file for a mission with a 737 using AVL
"""

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

import SUAVE
from SUAVE.Core import Units

import numpy as np
import pylab as plt

import copy, time

from SUAVE.Core import (
Data, Container,
)

import sys

sys.path.append('../Vehicles')
# the analysis functions

from Boeing_737 import vehicle_setup, configs_setup


sys.path.append('../B737')
# the analysis functions


from mission_B737 import vehicle_setup, configs_setup, analyses_setup, mission_setup, missions_setup, simple_sizing
import copy

# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main(): 
   
    # vehicle data
    vehicle  = vehicle_setup()
    configs  = configs_setup(vehicle)

    # vehicle analyses
    configs_analyses = analyses_setup(configs)
    
    aerodynamics          = SUAVE.Analyses.Aerodynamics.AVL()
    stability             = SUAVE.Analyses.Stability.AVL()
    aerodynamics.geometry = copy.deepcopy(configs.cruise)
    stability.geometry    = copy.deepcopy(configs.cruise)
    aerodynamics.process.compute.lift.inviscid.training_file = 'base_data_aerodynamics.txt'
    stability.training_file                                  = 'base_data_stability.txt'    
    configs_analyses.cruise.append(aerodynamics)
    configs_analyses.cruise.append(stability)

    # mission analyses
    mission  = mission_setup(configs_analyses)
    missions_analyses = missions_setup(mission)

    analyses = SUAVE.Analyses.Analysis.Container()
    analyses.configs  = configs_analyses
    analyses.missions = missions_analyses

    simple_sizing(configs, analyses)

    configs.finalize()
    analyses.finalize()
 
    # mission analysis
    mission = analyses.missions.base    
    results = mission.evaluate()

    # lift coefficient check
    lift_coefficient              = results.conditions.cruise.aerodynamics.lift_coefficient[0]
    lift_coefficient_true         = 0.59571034
    print lift_coefficient
    diff_CL                       = np.abs(lift_coefficient  - lift_coefficient_true) 
    print 'CL difference'
    print diff_CL
    assert np.abs((lift_coefficient  - lift_coefficient_true)/lift_coefficient_true) < 1e-6
    
    # moment coefficient check
    moment_coefficient            = results.conditions.cruise.stability.static.CM[0][0]
    moment_coefficient_true       = -0.62167644
    print moment_coefficient
    diff_CM                       = np.abs(moment_coefficient - moment_coefficient_true)
    print 'CM difference'
    print diff_CM
    assert np.abs((moment_coefficient - moment_coefficient_true)/moment_coefficient_true) < 1e-6    
 
    return

if __name__ == '__main__': 
    main()    
 