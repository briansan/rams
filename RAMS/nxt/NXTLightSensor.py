##
# @package RAMS.NXT
# @file    NXTLightSensor.py
# @author  Brian Kim
# @date    7/24/14
# @brief   a python wrapper around the LightSensorAssembly to interface with 
#          the NXT light sensors

from NXTSensor import NXTSensor

class NXTLightSensor( NXTSensor ):

  def getIntensity( self ):
    light  = self.asm()
    return light.getIntensity()[0]

  def getData( self ):
    return self.getIntensity()
