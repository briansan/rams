"""Client Interface for Pygame.

Pygame used to parse keyboard and mouse commands as well as display
images in a window

"""

from PygameClientInterface import PygameClientInterface


class JoystickClientInterface(PygameClientInterface):

    """
    __init__ function -> setup XMLRPC as well as pygame
    """

    def __init__(self, server_uri, update_image=True, joystick_id=0,
                 has_control=True):
        import pygame
        pygame.joystick.init()
        self.__joystick = pygame.joystick.Joystick(joystick_id)
        self.__joystick.init()

        self.__velocity_factor = 1.

        self.__has_control = has_control

        # Use base class to setup XMLRPC server
        PygameClientInterface.__init__(self, server_uri, update_image)

    def hasControl(self):
        """Return True if user wants to send control commands.

        Tab key and shift-tab toggle this.

        """
        # Check if control flag should be toggled.
        import pygame
        if pygame.key.get_pressed()[pygame.K_TAB]:
            self.__has_control = not (
                pygame.key.get_mods() & pygame.KMOD_LSHIFT)

            if self.__has_control:
                print('Take control')
            else:
                print('Release control')

        return self.__has_control

    def drive(self):
        pitch = -self.__joystick.get_axis(1) * self.__velocity_factor
        yaw = -self.__joystick.get_axis(2) * self.__velocity_factor

        self._proxy.setVel(0, pitch, 0)
        self._proxy.setRot(yaw)

    def processClients(self):
        exclusive_control = self.hasControl()

        if exclusive_control:
            self.drive()
            self.setWaypoint()

        return PygameClientInterface.processClients(
            self, exclusive_control=exclusive_control)

    def setWaypoint(self):
        """Process waypoint setting functions."""
        import pygame

        if pygame.key.get_pressed()[pygame.K_y]:
            self._proxy.setWayPoint()
