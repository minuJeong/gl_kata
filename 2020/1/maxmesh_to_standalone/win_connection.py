from ctypes import windll
from ctypes import POINTER, WINFUNCTYPE
from ctypes import c_bool, c_int
from ctypes import create_unicode_buffer


class Window(object):
    """
    Do not use this class directly. Instead use a subclass of this class.
    """

    TITLE_IDENTIFIER = None
    CLASS_IDENTIFIER = None

    def __init__(self, handler, title):
        super(Window, self).__init__()

        self.handler = handler
        self.title = title

    def __repr__(self):
        return self.title


class MaxWindow(Window):
    """
    Represents 3ds max window.
    """

    TITLE_IDENTIFIER = "Autodesk 3ds Max"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


class MayaWindow(Window):
    """
    Represents maya window.
    """

    TITLE_IDENTIFIER = "Autodesk Maya"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


class HoudiniWindow(Window):
    """
    Represents houdini window.
    """

    TITLE_IDENTIFIER = "Houdini"
    CLASS_IDENTIFIER = "Qt5QWindowIcon"


def find_windows(winclass: type, get_first: bool = False) -> list:
    """
    :param winclass:
    winclass should be a subclass of Window.

    :param get_first:
    if get_first is True, iteration stops immediately when first target window of the given class is found.

    return:
    returns list of windows
    """

    title_identifier = winclass.TITLE_IDENTIFIER
    class_identifier = winclass.CLASS_IDENTIFIER

    windows = []

    @WINFUNCTYPE(c_bool, c_int, POINTER(c_int))
    def enum_windows(handler: int, lparam):
        """
        :param handler:
        hanlder is an int that represents windll process handler id.

        :param lparam:
        lparam is always a null pointer here

        return:
        when returned False, enumeration stops, otherwise continues.
        """

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
                return not get_first
            return True

        return True

    windll.user32.EnumWindows(enum_windows, 0)
    return windows


def find_max_windows(get_first: bool=False):
    return find_windows(MaxWindow, get_first)


def find_maya_windows(get_first: bool=False):
    return find_windows(MayaWindow, get_first)


def find_houdini_windows(get_first: bool=False):
    return find_windows(HoudiniWindow, get_first)


def iterate_supported_windows(get_first: bool = False):
    """
    iterates all feasible windows.

    :param get_first:
    if get_first is True, stops immediately when first window is found.
    """

    for max_window in find_max_windows(get_first):
        yield max_window

    for maya_window in find_maya_windows(get_first):
        yield maya_window

    for houdini_window in find_houdini_windows(get_first):
        yield houdini_window


# test run this module
def test():
    for supported_window in iterate_supported_windows():
        print(supported_window, type(supported_window))


if __name__ == "__main__":
    test()
