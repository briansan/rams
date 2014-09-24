##
# @package RAMS.NXT
# @file NXT.py
# @author Brian Kim
# @date 7/24/14
# @brief a python wrapper that defines an interface to NXT robots
# @details roams calls them rovers, RAMS calls them bots

from NXTMotor import NXTMotor
from NXTSensor import NXTSensor

class NXTBot:
  def __init__( self, rvr ):
    # 
    self._rvr = rvr

    # setting the motors and sensors
    self._MotorA = self._MotorB = self._MotorC = NXTMotor( ) 
    self._Sensor1 = self._Sensor2 = self._Sensor3 = self._Sensor4 = NXTSensor( ) 

  def rvr( self ):
    return self._rvr

  def MotorA( self ):
    return self._MotorA

  def MotorB( self ):
    return self._MotorB

  def MotorC( self ):
    return self._MotorC

  def Sensor1( self ):
    return self._Sensor1

  def Sensor2( self ):
    return self._Sensor2

  def Sensor3( self ):
    return self._Sensor3

  def Sensor4( self ):
    return self._Sensor4
