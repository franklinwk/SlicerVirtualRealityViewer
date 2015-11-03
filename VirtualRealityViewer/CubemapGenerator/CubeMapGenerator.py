from __main__ import vtk, qt, ctk, slicer

class CubemapGenerator:
  def __init__(self, parent):
    parent.title = "Cubemap Generator"
    parent.categories = ["VR"]
    parent.contributors = ["Franklin King"]
    parent.helpText = """
    Add help text
    """
    parent.acknowledgementText = """
""" 
    # module build directory is not the current directory when running the python script, hence why the usual method of finding resources didn't work ASAP
    self.parent = parent

#
# qLeapMotionIntegratorWidget
#
class CubemapGeneratorWidget:
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

    self.stereoMode = False
    self.followNode = None
    self.tag = None
    self.cubeFaceViewNodes = []
    self.cubeFaceThreeDWidgets = {}
    self.lightDirection = [0, -10, 0]
      
  def setup(self):
    # # Instantiate and connect widgets 
    # ---------------------------- Window Settings -----------------------------
    initializationCollapsibleButton = ctk.ctkCollapsibleButton()
    initializationCollapsibleButton.text = "Window Initialization"
    self.layout.addWidget(initializationCollapsibleButton)    
    initializationLayout = qt.QFormLayout(initializationCollapsibleButton)
    
    self.stereoCheckBox = qt.QCheckBox()
    initializationLayout.addRow("Stereoscopic mode:", self.stereoCheckBox)        
    
    self.startButton = qt.QPushButton("Create Windows")
    initializationLayout.addRow(self.startButton)
    
    self.showButton = qt.QPushButton("Show Windows")
    initializationLayout.addRow(self.showButton)
    
    self.hideButton = qt.QPushButton("Hide Windows")
    initializationLayout.addRow(self.hideButton)
    
    # ---------------------------- Stereo Settings -----------------------------
    stereoCollapsibleButton = ctk.ctkCollapsibleButton()
    stereoCollapsibleButton.text = "Stereoscopic Settings"
    self.layout.addWidget(stereoCollapsibleButton)
    stereoSettingsLayout = qt.QFormLayout(stereoCollapsibleButton)        
    
    self.upViewAngleButton = qt.QPushButton("Increase View Angle")
    stereoSettingsLayout.addWidget(self.upViewAngleButton)
    
    self.downViewAngleButton = qt.QPushButton("Decrease View Angle")
    stereoSettingsLayout.addWidget(self.downViewAngleButton)
    
    # ---------------------------- Update Settings -----------------------------
    updatesCollapsibleButton = ctk.ctkCollapsibleButton()
    updatesCollapsibleButton.text = "Update Settings"
    self.layout.addWidget(updatesCollapsibleButton)
    updateSettingsLayout = qt.QFormLayout(updatesCollapsibleButton)
    
    self.followNodeSelector = slicer.qMRMLNodeComboBox()
    self.followNodeSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode", "vtkMRMLLinearTransformNode"]
    self.followNodeSelector.selectNodeUponCreation = False
    self.followNodeSelector.addEnabled = False
    self.followNodeSelector.showHidden = False
    self.followNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.followNodeSelector.setToolTip( "Pick Fiducial Node or Linear Transform to follow" )
    updateSettingsLayout.addWidget(self.followNodeSelector)
    
    self.createButton = qt.QPushButton("Create Image")
    updateSettingsLayout.addWidget(self.createButton)
    
    self.startRepeatButton = qt.QPushButton("Continually Create Images")
    updateSettingsLayout.addWidget(self.startRepeatButton)

    self.stopRepeatButton = qt.QPushButton("Stop Creating Images")
    updateSettingsLayout.addWidget(self.stopRepeatButton)
    
    # ---------------------------- Lighting Settings -----------------------------
    lightingCollapsibleButton = ctk.ctkCollapsibleButton()
    lightingCollapsibleButton.text = "Lighting Settings"
    self.layout.addWidget(lightingCollapsibleButton)
    lightingSettingsLayout = qt.QFormLayout(lightingCollapsibleButton)
    
    self.lightSliderX = ctk.ctkSliderWidget()
    self.lightSliderX.maximum = 500
    self.lightSliderX.minimum = -500
    self.lightSliderX.value = 0
    self.lightSliderX.tracking = True
    lightingSettingsLayout.addRow("X", self.lightSliderX)
    
    self.lightSliderY = ctk.ctkSliderWidget()
    self.lightSliderY.maximum = 500
    self.lightSliderY.minimum = -500
    self.lightSliderY.value = -10
    self.lightSliderY.tracking = True
    lightingSettingsLayout.addRow("Y", self.lightSliderY)

    self.lightSliderZ = ctk.ctkSliderWidget()
    self.lightSliderZ.maximum = 500
    self.lightSliderZ.minimum = -500
    self.lightSliderZ.value = 0
    self.lightSliderZ.tracking = True
    lightingSettingsLayout.addRow("Z", self.lightSliderZ)    
    
    # # Connections
    self.startButton.connect('clicked(bool)', self.createWindows)
    self.showButton.connect('clicked(bool)', self.showWindows)
    self.hideButton.connect('clicked(bool)', self.hideWindows)
    
    self.upViewAngleButton.connect('clicked(bool)', self.upViewAngle)
    self.downViewAngleButton.connect('clicked(bool)', self.downViewAngle)    
    
    self.createButton.connect('clicked(bool)', self.createWindowImages)
    self.startRepeatButton.connect('clicked(bool)', self.startCreatingImages)
    self.stopRepeatButton.connect('clicked(bool)', self.stopCreatingImages)
    
    self.followNodeSelector.connect('currentNodeChanged(bool)', self.setFollowNode)
    
    self.lightSliderX.connect('valueChanged(double)', self.onLightSliderChanged)
    self.lightSliderY.connect('valueChanged(double)', self.onLightSliderChanged)
    self.lightSliderZ.connect('valueChanged(double)', self.onLightSliderChanged)
    

    self.timer = qt.QTimer()
    self.timer.timeout.connect(self.createWindowImages)
    
    self.layout.addStretch(1)
    
  def createWindows(self):
    self.stereoMode = self.stereoCheckBox.isChecked()
  
    # Create widgets to hold windows
    self.leftWidgets = qt.QWidget()
    self.leftWidgets.setWindowTitle("SlicerCubeMap - Left")
    leftWidgetsLayout = qt.QHBoxLayout()
    leftWidgetsLayout.setSpacing(0)
    leftWidgetsLayout.setContentsMargins(0,0,0,0)
    self.leftWidgets.setLayout(leftWidgetsLayout)
    self.rightWidgets = qt.QWidget()
    self.rightWidgets.setWindowTitle("SlicerCubeMap - Right")
    rightWidgetsLayout = qt.QHBoxLayout()
    rightWidgetsLayout.setSpacing(0)
    rightWidgetsLayout.setContentsMargins(0,0,0,0)
    self.rightWidgets.setLayout(rightWidgetsLayout)
  
    # Per cube face per eye
    leftFaces  = ["lpx", "lnz", "lnx", "lpz", "lpy", "lny"]
    rightFaces = ["rpx", "rnz", "rnx", "rpz", "rpy", "rny"]
    
    slicer.mrmlScene.AddNode(slicer.vtkMRMLViewNode()) # There's some wonky behaviour with the first view node created (ViewNode2?), so this terrible thing exists for now
    for face in leftFaces:
      # Initialize View Nodes
      view = slicer.vtkMRMLViewNode()
      slicer.mrmlScene.AddNode(view)
      self.cubeFaceViewNodes.append(view)
      
      # Initialize ThreeD Widgets
      threeDWidget = slicer.qMRMLThreeDWidget()
      threeDWidget.setFixedSize(qt.QSize(600, 600))
      threeDWidget.setMRMLViewNode(view)
      threeDWidget.setMRMLScene(slicer.mrmlScene)
      threeDWidget.setWindowTitle("SlicerCubeMap - " + face)
      threeDWidget.children()[1].hide() # Hide widget controller bar; TODO: maybe a bit more robust
      self.cubeFaceThreeDWidgets[face] = threeDWidget
      
      # Set Stereo settings
      if (self.stereoCheckBox.isChecked()):
        threeDWidget.threeDView().renderWindow().StereoRenderOn()
        threeDWidget.threeDView().renderWindow().SetStereoTypeToLeft()
      threeDWidget.threeDView().renderWindow().Render()
      
      # Add to Left eye cubemap widget
      self.leftWidgets.layout().addWidget(threeDWidget)
    
    if (self.stereoMode is True):  
      for face in rightFaces:
        # Initialize View Nodes
        view = slicer.vtkMRMLViewNode()
        slicer.mrmlScene.AddNode(view)
        self.cubeFaceViewNodes.append(view)
        
        # Initialize ThreeD Widgets
        threeDWidget = slicer.qMRMLThreeDWidget()
        threeDWidget.setFixedSize(qt.QSize(600, 600))
        threeDWidget.setMRMLViewNode(view)
        threeDWidget.setMRMLScene(slicer.mrmlScene)
        threeDWidget.setWindowTitle("SlicerCubeMap - " + face)
        threeDWidget.children()[1].hide() # Hide widget controller bar; TODO: maybe a bit more robust
        self.cubeFaceThreeDWidgets[face] = threeDWidget
      
        # Set Stereo settings
        threeDWidget.threeDView().renderWindow().StereoRenderOn()
        threeDWidget.threeDView().renderWindow().SetStereoTypeToRight()
        threeDWidget.threeDView().renderWindow().Render()
        
        # Add to Right eye cubemap widget
        self.rightWidgets.layout().addWidget(threeDWidget)      
    
    # Set background colors depending on face
    # Front, Left, Right, and Back retain default color gradient
    # Top and Bottom have opposite sides of the gradient
    self.cubeFaceThreeDWidgets["lny"].threeDView().setBackgroundColor(qt.QColor(193, 195, 232))
    self.cubeFaceThreeDWidgets["lny"].threeDView().setBackgroundColor2(qt.QColor(193, 195, 232))
    self.cubeFaceThreeDWidgets["lpy"].threeDView().setBackgroundColor(qt.QColor(116, 120, 190))
    self.cubeFaceThreeDWidgets["lpy"].threeDView().setBackgroundColor2(qt.QColor(116, 120, 190))
    
    if (self.stereoMode is True):
      self.cubeFaceThreeDWidgets["rny"].threeDView().setBackgroundColor(qt.QColor(193, 195, 232))
      self.cubeFaceThreeDWidgets["rny"].threeDView().setBackgroundColor2(qt.QColor(193, 195, 232))    
      self.cubeFaceThreeDWidgets["rpy"].threeDView().setBackgroundColor(qt.QColor(116, 120, 190))
      self.cubeFaceThreeDWidgets["rpy"].threeDView().setBackgroundColor2(qt.QColor(116, 120, 190))
    
    # self.cubeFaceThreeDWidgets["lpx"].threeDView().setBackgroundColor(qt.QColor(qt.Qt.black))
    # self.cubeFaceThreeDWidgets["lnz"].threeDView().setBackgroundColor(qt.QColor(qt.Qt.white))
    # self.cubeFaceThreeDWidgets["lnx"].threeDView().setBackgroundColor(qt.QColor(qt.Qt.green))
    # self.cubeFaceThreeDWidgets["lpz"].threeDView().setBackgroundColor(qt.QColor(qt.Qt.red))
    # self.cubeFaceThreeDWidgets["lpy"].threeDView().setBackgroundColor(qt.QColor(qt.Qt.blue))
    # self.cubeFaceThreeDWidgets["lny"].threeDView().setBackgroundColor(qt.QColor(qt.Qt.yellow))
    
    # Add fiducial location
    self.setFollowNode()
    
  
  def setCubeFaceCameras(self, position):
    if (len(self.cubeFaceThreeDWidgets) > 0):
      # Position and orient cameras for each ThreeD Widget
      # Left Eye Front - lpx
      lpxCam = self.cubeFaceThreeDWidgets["lpx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      self.initializeCubeFaceCamera(lpxCam, position)
      
      # Left Eye Right - lnz
      lnzCam = self.cubeFaceThreeDWidgets["lnz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      self.initializeCubeFaceCamera(lnzCam, position)
      lnzCam.Yaw(270)
      
      # Left Eye Back - lnx
      lnxCam = self.cubeFaceThreeDWidgets["lnx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      self.initializeCubeFaceCamera(lnxCam, position)
      lnxCam.Yaw(180)
      
      # Left Eye Left - lpz
      lpzCam = self.cubeFaceThreeDWidgets["lpz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      self.initializeCubeFaceCamera(lpzCam, position)
      lpzCam.Yaw(90)
      
      # Left Eye Top - lpy
      lpyCam = self.cubeFaceThreeDWidgets["lpy"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      self.initializeCubeFaceCamera(lpyCam, position)
      #lpyCam.SetFocalPoint(position[0], position[1], position[2] + 0.05)
      lpyCam.Pitch(89.9)
      
      # Left Eye Bottom - lny
      lnyCam = self.cubeFaceThreeDWidgets["lny"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      self.initializeCubeFaceCamera(lnyCam, position)
      #lnyCam.SetFocalPoint(position[0], position[1], position[2] - 0.05)
      lnyCam.Pitch(-89.9)
      
      if (self.stereoMode is True):
        # Right Eye Front - rpx
        rpxCam = self.cubeFaceThreeDWidgets["rpx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
        self.initializeCubeFaceCamera(rpxCam, position)
        
        # Right Eye Right - rnz
        rnzCam = self.cubeFaceThreeDWidgets["rnz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
        self.initializeCubeFaceCamera(rnzCam, position)
        rnzCam.Yaw(270)
        
        # Right Eye Back - rnx
        rnxCam = self.cubeFaceThreeDWidgets["rnx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
        self.initializeCubeFaceCamera(rnxCam, position)
        rnxCam.Yaw(180)

        # Right Eye Left - rpz
        rpzCam = self.cubeFaceThreeDWidgets["rpz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
        self.initializeCubeFaceCamera(rpzCam, position)
        rpzCam.Yaw(90)
        
        # Right Eye Top - rpy
        rpyCam = self.cubeFaceThreeDWidgets["rpy"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
        self.initializeCubeFaceCamera(rpyCam, position)
        #rpyCam.SetFocalPoint(position[0], position[1], position[2] - 0.05)
        rpyCam.Pitch(90)
        
        # Right Eye Bottom - rny
        rnyCam = self.cubeFaceThreeDWidgets["rny"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
        self.initializeCubeFaceCamera(rnyCam, position)
        #rnyCam.SetFocalPoint(position[0], position[1], position[2] + 0.05)
        rnyCam.Pitch(-90)

      self.setLighting(self.lightDirection)

  def onLightSliderChanged(self, unused):
    self.lightDirection = [self.lightSliderX.value, self.lightSliderY.value, self.lightSliderZ.value]
    
  
  def setLighting(self, lightDirection):
    # Synchronize Lights
    for face in self.cubeFaceThreeDWidgets:
      self.cubeFaceThreeDWidgets[face].threeDView().renderWindow().Render()
      light = self.cubeFaceThreeDWidgets[face].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetLights().GetItemAsObject(0)
      light.SetLightTypeToSceneLight()
      light.SetFocalPoint(lightDirection[0], lightDirection[1], lightDirection[2])
  
  def initializeCubeFaceCamera(self, camera, position):
    camera.SetPosition(position[0], position[1], position[2])
    camera.SetFocalPoint(position[0], position[1] + 0.01, position[2])
    camera.SetViewUp(0, 0, 1)
    camera.UseHorizontalViewAngleOn()
    camera.SetViewAngle(90) # Increase for stereo projection and cut later (TODO)
    camera.SetClippingRange(0.1, 800)
    camera.SetEyeAngle(0) # Not set up for stereo yet
    #camera.UseOffAxisProjectionOn()
  
  def setFollowNode(self):
    # Remove old observer if one exists
    if (self.followNode and self.tag):
      self.followNode.RemoveObserver(self.tag)
    
    # Get new node and add new observers
    self.followNode = self.followNodeSelector.currentNode()
    if (self.followNode):
      if (self.followNode.GetClassName() == "vtkMRMLLinearTransformNode"):
        self.updatePositionFromTransform(self.followNode, 0)
        self.tag = self.followNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.updatePositionFromTransform)
      elif (self.followNode.GetClassName() == "vtkMRMLMarkupsFiducialNode"):
        #self.updatePositionFromFiducial(self.followNode, 0)
        self.tag = self.followNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updatePositionFromFiducial)
        self.followNode.Modified()
    else:
      position= [0,0,0]
      self.setCubeFaceCameras(position)
    
  def updatePositionFromTransform(self, followNode, eventId):
    if (followNode):
      position = [0,0,0]
      matrix = vtk.vtkMatrix4x4()
      followNode.GetMatrixTransformToParent(matrix)
      position[0] = matrix.GetElement(0,3)
      position[1] = matrix.GetElement(1,3)
      position[2] = matrix.GetElement(2,3)
      self.setCubeFaceCameras(position)

  def updatePositionFromFiducial(self, followNode, eventId):
    if (followNode):
      position = [0,0,0]
      followNode.GetNthFiducialPosition(0, position)
      self.setCubeFaceCameras(position)
  
  def showWindows(self):
    self.leftWidgets.showNormal()
    if (self.stereoMode is True):
      self.rightWidgets.showNormal()
    #for face in self.cubeFaceThreeDWidgets:
    #  self.cubeFaceThreeDWidgets[face].showNormal()
      
  def hideWindows(self):
    self.leftWidgets.hide()
    if (self.stereoMode is True):
      self.rightWidgets.hide()
    #for face in self.cubeFaceThreeDWidgets:
    #  self.cubeFaceThreeDWidgets[face].hide()
      
  # Temporary proof of concept implementation:
  def createWindowImages(self):
    widgetPixmapL = qt.QPixmap.grabWidget(self.leftWidgets)
    file = qt.QFile("C:/Work/data/left.jpg")
    file.open(qt.QIODevice.WriteOnly)
    widgetPixmapL.save(file, "JPEG", 100)
    
    if (self.stereoMode is True):
      widgetPixmapR = qt.QPixmap.grabWidget(self.rightWidgets)
      fileR = qt.QFile("C:/Work/data/right.jpg")
      fileR.open(qt.QIODevice.WriteOnly)
      widgetPixmapR.save(fileR, "JPEG", 100)
    
  def startCreatingImages(self):
    self.timer.start(500)
    
  def stopCreatingImages(self):
    self.timer.stop()
    
  def upViewAngle(self):
    for face in self.cubeFaceThreeDWidgets:
      camera = self.cubeFaceThreeDWidgets[face].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      camera.SetEyeAngle(camera.GetEyeAngle() + 2.0)
      print (camera.GetEyeAngle())
      #camera.SetEyeSeparation(camera.GetEyeSeparation() + 0.01)
      #print (camera.GetEyeSeparation())      
    
  def downViewAngle(self):
    for face in self.cubeFaceThreeDWidgets:
      camera = self.cubeFaceThreeDWidgets[face].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
      camera.SetEyeAngle(camera.GetEyeAngle() - 2.0)
      print (camera.GetEyeAngle())
      #camera.SetEyeSeparation(camera.GetEyeSeparation() - 0.01)
      #print (camera.GetEyeSeparation())      
  
class CubemapGeneratorLogic:
  def __init__(self):
    pass
 
  


