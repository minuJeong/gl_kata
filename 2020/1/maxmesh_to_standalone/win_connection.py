from ctypes import windll, WINFUNCTYPE
from ctypes import c_bool, c_int, POINTER
from ctypes import create_unicode_buffer


class Window(object):
    TITLE_IDENTIFIER = None
    CLASS_IDENTIFIER = None

    def __init__(self, handler, title):
        super(Window, self).__init__()

        self.handler = handler
        self.title = title

    def __repr__(self):
        return self.title


class MaxWindow(Window):
    TITLE_IDENTIFIER = "Autodesk 3ds Max"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


class MayaWindow(Window):
    TITLE_IDENTIFIER = "Autodesk Maya"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


class HoudiniWindow(Window):
    TITLE_IDENTIFIER = "Houdini"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


def find_windows(winclass: type, get_first: bool=False) -> list:
    title_identifier = winclass.TITLE_IDENTIFIER
    class_identifier = winclass.CLASS_IDENTIFIER

    windows = []

    # windll func: enumerate over opened windows while returning True,
    # when returned False, enumeration stops.
    @WINFUNCTYPE(c_bool, c_int, POINTER(c_int))
    def enum_windows(handler, lparam):
        is_visible = windll.user32.IsWindowVisible(handler)
        if not is_visible:
            return True

        wintex_buffer = create_unicode_buffer(255)
        windll.user32.GetWindowTextW(
            handler, wintex_buffer, windll.user32.GetWindowTextLengthW(handler) + 1
        )
        window_text = wintex_buffer.value

        # compare title name
        if title_identifier and title_identifier in window_text:
            class_buffer = create_unicode_buffer(255)
            windll.user32.GetClassNameW(handler, class_buffer, 255)

            # compare class name
            if class_identifier and class_buffer.value == class_identifier:
                windows.append(winclass(handler, window_text))
                return get_first
            return True

        return True

    windll.user32.EnumWindows(enum_windows, 0)
    return windows


def iterate_supported_windows(get_first=False):
    for max_window in find_windows(MaxWindow, get_first):
        yield max_window

    for maya_window in find_windows(MayaWindow, get_first):
        yield maya_window

    for houdini_window in find_windows(HoudiniWindow, get_first):
        yield houdini_window


def test():
    for supported_window in iterate_supported_windows():
        print(supported_window, type(supported_window))


if __name__ == "__main__":
    test()
