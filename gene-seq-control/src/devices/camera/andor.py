"""
Python bind andor sdk 2.x

2021/11/06

To-do List:
1. [x] PreAmp - set 5x
2. [x] EM Gain - a range not advanced mode
3. [  ] Snap Mode
4. [  ] Live Mode
5. [  ] ...

"""

import ctypes
import os

from ctypes import c_int, c_ulong, c_char_p, c_float
from ctypes import byref, sizeof, Structure, POINTER
from ctypes import create_string_buffer
from ctypes.wintypes import WORD 

import numpy as np




DLL_PATH = "D:/Program Files/Andor SDK/atmcd64d.dll"

# 
camdll = ctypes.windll.LoadLibrary(DLL_PATH)

# Return Codes
DRV_ERROR_CODES = 20001
DRV_SUCCESS = 20002
DRV_VXDNOTINSTALLED = 20003
DRV_ERROR_SCAN = 20004
DRV_ERROR_CHECK_SUM = 20005
DRV_ERROR_FILELOAD = 20006
DRV_UNKNOWN_FUNCTION = 20007
DRV_ERROR_VXD_INIT = 20008
DRV_ERROR_ADDRESS = 20009
DRV_ERROR_PAGELOCK = 20010
DRV_ERROR_PAGEUNLOCK = 20011
DRV_ERROR_BOARDTEST = 20012
DRV_ERROR_ACK = 20013
DRV_ERROR_UP_FIFO = 20014
DRV_ERROR_PATTERN = 20015

DRV_ACQUISITION_ERRORS = 20017
DRV_ACQ_BUFFER = 20018
DRV_ACQ_DOWNFIFO_FULL = 20019
DRV_PROC_UNKONWN_INSTRUCTION = 20020
DRV_ILLEGAL_OP_CODE = 20021
DRV_KINETIC_TIME_NOT_MET = 20022
DRV_ACCUM_TIME_NOT_MET = 20023
DRV_NO_NEW_DATA = 20024
DRV_PCI_DMA_FAIL = 20025
DRV_SPOOLERROR = 20026
DRV_SPOOLSETUPERROR = 20027
DRV_FILESIZELIMITERROR = 20028
DRV_ERROR_FILESAVE = 20029

DRV_TEMPERATURE_CODES = 20033
DRV_TEMPERATURE_OFF = 20034
DRV_TEMPERATURE_NOT_STABILIZED = 20035
DRV_TEMPERATURE_STABILIZED = 20036
DRV_TEMPERATURE_NOT_REACHED = 20037
DRV_TEMPERATURE_OUT_RANGE = 20038
DRV_TEMPERATURE_NOT_SUPPORTED = 20039
DRV_TEMPERATURE_DRIFT = 20040

DRV_TEMP_CODES = 20033
DRV_TEMP_OFF = 20034
DRV_TEMP_NOT_STABILIZED = 20035
DRV_TEMP_STABILIZED = 20036
DRV_TEMP_NOT_REACHED = 20037
DRV_TEMP_OUT_RANGE = 20038
DRV_TEMP_NOT_SUPPORTED = 20039
DRV_TEMP_DRIFT = 20040

DRV_GENERAL_ERRORS = 20049
DRV_INVALID_AUX = 20050
DRV_COF_NOTLOADED = 20051
DRV_FPGAPROG = 20052
DRV_FLEXERROR = 20053
DRV_GPIBERROR = 20054
DRV_EEPROMVERSIONERROR = 20055

DRV_DATATYPE = 20064
DRV_DRIVER_ERRORS = 20065
DRV_P1INVALID = 20066
DRV_P2INVALID = 20067
DRV_P3INVALID = 20068
DRV_P4INVALID = 20069
DRV_INIERROR = 20070
DRV_COFERROR = 20071
DRV_ACQUIRING = 20072
DRV_IDLE = 20073
DRV_TEMPCYCLE = 20074
DRV_NOT_INITIALIZED = 20075
DRV_P5INVALID = 20076
DRV_P6INVALID = 20077
DRV_INVALID_MODE = 20078
DRV_INVALID_FILTER = 20079

DRV_I2CERRORS = 20080
DRV_I2CDEVNOTFOUND = 20081
DRV_I2CTIMEOUT = 20082
DRV_P7INVALID = 20083
DRV_P8INVALID = 20084
DRV_P9INVALID = 20085
DRV_P10INVALID = 20086
DRV_P11INVALID = 20087

