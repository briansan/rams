##
# @package RAMS.NXT
# @file NXTPort.py
# @author Brian Kim
# @date 7/24/14
# @brief an nxt wrapper around a roams assembly
#

from Dshell.Dshell_Py import Assembly
from Rover import MotorAssembly

class NXTPort:
  
  def __init__( self, asm=None ):
    self._asm = asm

  def isValid( self ):
    return not self.asm() == None

  def asm( self ):
    return self._asm
