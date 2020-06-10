imgui
===

bloat-free UI framework

simple example of using imgui with ModernGLGLFWRenderer

```
import moderngl
import imgui

from integrations.imgui import ModernGLGLFWRenderer


window_width, window_height = 800, 800

moderngl_context = moderngl.create_context()
imgui.create_context()
imgui_renderer = ModernGLGLFWRenderer(
    ctx=moderngl_context, display_size=(window_width, window_height)
)

imgui.new_frame()
if imgui.begin_main_menu_bar():
    if imgui.begin_menu("Test Menu"):
        imgui.end_menu()

    imgui.end_main_menu_bar()

imgui.begin("Control")
imgui.text(f"FPS {1.0 / (dt):.2f}")
imgui.drag_float("AA", 0.0)
imgui.checkbox("A", True)
imgui.checkbox("B", False)
imgui.radio_button("A", False)
imgui.radio_button("B", True)
imgui.radio_button("C", False)
imgui.end()

imgui.render()

imgui_renderer.render(imgui.get_draw_data())

```