DRV_USBERROR = 20089
DRV_IOCERROR = 20090
DRV_VRMVERSIONERROR = 20091
DRV_GATESTEPERROR = 20092
DRV_USB_INTERRUPT_ENDPOINT_ERROR = 20093
DRV_RANDOM_TRACK_ERROR = 20094
DRV_INVALID_TRIGGER_MODE = 20095
DRV_LOAD_FIRMWARE_ERROR = 20096
DRV_DIVIDE_BY_ZERO_ERROR = 20097
DRV_INVALID_RINGEXPOSURES = 20098
DRV_BINNING_ERROR = 20099
DRV_INVALID_AMPLIFIER = 20100
DRV_INVALID_COUNTCONVERT_MODE = 20101
DRV_USB_INTERRUPT_ENDPOINT_TIMEOUT = 20102

DRV_ERROR_NOCAMERA = 20990
DRV_NOT_SUPPORTED = 20991
DRV_NOT_AVAILABLE = 20992

DRV_ERROR_MAP = 20115
DRV_ERROR_UNMAP = 20116
DRV_ERROR_MDL = 20117
DRV_ERROR_UNMDL = 20118
DRV_ERROR_BUFFSIZE = 20119
DRV_ERROR_NOHANDLE = 20121

DRV_GATING_NOT_AVAILABLE = 20130
DRV_FPGA_VOLTAGE_ERROR = 20131

DRV_OW_CMD_FAIL = 20150
DRV_OWMEMORY_BAD_ADDR = 20151
DRV_OWCMD_NOT_AVAILABLE = 20152
DRV_OW_NO_SLAVES = 20153
DRV_OW_NOT_INITIALIZED = 20154
DRV_OW_ERROR_SLAVE_NUM = 20155
DRV_MSTIMINGS_ERROR = 20156

DRV_OA_NULL_ERROR = 20173
DRV_OA_PARSE_DTD_ERROR = 20174
DRV_OA_DTD_VALIDATE_ERROR = 20175
DRV_OA_FILE_ACCESS_ERROR = 20176
DRV_OA_FILE_DOES_NOT_EXIST = 20177
DRV_OA_XML_INVALID_OR_NOT_FOUND_ERROR = 20178
DRV_OA_PRESET_FILE_NOT_LOADED = 20179
DRV_OA_USER_FILE_NOT_LOADED = 20180
DRV_OA_PRESET_AND_USER_FILE_NOT_LOADED = 20181
DRV_OA_INVALID_FILE = 20182
DRV_OA_FILE_HAS_BEEN_MODIFIED = 20183
DRV_OA_BUFFER_FULL = 20184
DRV_OA_INVALID_STRING_LENGTH = 20185
DRV_OA_INVALID_CHARS_IN_NAME = 20186
DRV_OA_INVALID_NAMING = 20187
DRV_OA_GET_CAMERA_ERROR = 20188
DRV_OA_MODE_ALREADY_EXISTS = 20189
DRV_OA_STRINGS_NOT_EQUAL = 20190
DRV_OA_NO_USER_DATA = 20191
DRV_OA_VALUE_NOT_SUPPORTED = 20192
DRV_OA_MODE_DOES_NOT_EXIST = 20193
DRV_OA_CAMERA_NOT_SUPPORTED = 20194
DRV_OA_FAILED_TO_GET_MODE = 20195
DRV_OA_CAMERA_NOT_AVAILABLE = 20196

DRV_PROCESSING_FAILED = 20211

class AndorCapabilities(Structure):
    _fields_ = [("ulSize", c_ulong),
            ("ulAcqModes", c_ulong),
            ("ulReadModes", c_ulong),
            ("ulTriggerModes", c_ulong),
            ("ulCameraType", c_ulong),
            ("ulPixelMode", c_ulong),
            ("ulSetFunctions", c_ulong),
            ("ulGetFunctions", c_ulong),
            ("ulFeatures", c_ulong),
            ("ulPCICard", c_ulong),
            ("ulEMGainCapability", c_ulong),
            ("ulFTReadModes", c_ulong),
            ("ulFeatures2", c_ulong)]

