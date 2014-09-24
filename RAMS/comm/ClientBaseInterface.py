import abc


class ClientBaseInterface(object):

    """Base client interface.

    Contains a commandClient and a viewClient for commanding and viewing
    server information. This client utilizes pygame to display
    information and retrieve mouse and keyboard inputs.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server_URI):
        """
        __init__( server_URI ) -> Initializes command and view clients. Sets up connection with XMLRPC server
        """
        import xmlrpclib
        self._proxy = xmlrpclib.ServerProxy(server_URI)

    @abc.abstractmethod
    def processClients(self):
        """To be implemented by derived client classes Function processes data
        for the command and view clients."""

    def runClient(self, print_fps=False):
        """
        Runs the client -> Simply a loop sending and receiving commands for command/view clients
        """
        import time
        last_time = time.time()

        while self.processClients():
            if print_fps:
                current_time = time.time()
                print('FPS: {fps}'.format(fps=1. / (current_time - last_time)))
                last_time = current_time
