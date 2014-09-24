##
# @package RAMS.NXT
# @file    NXTAccelerometer.py
# @author  Brian Kim
# @date    7/24/14
# @brief   an NXT wrapper around the IMU sensor to interface with the NXT accelerometer

from NXTSensor import NXTSensor

class NXTAccelerometer( NXTSensor ):
  def getData( self ):
    return self.asm().signal('IMU_accel').specNode()()