# Function args 
camdll.Initialize.argtypes = [c_char_p]
camdll.GetCapabilities.argtypes = [POINTER(AndorCapabilities)]
camdll.GetHeadModel.argtypes = [c_char_p]
camdll.GetDetector.argtypes = [POINTER(c_int), POINTER(c_int)]
camdll.GetFastestRecommendedVSSpeed.argtypes = [POINTER(c_int), POINTER(c_float)]
camdll.SetVSSpeed.argtypes = [c_int]
camdll.GetNumberADChannels.argtypes = [POINTER(c_int)]
camdll.GetNumberHSSpeeds.argtypes = [c_int, c_int, POINTER(c_int)]
camdll.GetHSSpeed.argtypes = [c_int, c_int, c_int, POINTER(c_float)]
camdll.SetADChannel.argtypes = [c_int]
camdll.SetHSSpeed.argtypes = [c_int, c_int]
camdll.SetBaselineClamp.argtypes = [c_int]
camdll.GetBitDepth.argtypes = [c_int, POINTER(c_int)]
camdll.GetTemperatureRange.argtypes = [POINTER(c_int), POINTER(c_int)]
camdll.GetTemperatureF.argtypes = [POINTER(c_float)]
camdll.GetStatus.argtypes = [POINTER(c_int)]
camdll.SetTemperature.argtypes = [c_int]
camdll.SetFanMode.argtypes = [c_int]
camdll.SetReadMode.argtypes = [c_int]
camdll.SetImage.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int]
camdll.SetAcquisitionMode.argtypes = [c_int]
camdll.SetExposureTime.argtypes = [c_float]
camdll.GetAcquisitionTimings.argtypes = [POINTER(c_float), POINTER(c_float), POINTER(c_float)]
camdll.SetPreAmpGain.argtypes = [c_int]
camdll.GetEMGainRange.argtypes = [POINTER(c_int), POINTER(c_int)]
camdll.SetEMCCDGain.argtypes = [c_int]
camdll.GetEMCCDGain.argtypes = [POINTER(c_int)]
# camdll.GetAcquiredData16.argtypes = [POINTER(WORD), c_ulong]

