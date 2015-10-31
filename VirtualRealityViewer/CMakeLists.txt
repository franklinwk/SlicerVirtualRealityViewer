cmake_minimum_required(VERSION 2.8.9)

project(VirtualRealityViewer)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "")
set(EXTENSION_CATEGORY "Virtual Reality")
set(EXTENSION_CONTRIBUTORS "Franklin King (Brigham and Women's Hospital")
set(EXTENSION_DESCRIPTION "Generate a cube map to be viewed by a VR player")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CubemapGenerator)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
