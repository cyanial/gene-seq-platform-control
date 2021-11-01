"""
NikonTi Microscope Control.
  - TiScope SDK in Windows Component Object Model.
"""

import win32com.client as com

class nikonTi():
    """Definition class of NikonTi"""

    def __init__(self):
        """Init the nikonti"""
        self.instance = com.Dispatch("Nikon.TiScope.NikonTi")
        self.LU4ALaser = self.instance.LU4ALaser
        self.LightPathDrive = self.instance.LightPathDrive
        self.Nosepiece = self.instance.Nosepiece
        self.ZDrive = self.instance.ZDrive
        self.TIRF = self.instance.TIRF
        self.PFS = self.instance.PFS
        




if __name__ == "__main__":
    NikonTi = nikonTi()
    print("aaa")
