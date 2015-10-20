from __main__ import vtk, qt, ctk, slicer

class StereoWindows:
  def __init__(self, parent):
    parent.title = "Stereo Windows"
    parent.categories = ["VR"]
    parent.contributors = ["Franklin King (Queen's University)"]
    parent.helpText = """
    Add help text
    """
    parent.acknowledgementText = """
    This work was funded by Cancer Care Ontario and the Ontario Consortium for Adaptive Interventions in Radiation Oncology (OCAIRO)
""" 
    # module build directory is not the current directory when running the python script, hence why the usual method of finding resources didn't work ASAP
    self.parent = parent

#
# qLeapMotionIntegratorWidget
#
class StereoWindowsWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    self.lastCommandId = 0
    self.timeoutCounter = 0
    if not parent:
      self.setup()
      self.parent.show()

      
  def setup(self):
    # # Instantiate and connect widgets
   
    self.viewNodeSelector = slicer.qMRMLNodeComboBox()
    self.viewNodeSelector.nodeTypes = ( ("vtkMRMLViewNode"), "" )
    self.viewNodeSelector.selectNodeUponCreation = True
    self.viewNodeSelector.addEnabled = False
    self.viewNodeSelector.showHidden = False
    self.viewNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.viewNodeSelector.setToolTip( "Pick View node" )
    self.layout.addWidget(self.viewNodeSelector) 
    
    self.startButton = qt.QPushButton("Create Windows")
    self.layout.addWidget(self.startButton)
    
    self.showButton = qt.QPushButton("Show Windows")
    self.layout.addWidget(self.showButton)    
    
    self.hideButton = qt.QPushButton("Hide Windows")
    self.layout.addWidget(self.hideButton)        
    
    self.startButton.connect('clicked(bool)', self.createWindows)
    self.showButton.connect('clicked(bool)', self.showWindows)
    self.hideButton.connect('clicked(bool)', self.hideWindows)
    
    self.riftWindowL = slicer.qMRMLThreeDWidget()
    self.riftWindowR = slicer.qMRMLThreeDWidget()
    
    
    self.cameraNodeSelector = slicer.qMRMLNodeComboBox()
    self.cameraNodeSelector.nodeTypes = ( ("vtkMRMLCameraNode"), "" )
    self.cameraNodeSelector.selectNodeUponCreation = True
    self.cameraNodeSelector.addEnabled = False
    self.cameraNodeSelector.showHidden = False
    self.cameraNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.cameraNodeSelector.setToolTip( "Pick Camera node" )
    self.layout.addWidget(self.cameraNodeSelector)
    
    self.increaseButton = qt.QPushButton("Increase Eye Separation")
    self.layout.addWidget(self.increaseButton)
    self.decreaseButton = qt.QPushButton("Decrease Eye Separation")
    self.layout.addWidget(self.decreaseButton)     
    
    self.increaseButton.connect('clicked(bool)', self.increaseSeparation)
    self.decreaseButton.connect('clicked(bool)', self.decreaseSeparation)    
    
    self.layout.addStretch(1)
    

  def createWindows(self):
    self.riftWindowL.setMRMLViewNode(self.viewNodeSelector.currentNode())
    self.riftWindowL.setMRMLScene(slicer.mrmlScene)
    self.riftWindowL.setFixedSize(qt.QSize(400,400))
    self.riftWindowL.showNormal()
    self.riftWindowL.setWindowTitle("Left 3D Widget")
    renderWindowL = self.riftWindowL.threeDView().renderWindow()
    renderWindowL.StereoRenderOn()
    renderWindowL.SetStereoTypeToLeft()
    #renderWindowL.StereoUpdate()
    renderWindowL.Render() 

    self.riftWindowR.setMRMLViewNode(self.viewNodeSelector.currentNode())
    self.riftWindowR.setMRMLScene(slicer.mrmlScene)
    self.riftWindowR.setFixedSize(qt.QSize(400,400))
    self.riftWindowR.showNormal()
    self.riftWindowR.setWindowTitle("Right 3D Widget")
    renderWindowR = self.riftWindowR.threeDView().renderWindow()
    renderWindowR.StereoRenderOn()
    renderWindowR.SetStereoTypeToRight()
    #renderWindowR.StereoUpdate()
    renderWindowR.Render()
    
  def showWindows(self):
    self.riftWindowL.showNormal()
    self.riftWindowR.showNormal()
    
  def hideWindows(self):
    self.riftWindowL.hide()
    self.riftWindowR.hide()    
  
  def increaseSeparation(self):
    camera = self.cameraNodeSelector.currentNode().GetCamera()
    #camera.SetEyeSeparation(camera.GetEyeSeparation() + 10)
    camera.SetEyeAngle(camera.GetEyeAngle() + 1.0)
    print camera.GetEyeSeparation()
    
  def decreaseSeparation(self):  
    camera = self.cameraNodeSelector.currentNode().GetCamera()
    #camera.SetEyeSeparation(camera.GetEyeSeparation() - 10)  
    camera.SetEyeAngle(camera.GetEyeAngle() - 1.0)
  
class StereoWindowsLogic:
  def __init__(self):
    pass
 
  


