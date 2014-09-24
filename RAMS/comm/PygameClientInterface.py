"""Client Interface for Pygame.

Pygame used to parse keyboard and mouse commands as well as display
images in a window

"""

from ClientBaseInterface import ClientBaseInterface


def retrieveDecompressedImage(proxy):
    """Return timestamped image from proxy."""
    from PIL import Image
    import cStringIO

    timestamp = proxy.time()
    data = proxy.imageString().decode('base64')
    fake_file = cStringIO.StringIO(data)
    image = Image.open(fake_file)
    return (image.tostring(), image.size, image.mode, timestamp)


class PygameClientInterface(ClientBaseInterface):

    def __init__(self, server_uri, update_image=True):
        """
        __init__ function -> setup XMLRPC as well as pygame
        """
        # Use base class to setup XMLRPC server
        ClientBaseInterface.__init__(self, server_uri)
        self.__server_uri = server_uri

        # Init pygame
        import pygame
        pygame.init()

        # Setup display
        (image_string, size, image_format,
         _) = retrieveDecompressedImage(self._proxy)
        self._screen = pygame.display.set_mode(size)

        self.__update_image = update_image

        self.__view_time_delay = 0.
        self.__command_time_delay = 0.

        import threading
        self.__quit_event = threading.Event()

        import Queue
        self.__image_queue = Queue.Queue()
        self.__command_queue = Queue.Queue()

        self.__image_producer_thread = threading.Thread(
            target=self.__produceImages)
        self.__image_producer_thread.start()

        self.__command_consumer_thread = threading.Thread(
            target=self.__consumeCommands)
        self.__command_consumer_thread.start()

    def quit(self):
        """Quit client."""
        # If dwatch present in server, have dwatch save
        if 'saveDwatch' in self._proxy.availableFunctions():
            self._proxy.saveDwatch()

        # Stop background threads
        self.__quit_event.set()
        # Put dummy item to get out of queue
        self.__command_queue.put(
            {'xvel': 0., 'yvel': 0., 'rot': 0., 'local_timestamp': 0.})
        self.__command_consumer_thread.join()
        self.__image_producer_thread.join()

    def processClients(self, exclusive_control=True):
        """Implement pure virtual function to process information."""
        import pygame
        events = pygame.event.get()

        if self.__update_image:
            self.updateImage()

        if exclusive_control:
            #self.camera(events)
            self.pausePlay()

        for e in events:
            if (e.type == pygame.QUIT or
                    (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)):
                self.quit()
                return False
        if (pygame.key.get_pressed()[pygame.K_b]):
            self._proxy.saveDwatch()

        return True

    def sendCommands(self, xvel, yvel, rot):
        """Process camera events."""
        # These commands are small so we assume latency to server is nearly 0.
        # This assumption allows us to simplify things and do the time delay
        # for the commands on the client.
        if not self.__quit_event.is_set():
            import time
            self.__command_queue.put({'xvel': xvel,
                                      'yvel': yvel,
                                      'rot': rot,
                                      'local_timestamp': time.time()})
            del xvel
            del yvel
            del rot

    def camera(self, events):

        import pygame

        del_wheel = 0
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    del_wheel -= 60
                elif event.button == 5:
                    del_wheel += 60

        self.cameraMove(pygame.mouse.get_pressed(),
                        pygame.mouse.get_pos(), del_wheel)

    def pausePlay(self):
        """Spacebar toggles pause play."""
        import pygame

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self._proxy.toggleSim(True)
        if pygame.key.get_pressed()[pygame.K_p]:
            self._proxy.toggleSim(False)

    def updateImage(self):
        """Update the image."""
        import pygame

        black = (0, 0, 0)

        image = self.retrieveImage()
        self._screen.fill(black)
        self._screen.blit(image, image.get_rect())

        pygame.display.flip()

    def retrieveImage(self):
        """
        Return time-delayed image.
        """
        while True:
            timestamped_image = self.__image_queue.get()
            current_server_time = self.serverTime()

            delta = current_server_time - timestamped_image['timestamp']
            assert delta >= 0
            """
            if delta > self.__view_time_delay:
                # Drop this image since it is too old
                self.__image_queue.task_done()
                continue
            else:
            """
            if delta < self.__view_time_delay:
                import time
                sleep_time = self.__view_time_delay - delta
                assert sleep_time > 0
                time.sleep(sleep_time)

            self.__image_queue.task_done()
            return timestamped_image['image']

    def setRoundTripTimeDelay(self, seconds):
        """
        Specify the round-trip time delay for purposes of emulation
        that happens purely in the client.
        """
        self.__view_time_delay = self.__command_time_delay = seconds / 2.

    def __produceImages(self):
        """Retrieve images and put in queue."""
        # This thread needs its own separate connection for thread safety
        import xmlrpclib
        proxy = xmlrpclib.ServerProxy(self.__server_uri)

        while not self.__quit_event.is_set():
            # Don't produce more images until they are consumed
            if self.__image_queue.qsize() > 1 + 30 * self.__view_time_delay:
                import time
                time.sleep(.01)
                continue
            (image_string, size, image_format,
             timestamp) = retrieveDecompressedImage(proxy)
            import pygame
            image = pygame.image.fromstring(image_string, size, image_format)
            self.__image_queue.put({'image': image, 'timestamp': timestamp})

    def __consumeCommands(self):
        """
        Consume commands from queue and execute them in a time-delayed
        manner.
        """
        # This thread needs its own separate connection for thread safety
        import xmlrpclib
        proxy = xmlrpclib.ServerProxy(self.__server_uri)

        import time
        while not self.__quit_event.is_set():
            timestamped_command = self.__command_queue.get()
            if self.__quit_event.is_set():
                break

            current_local_time = time.time()

            delta = current_local_time - timestamped_command['local_timestamp']
            assert delta >= 0
            if delta < self.__command_time_delay:
                sleep_time = self.__command_time_delay - delta
                assert sleep_time > 0
                time.sleep(sleep_time)

            proxy.setVel(timestamped_command['xvel'],
                         timestamped_command['yvel'],
                         0.)
            proxy.setRot(timestamped_command['rot'])

            self.__command_queue.task_done()

    def cameraMove(self, mouse_buttons, mouse_pos, wheel):
        """
        cameraMove -> Takes mouse information and passes it to server for camera action
        """
        self._proxy.view(mouse_buttons, mouse_pos, wheel)

    def serverTime(self):
        """Return current time on server."""
        return self._proxy.time()

    def writeToImageFile(self, filename):
        """Write the contents of the pygame screen to image file."""
        import pygame
        pygame.image.save(self._screen, filename)
