##
# @package RAMS.NXT
# @file    NXTSonarSensor.py
# @author  Brian Kim
# @date    7/24/14
# @brief   an NXT wrapper around the SonarSensorAssembly to interface with 
#          the NXT sonar sensors

from RAMS.NXT.NXTSensor import NXTSensor
from RAMS.common.sensors.SonarSensorAssembly import SonarSensorAssembly

class NXTSonarSensor( NXTSensor ):

  def getDepth( self ):
    sonar = self.asm()
    return sonar.getDepth()[0]

  def getData( self ):
    return self.getDepth()
