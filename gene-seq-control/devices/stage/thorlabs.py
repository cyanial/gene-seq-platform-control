"""
Thorlabs APT Stages controller.

2021/11/06


"""

import ctypes

from ctypes import byref, POINTER
from ctypes import c_char_p, c_int, c_short, c_long, c_double
from ctypes.wintypes import DWORD

THORLABS_DLL = "C:/Program Files/Thorlabs/Kinesis/Thorlabs.MotionControl.Benchtop.BrushlessMotor.dll"
SERIALNO = c_char_p(b"73852055")

kndll = ctypes.cdll.LoadLibrary(THORLABS_DLL)


# FT_Status
FT_OK = 0x00                    # <OK - no error.
FT_InvalidHandle = 0x01         # <Invalid handle.
FT_DeviceNotFound = 0x02        # <Device not found.
FT_DeviceNotOpened = 0x03       # <Device not opened.
FT_IOError = 0x04               # <I/O error.
FT_InsufficientResources = 0x05 # <Insufficient resources.
FT_InvalidParameter = 0x06      # <Invalid parameter.
FT_DeviceNotPresent = 0x07      # <Device not present.
FT_IncorrectDevice = 0x08       # <Incorrect device.

kndll.BMC_Open.argtypes = [c_char_p]
kndll.BMC_Close.argtypes = [c_char_p]
kndll.BMC_LoadSettings.argtypes = [c_char_p, c_short]
kndll.BMC_StartPolling.argtypes = [c_char_p, c_short, c_int]
kndll.BMC_StopPolling.argtypes = [c_char_p, c_short]
kndll.BMC_GetPosition.argtypes = [c_char_p, c_short]
kndll.BMC_GetMotorParams.argtypes = [c_char_p, c_short, POINTER(c_long)]
kndll.BMC_EnableChannel.argtypes = [c_char_p, c_short]
kndll.BMC_DisableChannel.argtypes = [c_char_p, c_short]
kndll.BMC_GetMotorTravelLimits.argtypes = [c_char_p, c_short, POINTER(c_double), POINTER(c_double)]
kndll.BMC_GetStatusBits.argtypes = [c_char_p, c_short]
kndll.BMC_Home.argtypes = [c_char_p, c_short]
kndll.BMC_MoveRelative.argtypes = [c_char_p, c_short, c_int]
kndll.BMC_MoveToPosition.argtypes = [c_char_p, c_short, c_int]
kndll.BMC_GetStageAxisMinPos.argtypes = [c_char_p, c_short]
kndll.BMC_GetStageAxisMaxPos.argtypes = [c_char_p, c_short]

kndll.BMC_GetStatusBits.restype = DWORD

