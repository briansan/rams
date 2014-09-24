"""This is an interface for the simulation to XMLRPC client.

It contains standardized functions that the client can access and will
interface these functions to sim functions

"""


class ServerInterface:

    def __init__(self, simulation, show_overlay=True):
        """
        __init__ -> Sets up the mapping of command names to simulation functions
        """
        self.__show_overlay = show_overlay

        # Function map initialized with some generic functions
        self._function_map = {}

        # Viewport list = List of viewports
        self._viewports = {'default': None}

        # Current viewport
        self._curr_viewport = 'default'

        # Simulation object
        self._sim = simulation

        # Toggle sim stepping
        self._step = False

        self.__exit_simulation_thread = False

        import os
        environment_variable = os.getenv('LUNAR_SIM_DEBUG')
        self.__print_debug_messages = False
        if environment_variable:
            self.__print_debug_messages = int(environment_variable)

    """
    addViewport function adds a viewport to the list
    """

    def addViewport(self, viewport, viewportName='default'):
        self._viewports[viewportName] = viewport

        if self.__show_overlay:
            # Show wall-clock time overlay
            viewport.overlayText('wall_time', '')
            viewport.overlayTextFont('wall_time', 'monospaced')
            viewport.overlayTextSize('wall_time', .05)
            viewport.overlayTextPosition('wall_time', .01, .95)
            viewport.overlayTextColor('wall_time', 1., 1., 1., .75)

    """
    Prepare a viewport for XMLRPC forwarding
    """

    def imageString(self, quality=70):

        def compress(image_format, size, data):
            from PIL import Image
            import cStringIO
            fake_file = cStringIO.StringIO()
            Image.fromstring(image_format, size, data).save(
                fake_file, 'jpeg', quality=quality)
            return fake_file.getvalue()

        viewport = self._viewports[self._curr_viewport]

        if viewport:
            image_format = 'RGB'
            image = viewport.contentsToString()
            size = (image.width, image.height)
            return compress(image_format, size, image.data).encode('base64')
        else:
            return 0

    """
    Select a viewport to view
    """

    def selectViewport(self, viewportName):

        if viewportName in self._viewports.keys() and self._viewports[viewportName]:
            self._curr_viewport = viewportName
            return 'Using the ' + viewportName + ' viewport.'
        else:
            return 'Error, viewport name not found. Using the default viewport.'

    """
    Toggle pausing
    """

    def toggleSim(self, toggle):
        self._step = toggle
        return 'Toggling Pause Play'

    """
    The viewport interaction function
    """

    def viewportInteraction(self, mousePressInfo, mousePosInfo, del_wheel):

        from DspaceOgre.DspaceOgre_Py import MouseInfo
        mouseinfo = MouseInfo()

        viewport = self._viewports[self._curr_viewport]

        mouseinfo.x = mousePosInfo[0]
        mouseinfo.y = mousePosInfo[1]
        mouseinfo.left = mousePressInfo[0]
        mouseinfo.right = mousePressInfo[2]
        mouseinfo.middle = mousePressInfo[1]

        # Need to find a good way to detect mousewheel stuff
        mouseinfo.delta_wheel_degrees = del_wheel

        viewport._mouseInput(mouseinfo)

        return True

    """
    Print available functions
    """

    def availableFunctions(self):
        """Returns available functions."""
        funcs = ['imageString', 'selectViewport', 'availableFunctions',
                 'toggleSim', 'time']
        return funcs + self._function_map.keys()

    """
    Register a function for XMLRPC forwarding
    """

    def addFunctionCall(self, funcName, func):
        assert hasattr(func, '__call__') and isinstance(funcName, str)
        self._function_map[funcName] = func

    """
    Setup and XMLRPC server
    """

    def runServer(self, hostname='', port=54321, render_path=None):
        import SimpleXMLRPCServer
        server = SimpleXMLRPCServer.SimpleXMLRPCServer(
            addr=(hostname, port), logRequests=self.__print_debug_messages)

        import time

        # Register viewport functions
        server.register_function(self.imageString, 'imageString')
        server.register_function(self.selectViewport, 'selectViewport')
        server.register_function(self.viewportInteraction, 'view')
        server.register_function(self.toggleSim, 'toggleSim')
        server.register_function(time.time, 'time')

        # Register check for available functions
        server.register_function(self.availableFunctions, 'availableFunctions')

        # Register additional user functions
        for funcName in self._function_map.keys():
            server.register_function(self._function_map[funcName], funcName)

        # Start simulation in separate thread
        import threading
        simulation_thread = threading.Thread(
            target=lambda: self.__runSimulation(render_path=render_path))
        self.__exit_simulation_thread = False
        simulation_thread.start()

        last_iteration_time = time.time()
        first_request = True
        while True:
            try:
                server.handle_request()
            except KeyboardInterrupt:
                break

            # Toggle on simulation if this is the first XMLRPC request
            if first_request:
                self._step = True
                first_request = False

            current_time = time.time()
            delta = current_time - last_iteration_time
            if delta > 0:
                fps = 1. / delta
            else:
                fps = 0.
            if self.__print_debug_messages:
                print('Server frame rate: {fps}'.format(fps=fps))
            last_iteration_time = current_time

        self.__exit_simulation_thread = True
        simulation_thread.join()

    def __runSimulation(self, render_path=None):
        """"""
        import time

        last_iteration_time = time.time()
        render_count = 0
        while not self.__exit_simulation_thread:
            if self._step:
                # DshelLCommon fsm step
                self._sim.stepSim()

                viewport = self._viewports[self._curr_viewport]

                if self.__show_overlay:
                    import datetime
                    viewport.overlayText(
                        'wall_time', '{t}'.format(t=datetime.datetime.now()))

                if render_path:
                    import os
                    render_filename = os.path.join(render_path,
                                                   '{i:06}.png'.format(i=render_count))
                    viewport.writeContentsToFile(render_filename)
                    print(render_filename)
                    render_count += 1

            current_time = time.time()
            delta = current_time - last_iteration_time
            if delta > 0:
                fps = 1. / delta
            else:
                fps = 0.
            if self.__print_debug_messages:
                print('Simulation frame rate: {fps}'.format(fps=fps))
            last_iteration_time = current_time