class Andor_EMCCD():
    """Class Interface for Andor EMCCD"""
    
    _cooler_state_dict = {
        20075: 'System not initialized',
        20072: 'Acquisition in progress',
        20013: 'Unable to communicate with card',
        20034: 'OFF',
        20036: 'Stabilized',
        20037: 'Not React',
        20040: 'Drifed',
        20035: 'Not Stabilized',
    }

    _status_state_dict = {
        0: 'NULL',
        20073: 'IDLE',
        20074: 'Executing temperature cycle',
        20072: 'Acquiring',
        20023: 'Unable to meet accumulate cycle time',
        20022: 'Unable to meet Kinetic cycle time',
        20013: 'Unable to communicate with card',
        20018: 'Unable read data via required rate',
        20019: 'Camera memory going full',
        20026: 'Overflow of the spool buffer',
    }

    def __init__(self):
        self._connected = False
        
        # Init 
        if DRV_SUCCESS == camdll.Initialize(bytes(os.getcwd(), encoding='utf-8')):
            self._connected = True

        # Get Camera Capabilities
        self.caps = AndorCapabilities()
        self.caps.ulSize = sizeof(AndorCapabilities)
        camdll.GetCapabilities(byref(self.caps))
        
        # Get Head Model
        headModel = create_string_buffer(32)
        camdll.GetHeadModel(headModel)
        self.headModel = str(headModel.value, encoding='utf-8')

        # Get detector information
        gblXPixels, gblYPixels = c_int(), c_int()
        camdll.GetDetector(byref(gblXPixels), byref(gblYPixels))
        self.gblXPixels, self.gblYPixels = gblXPixels.value, gblYPixels.value

        # Set default read mode acquisition mode (not do here)

        # Set Vertical Speed to recommanded
        # Set Horizontal Speed to max
        VSNumber, HSNumber, ADNumber, BitDepth = c_int(), c_int(), c_int(), c_int()
        a_speed = c_float()
        camdll.GetFastestRecommendedVSSpeed(byref(VSNumber), byref(a_speed))
        camdll.SetVSSpeed(VSNumber)

        a_Stemp, a_nAD, a_index = c_float(), c_int(), c_int()
        camdll.GetNumberADChannels(byref(a_nAD))
        for i in range(a_nAD.value):
            camdll.GetNumberHSSpeeds(i, 0, byref(a_index))
            for iSpeed in range(a_index.value):
                camdll.GetHSSpeed(i, 0, iSpeed, byref(a_speed))
                if a_speed.value > a_Stemp.value:
                    a_Stemp = a_speed
                    HSNumber = iSpeed
                    ADNumber = i

        camdll.SetADChannel(ADNumber)
        camdll.SetHSSpeed(0, HSNumber)

        # AC_SETFUNCTION_BASELINECLAMP 0x20
        if self.caps.ulSetFunctions & 0x20:
            camdll.SetBaselineClamp(1)
        
        camdll.GetBitDepth(ADNumber, byref(BitDepth))

        self.VSNumber = VSNumber.value
        self.HSNumber = HSNumber
        self.ADNumber = ADNumber
        self.BitDepth = BitDepth.value

        # Set PreAmp Gain to 5x
        camdll.SetPreAmpGain(2)

        # Get EM Gain Range
        emgain_low, emgain_high = c_int(), c_int()
        camdll.GetEMGainRange(byref(emgain_low), byref(emgain_high))
        self.EMGain_Low = emgain_low.value
        self.EMGain_High = emgain_high.value

        # Get Temperature Control Range
        temp_min, temp_max = c_int(), c_int()
        camdll.GetTemperatureRange(byref(temp_min), byref(temp_max))
        self.temp_min = temp_min.value
        self.temp_max = temp_max.value

        # Set Readout Mode: Image - Full pixels
        self.setReadoutMode()

        # Set Acquisition Mode: Single Scan
        self.setAcquisitionMode()

    def __del__(self):
        self.coolerOFF()
        camdll.ShutDown()
        print('Shutdown')

    def available(self):
        return self._connected

    def getStatus(self):
        status = c_int()
        camdll.GetStatus(byref(status))
        return self._status_state_dict[status.value]

    def getTemperature(self):
        temperature = c_float()
        cooler_state = camdll.GetTemperatureF(byref(temperature))
        return temperature.value, self._cooler_state_dict[cooler_state]

    def setTemperature(self, temperature):
        return camdll.SetTemperature(temperature)

    def coolerON(self):
        return camdll.CoolerON()

    def coolerOFF(self):
        return camdll.CoolerOFF()

    def fanFullSpeed(self):
        return camdll.SetFanMode(0)
    
    def fanLowSpeed(self):
        return camdll.SetFanMode(1)

    def fanOFF(self):
        return camdll.SetFanMode(2)

    def setReadoutMode(self):
        """Set Readout Mode: Image"""
        camdll.SetReadMode(4)
        camdll.SetImage(1, 1, 1, self.gblXPixels, 1, self.gblYPixels)

    def setAcquisitionMode(self):
        """Set Acquisition Mode: Single-Scan"""
        camdll.SetAcquisitionMode(1)

    def setExposureTime(self, sec):
        """Set exposure time (sec) return truly setting value"""
        camdll.SetExposureTime(sec)
        exposureTime, no_use_1, no_use_2 = c_float(), c_float(), c_float()
        camdll.GetAcquisitionTimings(byref(exposureTime), byref(no_use_1), byref(no_use_2))
        return exposureTime.value

    def setEMGain(self, gain):
        if gain < self.EMGain_Low or gain > self.EMGain_High:
            return
        camdll.SetEMCCDGain(gain)

    def getEMGain(self):
        gain = c_int()
        camdll.GetEMCCDGain(byref(gain))
        return gain.value
        
    def startAcquisition(self):
        camdll.StartAcquisition()

    def isIDLE(self):
        return self.getStatus() == DRV_IDLE

    def acquireData(self):
        total_pixels = self.gblXPixels * self.gblYPixels
        pImageArray = (WORD * (total_pixels))()
        camdll.GetAcquiredData16(byref(pImageArray), total_pixels)
        # print(pImageArray[100])
        return np.ctypeslib.as_array(pImageArray).reshape((self.gblXPixels, self.gblYPixels))

    def abortAcquisition(self):
        return camdll.AbortAcquisition()


if __name__ == "__main__":
    cam = Andor_EMCCD()
    if cam.available():
        print("Camera Connected.")

        print("-- iXon+ EMCCD --")
        print(f"-- -- Head Model  : {cam.headModel}")
        print(f"-- -- Size of CCD : {cam.gblXPixels} * {cam.gblYPixels}")
        print(f"-- -- Bit Depth   : {cam.BitDepth}")

        a_speed = c_float()
        camdll.GetVSSpeed(cam.VSNumber, byref(a_speed))
        vs = round(a_speed.value, 2)
        print(f"-- -- Vertical Speed   : {vs} us / pixel shift")
        camdll.GetHSSpeed(cam.ADNumber, 0, cam.HSNumber, byref(a_speed))
        hs = a_speed.value
        print(f"-- -- Horizontal Speed : {hs} MHz")

        print(f"-- -- Temperature ~ {cam.temp_min} - {cam.temp_max}")

        temperature, cooler_state = cam.getTemperature()
        print(f'-- -- Current Temperature : {temperature}')
        print(f'-- -- Cooler State: {cooler_state}')

        status = cam.getStatus()
        print(f'-- -- Status : {status}')

        ret_code = cam.setTemperature(-20)
        print(f'-- -- Set Temperature ret code : {ret_code}')



        


        