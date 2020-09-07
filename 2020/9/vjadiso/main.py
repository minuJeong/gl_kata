import glfw
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client(object):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.gl = mg.create_context()

        handler = FileSystemEventHandler()
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        pass

    def update(self):
        pass


def main():
    assert glfw.init()

    window = glfw.create_window(800, 600, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    if not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
