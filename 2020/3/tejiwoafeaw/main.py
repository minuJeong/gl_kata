import ctypes as ct


dirpath = "T:/branches/warhammer2/warden/warhammer/binaries.x64"

warscape = ct.WinDLL(f"{dirpath}/Warscape.profile.x64.dll")
print(warscape)
