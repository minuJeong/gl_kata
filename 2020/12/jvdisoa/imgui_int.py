import ctypes

import imgui
import moderngl
import glfw
from imgui.integrations.opengl import BaseOpenGLRenderer


class ModernGLRenderer(BaseOpenGLRenderer):

    VERTEX_SHADER_SRC = """
        #version 330
        uniform mat4 ProjMtx;
        in vec2 Position;
        in vec2 UV;
        in vec4 Color;
        out vec2 Frag_UV;
        out vec4 Frag_Color;
        void main() {
            Frag_UV = UV;
            Frag_Color = Color;
            gl_Position = ProjMtx * vec4(Position.xy, 0, 1);
        }
    """
    FRAGMENT_SHADER_SRC = """
        #version 330
        uniform sampler2D Texture;
        in vec2 Frag_UV;
        in vec4 Frag_Color;
        out vec4 Out_Color;
        void main() {
            Out_Color = Frag_Color * texture(Texture, Frag_UV.st);
        }
    """

    def __init__(self, *args, **kwargs):
        self._prog = None
        self._fbo = None
        self._font_texture = None
        self._vertex_buffer = None
        self._index_buffer = None
        self._vao = None
        self.wnd = kwargs.get('wnd')
        self.ctx = self.wnd.ctx if self.wnd and self.wnd.ctx else kwargs.get('ctx')

        if not self.ctx:
            raise ValueError('Missing moderngl context')

        assert isinstance(self.ctx, moderngl.context.Context)

        super().__init__()

        if 'display_size' in kwargs:
            self.io.display_size = kwargs.get('display_size')

    def refresh_font_texture(self):
        width, height, pixels = self.io.fonts.get_tex_data_as_rgba32()

        if self._font_texture:
            self._font_texture.release()

        self._font_texture = self.ctx.texture((width, height), 4, data=pixels)
        self.io.fonts.texture_id = self._font_texture.glo
        self.io.fonts.clear_tex_data()

    def _create_device_objects(self):
        self._prog = self.ctx.program(
            vertex_shader=self.VERTEX_SHADER_SRC,
            fragment_shader=self.FRAGMENT_SHADER_SRC,
        )
        self.projMat = self._prog['ProjMtx']
        self._prog['Texture'].value = 0
        self._vertex_buffer = self.ctx.buffer(reserve=imgui.VERTEX_SIZE * 65536)
        self._index_buffer = self.ctx.buffer(reserve=imgui.INDEX_SIZE * 65536)
        self._vao = self.ctx.vertex_array(
            self._prog,
            [
                (self._vertex_buffer, '2f 2f 4f1', 'Position', 'UV', 'Color'),
            ],
            index_buffer=self._index_buffer,
            index_element_size=imgui.INDEX_SIZE,
        )

    def render(self, draw_data):
        io = self.io
        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_fb_scale[0])
        fb_height = int(display_height * io.display_fb_scale[1])

        if fb_width == 0 or fb_height == 0:
            return

        self.projMat.value = (
            2.0 / display_width, 0.0, 0.0, 0.0,
            0.0, 2.0 / -display_height, 0.0, 0.0,
            0.0, 0.0, -1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
        )

        draw_data.scale_clip_rects(*io.display_fb_scale)

        self.ctx.enable_only(moderngl.BLEND)
        self.ctx.blend_equation = moderngl.FUNC_ADD
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self._font_texture.use()

        for commands in draw_data.commands_lists:
            # Write the vertex and index buffer data without copying it
            vtx_type = ctypes.c_byte * commands.vtx_buffer_size * imgui.VERTEX_SIZE
            idx_type = ctypes.c_byte * commands.idx_buffer_size * imgui.INDEX_SIZE
            vtx_arr = (vtx_type).from_address(commands.vtx_buffer_data)
            idx_arr = (idx_type).from_address(commands.idx_buffer_data)
            self._vertex_buffer.write(vtx_arr)
            self._index_buffer.write(idx_arr)

            idx_pos = 0
            for command in commands.commands:
                x, y, z, w = command.clip_rect
                self.ctx.scissor = int(x), int(fb_height - w), int(z - x), int(w - y)
                self._vao.render(moderngl.TRIANGLES, vertices=command.elem_count, first=idx_pos)
                idx_pos += command.elem_count

        self.ctx.scissor = None

    def _invalidate_device_objects(self):
        if self._font_texture:
            self._font_texture.release()
        if self._vertex_buffer:
            self._vertex_buffer.release()
        if self._index_buffer:
            self._index_buffer.release()
        if self._vao:
            self._vao.release()
        if self._prog:
            self._prog.release()

        self.io.fonts.texture_id = 0
        self._font_texture = None


class ModernGLGLFWRenderer(ModernGLRenderer):

    def on_resize(self, window, width, height):
        pass

    def on_cursor_pos(self, window, x, y):
        pass

    def on_mouse_button(self, window, button, action, mods):
        pass

    def on_scroll(self, window, scroll_x, scroll_y):
        pass

    def wire_events(self, gl, window):
        """
        :param gl:
        moderngl context

        :param window:
        glfw window handle
        """

        def on_resize(window, width, height):
            gl.viewport = (0, 0, width, height)
            imgui.get_io().display_size = width, height
            self.on_resize(window, width, height)

        def on_cursor_pos(window, x, y):
            imgui.get_io().mouse_pos = x, y
            self.on_cursor_pos(window, x, y)

        def on_mouse_button(window, button, action, mods):
            imgui.get_io().mouse_down[button] = action
            self.on_mouse_button(window, button, action, mods)

        def on_scroll(window, scroll_x, scroll_y):
            imgui.get_io().mouse_wheel = scroll_y
            self.on_scroll(window, scroll_x, scroll_y)

        glfw.set_window_size_callback(window, on_resize)
        glfw.set_cursor_pos_callback(window, on_cursor_pos)
        glfw.set_mouse_button_callback(window, on_mouse_button)
        glfw.set_scroll_callback(window, on_scroll)
