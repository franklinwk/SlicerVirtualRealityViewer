from __main__ import vtk, qt, ctk, slicer

class VirtualRealityViewer:
  def __init__(self, parent):
    parent.title = "Virtual Reality Viewer"
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
class VirtualRealityViewerWidget:
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
    self.startButton = qt.QPushButton("Create Windows")
    self.layout.addWidget(self.startButton)
    
    self.showButton = qt.QPushButton("Show Windows")
    self.layout.addWidget(self.showButton)
    
    self.hideButton = qt.QPushButton("Hide Windows")
    self.layout.addWidget(self.hideButton)
    
    
    # ----------------------------
    
    
    self.createButton = qt.QPushButton("Create Image")
    self.layout.addWidget(self.createButton)
    
    self.startRepeatButton = qt.QPushButton("Continually Create Images")
    self.layout.addWidget(self.startRepeatButton)

    self.stopRepeatButton = qt.QPushButton("Stop Creating Images")
    self.layout.addWidget(self.stopRepeatButton)       
    
    self.startButton.connect('clicked(bool)', self.createWindows)
    self.showButton.connect('clicked(bool)', self.showWindows)
    self.hideButton.connect('clicked(bool)', self.hideWindows)
    
    self.createButton.connect('clicked(bool)', self.createWindowImages)
    self.startRepeatButton.connect('clicked(bool)', self.startCreatingImages)
    self.stopRepeatButton.connect('clicked(bool)', self.stopCreatingImages)
    
    self.timer = qt.QTimer()
    self.timer.timeout.connect(self.createWindowImages)
    
    self.layout.addStretch(1)
    
  def createWindows(self):
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
    self.cubeFaceViewNodes = []
    self.cubeFaceThreeDWidgets = {}
    for face in leftFaces:
      # Initialize View Nodes
      view = slicer.vtkMRMLViewNode()
      slicer.mrmlScene.AddNode(view)
      self.cubeFaceViewNodes.append(view)
      
      # Initialize ThreeD Widgets
      threeDWidget = slicer.qMRMLThreeDWidget()
      threeDWidget.setFixedSize(qt.QSize(450, 450))
      threeDWidget.setMRMLViewNode(view)
      threeDWidget.setMRMLScene(slicer.mrmlScene)
      threeDWidget.setWindowTitle("SlicerCubeMap - " + face)
      threeDWidget.children()[1].hide() # Hide widget controller bar; TODO: maybe a bit more robust
      self.cubeFaceThreeDWidgets[face] = threeDWidget
      
      # Set Stereo settings
      threeDWidget.threeDView().renderWindow().StereoRenderOn()
      threeDWidget.threeDView().renderWindow().SetStereoTypeToLeft()
      threeDWidget.threeDView().renderWindow().Render()
      
      # Add to Left eye cubemap widget
      self.leftWidgets.layout().addWidget(threeDWidget)
    
    for face in rightFaces:
      # Initialize View Nodes
      view = slicer.vtkMRMLViewNode()
      slicer.mrmlScene.AddNode(view)
      self.cubeFaceViewNodes.append(view)
      
      # Initialize ThreeD Widgets
      threeDWidget = slicer.qMRMLThreeDWidget()
      threeDWidget.setFixedSize(qt.QSize(450, 450))
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
    
    # Add fiducial location
    
    
    # Set background colors depending on face
    # Front, Left, Right, and Back retain default color gradient
    # Top and Bottom have opposite sides of the gradient
    self.cubeFaceThreeDWidgets["lny"].threeDView().setBackgroundColor(qt.QColor(193, 195, 232))
    self.cubeFaceThreeDWidgets["lny"].threeDView().setBackgroundColor2(qt.QColor(193, 195, 232))
    self.cubeFaceThreeDWidgets["rny"].threeDView().setBackgroundColor(qt.QColor(193, 195, 232))
    self.cubeFaceThreeDWidgets["rny"].threeDView().setBackgroundColor2(qt.QColor(193, 195, 232))
    self.cubeFaceThreeDWidgets["lpy"].threeDView().setBackgroundColor(qt.QColor(116, 120, 190))
    self.cubeFaceThreeDWidgets["lpy"].threeDView().setBackgroundColor2(qt.QColor(116, 120, 190))
    self.cubeFaceThreeDWidgets["rpy"].threeDView().setBackgroundColor(qt.QColor(116, 120, 190))
    self.cubeFaceThreeDWidgets["rpy"].threeDView().setBackgroundColor2(qt.QColor(116, 120, 190))
    
    # Position and orient cameras for each ThreeD Widget
    x = 0
    y = 0
    z = 0
    # Left Eye Front - lpx
    lpxCam = self.cubeFaceThreeDWidgets["lpx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(lpxCam, x, y, z)
    
    # Left Eye Right - lnz
    lnzCam = self.cubeFaceThreeDWidgets["lnz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(lnzCam, x, y, z)
    lnzCam.Yaw(270)
    #lnzCam.Roll(180)
    
    # Left Eye Back - lnx
    lnxCam = self.cubeFaceThreeDWidgets["lnx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(lnxCam, x, y, z)
    lnxCam.Yaw(180)
    
    # Left Eye Left - lpz
    lpzCam = self.cubeFaceThreeDWidgets["lpz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(lpzCam, x, y, z)
    lpzCam.Yaw(90)
    #lpzCam.Roll(180)
    
    # Left Eye Top - lpy
    lpyCam = self.cubeFaceThreeDWidgets["lpy"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(lpyCam, x, y, z)
    lpyCam.Pitch(90)
    
    # Left Eye Bottom - lny
    lnyCam = self.cubeFaceThreeDWidgets["lny"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(lnyCam, x, y, z)
    lnyCam.SetViewUp(1,0,0)
    lnyCam.Yaw(270)   
    lnyCam.Roll(90)
    
    # Right Eye Front - rpx
    rpxCam = self.cubeFaceThreeDWidgets["rpx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(rpxCam, x, y, z)
    
    # Right Eye Right - rnz
    rnzCam = self.cubeFaceThreeDWidgets["rnz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(rnzCam, x, y, z)
    rnzCam.Yaw(270)
    #rnzCam.Roll(180)
    
    # Right Eye Back - rnx
    rnxCam = self.cubeFaceThreeDWidgets["rnx"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(rnxCam, x, y, z)
    rnxCam.Yaw(180)
    
    # Right Eye Left - rpz
    rpzCam = self.cubeFaceThreeDWidgets["rpz"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(rpzCam, x, y, z)
    rpzCam.Yaw(90)
    #rpzCam.Roll(180)
    
    # Right Eye Top - rpy
    rpyCam = self.cubeFaceThreeDWidgets["rpy"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(rpyCam, x, y, z)
    rpyCam.Pitch(90)
    
    # Right Eye Bottom - rny
    rnyCam = self.cubeFaceThreeDWidgets["rny"].threeDView().renderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()
    self.initializeCubeFaceCamera(rnyCam, x, y, z)
    rnyCam.SetViewUp(1,0,0)
    rnyCam.Yaw(270)   
    rnyCam.Roll(90)    
    
  def initializeCubeFaceCamera(self, camera, x, y ,z):
    camera.SetPosition(x, y, z);
    camera.SetFocalPoint(x, y + 0.01, z);
    camera.SetViewUp(0, 0, 1);
    camera.UseHorizontalViewAngleOn();
    camera.SetViewAngle(90);
    camera.SetClippingRange(0.3, 500);    
    
  def showWindows(self):
    self.leftWidgets.showNormal()
    self.rightWidgets.showNormal()
    #for face in self.cubeFaceThreeDWidgets:
    #  self.cubeFaceThreeDWidgets[face].showNormal()
      
  def hideWindows(self):
    self.leftWidgets.hide()
    self.rightWidgets.hide()
    #for face in self.cubeFaceThreeDWidgets:
    #  self.cubeFaceThreeDWidgets[face].hide()
      
  # Temporary proof of concept implemention:
  
  def createWindowImages(self):
    widgetPixmapL = qt.QPixmap.grabWidget(self.leftWidgets)
    file = qt.QFile("C:/Work/data/left.jpg")
    file.open(qt.QIODevice.WriteOnly)
    widgetPixmapL.save(file, "JPEG", 100)
    
    widgetPixmapR = qt.QPixmap.grabWidget(self.rightWidgets)
    fileR = qt.QFile("C:/Work/data/right.jpg")
    fileR.open(qt.QIODevice.WriteOnly)
    widgetPixmapR.save(fileR, "JPEG", 100)
    
  def startCreatingImages(self):
    self.timer.start(1000)
    
  def stopCreatingImages(self):
    self.timer.stop()

  
class VirtualRealityViewerLogic:
  def __init__(self):
    pass
 
  


