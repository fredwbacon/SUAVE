## @ingroup Components-Energy-Converters
# Motor.py
#
# Created:  Jun 2014, E. Botero
# Modified: Jan 2016, T. MacDonald

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

# package imports
import numpy as np
from SUAVE.Components.Energy.Energy_Component import Energy_Component

# ----------------------------------------------------------------------
#  Motor Class
# ----------------------------------------------------------------------
## @ingroup Components-Energy-Converters
class Motor(Energy_Component):
    """This is a motor component.
    
    Assumptions:
    None

    Source:
    None
    """      
    def __defaults__(self):
        """This sets the default values for the component to function.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """           
        self.resistance         = 0.0
        self.no_load_current    = 0.0
        self.speed_constant     = 0.0
        self.propeller_radius   = 0.0
        self.propeller_Cp       = 0.0
        self.gear_ratio         = 0.0
        self.gearbox_efficiency = 0.0
        self.expected_current   = 0.0
    
    def omega(self,conditions):
        """Calculates the motors rotation rate

        Assumptions:
        Cp (power coefficient) is constant

        Source:
        N/A

        Inputs:
        conditions.
          freestream.velocity                    [m/s]
          freestream.density                     [kg/m^3]
          propulsion.propeller_power_coefficient [-]
        self.inputs.voltage                      [V]

        Outputs:
        self.outputs.
          torque                                 [Nm]
          omega                                  [radian/s]

        Properties Used:
        self.
          resistance                             [ohms]
          gearbox_efficiency                     [-]
          expected_current                       [A]
          no_load_current                        [A]
          gear_ratio                             [-]
          speed_constant                         [radian/s/V]
          propeller_radius                       [m]
        """           
        # Unpack
        V     = conditions.freestream.velocity[:,0,None]
        rho   = conditions.freestream.density[:,0,None]
        Cp    = conditions.propulsion.propeller_power_coefficient[:,0,None]
        Res   = self.resistance
        etaG  = self.gearbox_efficiency
        exp_i = self.expected_current
        io    = self.no_load_current + exp_i*(1-etaG)
        G     = self.gear_ratio
        Kv    = self.speed_constant/G
        R     = self.propeller_radius
        v     = self.inputs.voltage
    
        # Omega
        # This is solved by setting the torque of the motor equal to the torque of the prop
        # It assumes that the Cp is constant
        omega1  =   ((np.pi**(3./2.))*((- 16.*Cp*io*rho*(Kv*Kv*Kv)*(R*R*R*R*R)*(Res*Res) +
                    16.*Cp*rho*v*(Kv*Kv*Kv)*(R*R*R*R*R)*Res + (np.pi*np.pi*np.pi))**(0.5) - 
                    np.pi**(3./2.)))/(8.*Cp*(Kv*Kv)*(R*R*R*R*R)*Res*rho)
        omega1[np.isnan(omega1)] = 0.0
        
        Q = ((v-omega1/Kv)/Res -io)/Kv
        # store to outputs
       
        #P = Q*omega1
        
        self.outputs.torque = Q
        self.outputs.omega = omega1

        return omega1
    
    def current(self,conditions):
        """Calculates the motors rotation rate

        Assumptions:
        Cp (power coefficient) is constant

        Source:
        N/A

        Inputs:
        self.inputs.voltage    [V]

        Outputs:
        self.outputs.current   [A]

        Properties Used:
        self.
          gear_ratio           [-]
          speed_constant       [radian/s/V]
          resistance           [ohm]
          outputs.omega        [radian/s]
          gearbox_efficiency   [-]
          expected_current     [A]
          no_load_current      [A]
        """                      
        
        # Unpack
        G     = self.gear_ratio
        Kv    = self.speed_constant
        Res   = self.resistance
        v     = self.inputs.voltage
        omeg  = self.outputs.omega*G
        etaG  = self.gearbox_efficiency
        exp_i = self.expected_current
        io    = self.no_load_current + exp_i*(1-etaG)
        
        i=(v-omeg/Kv)/Res
        
        # This line means the motor cannot recharge the battery
        i[i < 0.0] = 0.0

        # Pack
        self.outputs.current = i
          
        etam=(1-io/i)*(1-i*Res/v)
        conditions.propulsion.etam = etam
        
        return i

        
    