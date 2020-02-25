from subprocess import Popen, PIPE
import sys
import ctypes as ct


libpath = "C:/Users/minu.jeong/Downloads/DirectXTex-master/DirectXTex/Bin/Desktop_2019_Win10/x64/Release"
if libpath not in sys.path:
    sys.path.append(libpath)


dllpath = "{}/DirectXTex.lib".format(libpath)

res = Popen(args="nm.exe {}".format(dllpath), shell=True, stdout=PIPE).communicate()[0].decode("utf8")
print(res)

# texlib = ct.WinDLL(dllpath)
# print(texlib.DirectX)
