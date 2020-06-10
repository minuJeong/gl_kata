GLFW
===

Window creation, input handling, GL context management, buffer handling in cross-platform

simplest glfw window creation

```
import glfw


glfw.init()

window = glfw.create_window(800, 600, "window title", None, None)
glfw.make_context_current(window)

while not glfw.window_should_close(window):
    glfw.swap_buffers(window)
    glfw.poll_events()

```
