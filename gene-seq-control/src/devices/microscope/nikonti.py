"""
NikonTi Microscope Control.
  - TiScope SDK in Windows Component Object Model.

2021/11/07

"""

import win32com.client as com

class nikonTi():
    """Definition class of NikonTi"""

    def __init__(self):
        """Init the nikonti"""
        self._connected = False

        self.instance = com.Dispatch("Nikon.TiScope.NikonTi")
        self.LU4ALaser = self.instance.LU4ALaser
        self.LightPathDrive = self.instance.LightPathDrive
        self.Nosepiece = self.instance.Nosepiece
        self.ZDrive = self.instance.ZDrive
        self.TIRF = self.instance.TIRF
        self.PFS = self.instance.PFS
        # self.EpiShutter = self.instance.EpiShutter

        # Acquire zdrive parameters
        self.zdrive_lowerlimit = int(self.ZDrive.LowerLimit)
        self.zdrive_upperlimit = int(self.ZDrive.UpperLimit)
        self.zdrive_resolution = int(self.ZDrive.Resolution)
        self.zdrive_unit = str(self.ZDrive.Unit)
        self.zdrive_name = str(self.ZDrive.Name)

        # Acquire light path parameters 
        self.lightpath_name = str(self.LightPathDrive.Name)

        # Acquire nosepiece parameters

        # Setup LU4ALaser
        self.LU4ALaser.Connect(1)
        self.LU4ALaser.IsControlled = 1
        
        # Acquire TIRF parameters
        self.tirf_name = str(self.TIRF.name)
        self.tirf_lowerlimit = int(self.TIRF.LowerLimit)
        self.tirf_upperlimit = int(self.TIRF.UpperLimit)

        # Acquire PFS parameters
        self.pfs_name = str(self.PFS.Name)
        self.pfs_lowerlimit = int(self.PFS.LowerLimit)
        self.pfs_upperlimit = int(self.PFS.UpperLimit)

        self._connected = True

    def __del__(self):
        pass

    def available(self):
        return self._connected

    def zescape(self):
        """ZDrive Escape"""
        self.ZDrive.ZEscape()

    def refocus(self):
        """ZDrive Refocus"""
        self.ZDrive.Refocus()

    def zGetPos(self):
        return int(self.ZDrive.Position)

    def um_to_zpos(self, um):
        return int(um * 1000 / self.zdrive_resolution)

    def zpos_to_um(self, pos):
        return pos * self.zdrive_resolution / 1000

    def zMoveAbsolute(self, pos):
        if pos > self.zdrive_upperlimit or pos < self.zdrive_lowerlimit:
            return
        self.ZDrive.MoveAbsolute(pos)
    
    def zMoveRelative(self, pos):
        curr_pos = self.zGetPos()
        if curr_pos + pos > self.zdrive_upperlimit:
            return self.zMoveAbsolute(self.zdrive_upperlimit)
        if curr_pos + pos < self.zdrive_lowerlimit:
            return self.zMoveAbsolute(self.zdrive_lowerlimit)
        self.ZDrive.MoveRelative(pos)

    def isZEscape(self):
        return int(self.ZDrive.IsZEscape)

    def pfsStatus(self):
        return int(self.PFS.Status)

    def pfsIsEnable(self):
        return int(self.PFS.IsEnabled)

    def pfsPos(self):
        return int(self.PFS.Position)

    def pfsEnable(self):
        self.PFS.Enable()

    def pfsDisable(self):
        self.PFS.Disable()

    def pfsMoveAbsolute(self, pos):
        if pos > self.pfs_upperlimit or pos < self.pfs_lowerlimit:
            return
        self.PFS.MoveAbsolute(pos)

    def pfsMoveRelative(self, pos):
        curr_pos = self.pfsPos()
        if curr_pos + pos > self.pfs_upperlimit:
            return self.pfsMoveAbsolute(self.pfs_upperlimit)
        if curr_pos + pos < self.pfs_lowerlimit:
            return self.pfsMoveAbsolute(self.pfs_lowerlimit)
        self.PFS.MoveRelative(pos)

    def tirfPos(self):
        return int(self.TIRF.Position)

    def tirfIsInserted(self):
        return int(self.TIRF.IsInserted)

    def tirfInsert(self):
        self.TIRF.Insert()
    
    def tirfExtract(self):
        self.TIRF.Extract()
        
    def tirfMoveAbsolute(self, pos):
        if pos > self.tirf_upperlimit or pos < self.tirf_lowerlimit:
            return
        self.TIRF.MoveAbsolute(pos)

    def tirfMoveRealtive(self, pos):
        curr_pos = self.tirfPos()
        if curr_pos + pos > self.tirf_upperlimit:
            return self.tirfMoveAbsolute(self.tirf_upperlimit)
        if curr_pos + pos < self.tirf_lowerlimit:
            return self.tirfMoveAbsolute(self.tirf_upperlimit)
        self.TIRF.MoveRelative(pos)

    def shuterCtrl(self):
        # '0b11111' close all
        # '0b00000' open all
        pass



if __name__ == "__main__":
    mic = nikonTi()
    if mic.available():
        pass
