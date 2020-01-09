from ctypes import windll, WINFUNCTYPE
from ctypes import c_bool, c_int, POINTER
from ctypes import create_unicode_buffer


class MaxWindow(object):
    TITLE_IDENTIFIER = "Autodesk 3ds Max"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"

    def __init__(self, handler, title):
        super(MaxWindow, self).__init__()

        self.handler = handler
        self.title = title

    def __repr__(self):
        return self.title


class MayaWindow(object):
    TITLE_IDENTIFIER = "Autodesk Maya"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


def find_windows(title_identifier, class_identifier, get_first=False):
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
        if title_identifier in window_text:
            class_buffer = create_unicode_buffer(255)
            windll.user32.GetClassNameW(handler, class_buffer, 255)

            # compare class name
            if class_buffer.value == class_identifier:
                windows.append(MaxWindow(handler, window_text))
                return get_first
            return True

        return True

    windll.user32.EnumWindows(enum_windows, 0)
    return windows


def find_max_windows(get_first=False):
    return find_windows(MaxWindow.TITLE_IDENTIFIER, MaxWindow.CLASS_IDENTIFIER, get_first)


def find_maya_windows(get_first=False):
    return find_windows(MayaWindow.TITLE_IDENTIFIER, MayaWindow.CLASS_IDENTIFIER, get_first)


for max_window in find_max_windows():
    print("max window", max_window)

for maya_window in find_maya_windows():
    print("maya window", maya_window)
