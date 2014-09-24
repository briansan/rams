##
# @package RAMS.NXT
# @file NXTMotor.py
# @author Brian Kim
# @date 7/24/14
# @brief a wrapper around a MotorProfileAssembly that defines an interface with an NXTMotor
#

from NXTPort import NXTPort
from Rover import MotorAssembly

class NXTMotor( NXTPort ):
  
  def __init__( self, asm=None ):
    NXTPort.__init__( self, asm )
    # self.resetTacho()

  def tacho( self ):
    if self.isValid():
      asm = self.asm()
      name = asm.name()
      y = asm.signal( name + '_angle' ).specNode()
      return y()[0]

  def resetTacho( self ):
    if self.isValid():
      asm = self.asm()
      name = asm.name()
      y = asm.signal( name + '_angle' ).specNode()
      y(0)

  def setProfile( self, accel, vel, disp ):
    if self.isValid():
      asm = self.asm()
      name = asm.name()
      profile = asm.assembly( name+'Motor_ProfileMotor',0,False )
      if not profile == None:
        profile.motorProfileCmd( accel, vel, disp )
      else:
        raise Exception( 'Couldn\'t get ProfileMotor for %s' % name )
    
