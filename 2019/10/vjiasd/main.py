from ctypes import CDLL
from ctypes import c_int
from ctypes import c_ubyte


cpplibrary = CDLL("./cpp_library/CPPCommunication/x64/Debug/CPPLibrary.dll")
cpplibrary.Print("Hi")