class Kinesis_Stage():
    """Kinesis SDK bind"""

    def __init__(self):
        self._connected = False
        kndll.TLI_BuildDeviceList()
        kndll.BMC_Open(SERIALNO)
        kndll.BMC_LoadSettings(SERIALNO, 1)     # x-axis
        kndll.BMC_LoadSettings(SERIALNO, 2)     # y-axis

        # Starts the internal polling loop
        # which continuously requests position and status.
        kndll.BMC_StartPolling(SERIALNO, 1, 200)    # x-axis 200ms
        kndll.BMC_StartPolling(SERIALNO, 2, 200)    # y-axis 200ms

        x_countsPerUnit, y_countsPerUnit = c_long(), c_long()
        kndll.BMC_GetMotorParams(SERIALNO, 1, byref(x_countsPerUnit))
        kndll.BMC_GetMotorParams(SERIALNO, 1, byref(y_countsPerUnit))
        self.x_countsPerUnit = x_countsPerUnit.value
        self.y_countsPerUnit = y_countsPerUnit.value

        x_min_mm, x_max_mm, y_min_mm, y_max_mm = c_double(), c_double(), c_double(), c_double()
        kndll.BMC_GetMotorTravelLimits(SERIALNO, 1, byref(x_min_mm), byref(x_max_mm))
        kndll.BMC_GetMotorTravelLimits(SERIALNO, 2, byref(y_min_mm), byref(y_max_mm))
        self.x_min_mm = x_min_mm.value
        self.x_max_mm = x_max_mm.value
        self.y_min_mm = y_min_mm.value
        self.y_max_mm = y_max_mm.value

        self.x_min_pos = kndll.BMC_GetStageAxisMinPos(SERIALNO, 1)
        self.x_max_pos = kndll.BMC_GetStageAxisMaxPos(SERIALNO, 1)
        self.y_min_pos = kndll.BMC_GetStageAxisMinPos(SERIALNO, 2)
        self.y_max_pos = kndll.BMC_GetStageAxisMaxPos(SERIALNO, 2)

        self._connected = True

    def __del__(self):
        self.disableX()
        self.disableY()
        kndll.BMC_StopPolling(SERIALNO, 1)
        kndll.BMC_StopPolling(SERIALNO, 2)
        kndll.BMC_Close(SERIALNO)
        print("Shutdown - Thorlabs")

    def available(self):
        return self._connected

    def getXpos(self):
        return kndll.BMC_GetPosition(SERIALNO, 1)

    def getYpos(self):
        return kndll.BMC_GetPosition(SERIALNO, 2)

    def getXpos_mm(self):
        return self.xpos_to_mm(self.getXpos())

    def getYpos_mm(self):
        return self.ypos_to_mm(self.getYpos())

    def enableX(self):
        """Enable x-axis"""
        return kndll.BMC_EnableChannel(SERIALNO, 1)

    def enableY(self):
        """Enable y-axis"""
        return kndll.BMC_EnableChannel(SERIALNO, 2)

    def disableX(self):
        """Disable x-axis"""
        return kndll.BMC_DisableChannel(SERIALNO, 1)

    def disableY(self):
        """Disable y-axis"""
        return kndll.BMC_DisableChannel(SERIALNO, 2)

    def homeX(self):
        return kndll.BMC_Home(SERIALNO, 1)

    def homeY(self):
        return kndll.BMC_Home(SERIALNO, 2)

    def moveXabsolute(self, pos):
        return kndll.BMC_MoveToPosition(SERIALNO, 1, pos)

    def moveYabsolute(self, pos):
        return kndll.BMC_MoveToPosition(SERIALNO, 2, pos)

    def moveXrelative(self, pos):
        curr_pos = self.getXpos()
        if curr_pos + pos > self.x_max_pos:
            return self.moveXabsolute(self.x_max_pos)
        if curr_pos + pos < self.x_min_pos:
            return self.moveXabsolute(self.x_min_pos)
        return kndll.BMC_MoveRelative(SERIALNO, 1, pos)

    def moveYrelative(self, pos):
        curr_pos = self.getYpos()
        if curr_pos + pos > self.y_max_pos:
            return self.moveYabsolute(self.y_max_pos)
        if curr_pos + pos < self.y_min_pos:
            return self.moveYabsolute(self.y_min_pos)
        return kndll.BMC_MoveRelative(SERIALNO, 2, pos)

    def getXStatusBit(self):
        return kndll.BMC_GetStatusBits(SERIALNO, 1)

    def getYStatusBit(self):
        return kndll.BMC_GetStatusBits(SERIALNO, 2)

    def isXenable(self):
        return (self.getXStatusBit() & 0x80000000) == 0x80000000
    
    def isYenable(self):
        return (self.getYStatusBit() & 0x80000000) == 0x80000000

    def isXhomed(self):
        return (self.getXStatusBit() & 0x00000400) == 0x00000400

    def isYhomed(self):
        return (self.getYStatusBit() & 0x00000400) == 0x00000400

    def mm_to_xpos(self, mm):
        return int(mm * self.x_countsPerUnit)
    
    def mm_to_ypos(self, mm):
        return int(mm * self.y_countsPerUnit)

    def xpos_to_mm(self, xpos):
        return xpos / self.x_countsPerUnit

    def ypos_to_mm(self, ypos):
        return ypos / self.y_countsPerUnit

    

        

if __name__ == "__main__":
    stage = Kinesis_Stage()

    if stage.available():
        print('-- Thorlabs Stage --')
        print('-- -- Pos range: ')
        print(f'-- -- x: {stage.x_min_mm} ~ {stage.x_max_mm}')
        print(f'-- -- y: {stage.y_min_mm} ~ {stage.y_max_mm}')
        print(f'-- -- x: {stage.x_min_pos} ~ {stage.x_max_pos}')
        print(f'-- -- y: {stage.y_min_pos} ~ {stage.y_max_pos}')
        x_pos = stage.getXpos()
        y_pos = stage.getYpos()
        print(f'-- -- (x, y): ({x_pos}, {y_pos})')

        x_mm = stage.getXpos_mm()
        y_mm = stage.getYpos_mm()
        print(f'-- -- (x, y): ({x_mm}, {y_mm})')

        # stage.disableX()
        # stage.disableY()
        # print(stage.isXenable())
        # print(stage.isYenable())
        # print(stage.isXhomed())
        # print(stage.isYhomed())
        

    
