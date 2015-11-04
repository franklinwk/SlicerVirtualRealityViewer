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
    self.followTag = None
    self.oculusNode = None
    self.oculusTag = None
    self.cubeFaceViewNodes = []
    self.cubeFaceThreeDWidgets = {}
    self.lightDirection = [0, 0, 300, 0]
  
  def __del__(self):
    for face in self.cubeFaceThreeDWidgets:
      del self.cubeFaceThreeDWidgets[face]
  
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
    
    # ------------------- Transform and Tracking Settings ----------------------
    trackingCollapsibleButton = ctk.ctkCollapsibleButton()
    trackingCollapsibleButton.text = "Update Settings"
    self.layout.addWidget(trackingCollapsibleButton)
    trackingSettingsLayout = qt.QFormLayout(trackingCollapsibleButton)    
    
    self.followNodeSelector = slicer.qMRMLNodeComboBox()
    self.followNodeSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode", "vtkMRMLLinearTransformNode"]
    self.followNodeSelector.selectNodeUponCreation = False
    self.followNodeSelector.noneEnabled = False
    self.followNodeSelector.addEnabled = True
    self.followNodeSelector.showHidden = False
    self.followNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.followNodeSelector.setToolTip( "Pick Fiducial Node or Linear Transform to follow" )
    trackingSettingsLayout.addRow("Path node (transform or fiducial)", self.followNodeSelector)
    
    self.oculusNodeSelector = slicer.qMRMLNodeComboBox()
    self.oculusNodeSelector.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.oculusNodeSelector.selectNodeUponCreation = False
    self.oculusNodeSelector.noneEnabled = False
    self.oculusNodeSelector.addEnabled = True
    self.oculusNodeSelector.showHidden = False
    self.oculusNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.oculusNodeSelector.setToolTip( "Pick Transform for Oculus Rift" )
    trackingSettingsLayout.addRow("Oculus Transform", self.oculusNodeSelector)

    self.updateTrackingButton = qt.QPushButton("Update Tracking")
    trackingSettingsLayout.addWidget(self.updateTrackingButton)
    
    # ---------------------------- Update Export Image Settings -----------------------------
    updatesCollapsibleButton = ctk.ctkCollapsibleButton()
    updatesCollapsibleButton.text = "Update Settings"
    self.layout.addWidget(updatesCollapsibleButton)
    updateSettingsLayout = qt.QFormLayout(updatesCollapsibleButton)
    
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
    
    #       ----- Manual Lighting Control ------
    manualLightingGroupBox = ctk.ctkCollapsibleGroupBox()
    lightingSettingsLayout.addWidget(manualLightingGroupBox)
    manualLightingLayout = qt.QFormLayout(manualLightingGroupBox)
    
    self.lightSliderX = ctk.ctkSliderWidget()
    self.lightSliderX.maximum = 500
    self.lightSliderX.minimum = -500
    self.lightSliderX.value = 0
    self.lightSliderX.tracking = True
    manualLightingLayout.addRow("X", self.lightSliderX)
    
    self.lightSliderY = ctk.ctkSliderWidget()
    self.lightSliderY.maximum = 500
    self.lightSliderY.minimum = -500
    self.lightSliderY.value = 0
    self.lightSliderY.tracking = True
    manualLightingLayout.addRow("Y", self.lightSliderY)

    self.lightSliderZ = ctk.ctkSliderWidget()
    self.lightSliderZ.maximum = 500
    self.lightSliderZ.minimum = -500
    self.lightSliderZ.value = 300
    self.lightSliderZ.tracking = True
    manualLightingLayout.addRow("Z", self.lightSliderZ)    
    
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
    self.updateTrackingButton.connect('clicked(bool)', self.updateTracking)   
    
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
    
  
  def setCubeFaceCameras(self, position):
    if (len(self.cubeFaceThreeDWidgets) > 0):
      oculusMatrix = vtk.vtkMatrix4x4()
      self.oculusNode.GetMatrixTransformToWorld(oculusMatrix)
      position[0] = position[0] + oculusMatrix.GetElement(0,3)
      position[1] = position[1] + oculusMatrix.GetElement(1,3)
      position[2] = position[2] + oculusMatrix.GetElement(2,3)
      
      # Not sure why this is needed 
      # TODO: remove once figured out
      oculusMatrixToParent = vtk.vtkMatrix4x4()
      self.oculusNode.GetMatrixTransformToParent(oculusMatrixToParent)
      lightingMatrix = vtk.vtkMatrix4x4()
      lightingMatrix = vtk.vtkMatrix4x4()
      lightingMatrix.SetElement(0,0,oculusMatrixToParent.GetElement(0,0))
      lightingMatrix.SetElement(0,1,oculusMatrixToParent.GetElement(0,2))
      lightingMatrix.SetElement(0,2,oculusMatrixToParent.GetElement(0,1))
      lightingMatrix.SetElement(0,3,0)
      lightingMatrix.SetElement(1,0,oculusMatrixToParent.GetElement(1,0))
      lightingMatrix.SetElement(1,1,oculusMatrixToParent.GetElement(1,2))
      lightingMatrix.SetElement(1,2,oculusMatrixToParent.GetElement(1,1))
      lightingMatrix.SetElement(1,3,0)
      lightingMatrix.SetElement(2,0,oculusMatrixToParent.GetElement(2,0))
      lightingMatrix.SetElement(2,1,oculusMatrixToParent.GetElement(2,2))
      lightingMatrix.SetElement(2,2,oculusMatrixToParent.GetElement(2,1))
      lightingMatrix.SetElement(2,3,0)
      lightingMatrix.SetElement(3,0,0)
      lightingMatrix.SetElement(3,1,0)
      lightingMatrix.SetElement(3,2,0)
      lightingMatrix.SetElement(3,3,1)
      
      currentLightDirection = [0,0,0,0]
      oculusMatrix.SetElement(0,3,0)
      oculusMatrix.SetElement(1,3,0)
      oculusMatrix.SetElement(2,3,0)      
      oculusMatrix.MultiplyPoint(self.lightDirection, currentLightDirection)   

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

      self.setLighting(currentLightDirection)

  def onLightSliderChanged(self, unused):
    self.lightDirection = [self.lightSliderX.value, self.lightSliderY.value, self.lightSliderZ.value, 0]
    
  
  def setLighting(self, lightDirection):
    # Synchronize Lights
    for face in self.cubeFaceThreeDWidgets:
      self.cubeFaceThreeDWidgets[face].threeDView().renderWindow().Render()
      light = self.cubeFaceThreeDWidgets[face].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetLights().GetItemAsObject(0)
      light.SetLightTypeToSceneLight()
      light.SetConeAngle(140)
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
  
  def setOculusNode(self):
    if (self.oculusNode and self.oculusTag):
      self.oculusNode.RemoveObserver(self.oculusTag)
      
    # Get new node and add new observers
    # The same observer needs to be added to the Oculus node for when there is head movement but no path movement
    self.oculusNode = self.oculusNodeSelector.currentNode()
    if (self.oculusNode):
      if (self.followNode and self.followTag):
        self.followNode.RemoveObserver(self.followTag)    
    
      self.followNode = self.followNodeSelector.currentNode()
      if (self.followNode):
        if (self.followNode.GetClassName() == "vtkMRMLLinearTransformNode"):
          self.oculusTag = self.oculusNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.updateOculusWithTransformFollowNode)
        elif (self.followNode.GetClassName() == "vtkMRMLMarkupsFiducialNode"):
          self.oculusTag = self.oculusNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateOculusWithFiducialollowNode) 
  
  def setFollowNode(self):
    if (self.followNode and self.followTag):
      self.followNode.RemoveObserver(self.followTag)
    # Get new node and add new observers
    self.followNode = self.followNodeSelector.currentNode()
    if (self.followNode):
      if (self.followNode.GetClassName() == "vtkMRMLLinearTransformNode"):
        self.updatePositionFromTransform(self.followNode, 0)
        self.followTag = self.followNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.updatePositionFromTransform)
      elif (self.followNode.GetClassName() == "vtkMRMLMarkupsFiducialNode"):
        self.updatePositionFromFiducial(self.followNode, 0)
        self.followTag = self.followNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updatePositionFromFiducial)
  
  def updateOculusWithTransformFollowNode(self, oculusNode, eventId):
    self.updatePositionFromTransform(self.followNode, 0)
    
  def updateOculusWithFiducialollowNode(self, oculusNode, eventId):
    self.updatePositionFromFiducial(self.followNode, 0)
  
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
  
  def updateTracking(self):
    if (self.oculusNode and self.oculusTag):
      self.oculusNode.RemoveObserver(self.oculusTag)
    if (self.followNode and self.followTag):
      self.followNode.RemoveObserver(self.followTag)

    self.followNode = self.followNodeSelector.currentNode()
    self.oculusNode = self.oculusNodeSelector.currentNode()
    if (self.followNode and self.oculusNode):
      if (self.followNode.GetClassName() == "vtkMRMLLinearTransformNode"):
        self.updatePositionFromTransform(self.followNode, 0)
        self.followTag = self.followNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.updatePositionFromTransform)
        self.oculusTag = self.oculusNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.updateOculusWithTransformFollowNode)
        self.updateOculusWithTransformFollowNode(self.oculusNode, 0)
      elif (self.followNode.GetClassName() == "vtkMRMLMarkupsFiducialNode"):
        self.updatePositionFromFiducial(self.followNode, 0)
        self.followTag = self.followNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updatePositionFromFiducial)    
        self.oculusTag = self.oculusNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateOculusWithFiducialollowNode)
        self.updateOculusWithFiducialollowNode(self.oculusNode, 0)
    else:
      print "Requires both an Oculus Transform node and a Follow (Fiducial or Transform) node to be selected"
    
  
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
 
  


