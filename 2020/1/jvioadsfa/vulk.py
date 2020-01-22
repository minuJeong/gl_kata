from threading import Thread

import glfw
import vulkan


WIDTH, HEIGHT = 1024, 1024


class Application(Thread):
    def __init__(self):
        super(Application, self).__init__()

    def init(self):
        application_info = vulkan.VkApplicationInfo(
            sType=vulkan.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="Triangle",
        )
        instance_create_info = vulkan.VkInstanceCreateInfo(
            sType=vulkan.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pNext=None,
            flags=0,
            pApplicationInfo=application_info,
            ppEnabledExtensionNames=glfw.get_required_instance_extensions(),
        )

        self.instance = vulkan.vkCreateInstance(instance_create_info, None)
        if not self.instance:
            raise Exception("can't create vulkan instance")

        self.device = None
        for device in vulkan.vkEnumeratePhysicalDevices(self.instance):
            if device:
                self.device = device
                break

        if not self.device:
            raise Exception("no suitable device is found")

        for x in dir(self.instance):
            print(x)

    def mainloop(self):
        pass

    def cleanup(self):
        vulkan.vkDestroyInstance(self.instance, None)
        glfw.destroy_window(self.window)
        glfw.terminate()

    def run(self):
        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        self.window = glfw.create_window(WIDTH, HEIGHT, "hello vulkan", None, None)
        self.init()
        while not glfw.window_should_close(self.window):
            glfw.swap_buffers(self.window)
            glfw.poll_events()
            self.mainloop()
        self.cleanup()


app = Application()
app.start()
app.join()
