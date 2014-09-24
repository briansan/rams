##
# title: RAMSClient.py
# by: Brian Kim
# description: the top level program that runs the client
#  side controller of rams
#

import pygtk
pygtk.require('2.0')
import gtk

class RAMSClient.py( RAMSXMLRPCHandlerDelegate ):
  def __init__( self, ip ):
    self.xmlrpc_handler = RAMSXMLRPCHandler(ip)
    self.xmlrpc_handler.delegate = self
    self.info_window = RAMSInfoView( self.xmlrpc_handler )
    self.render_window = RAMSViewport( self.xmlrpc_handler )

  def start( self ):
    self.xmlrpc_handler.request_start()

  def resume( self ):
    self.xmlrpc_handler.request_resume()

  def pause( self ):
    self.xmlrpc_handler.request_pause()

  def stop( self ):
    self.xmlrpc_handler.request_stop()

  def cleanup( self ):
    self.info_window.cleanup()
    self.render_window.cleanup()
    self.xmlrpc_handler.cleanup() 

  def update( self ):
    self.xmlrpc_handler.request_update()

  def rams_xmlrpc_info_update( self, infoDict ):
    self.info_window.update( infoDict )

  def rams_xmlrpc_render_update( self, imageString ):
    aelf.render_window.update( imageString )


