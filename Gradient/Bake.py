from PySide2 import QtGui, QtCore
from pymel.core import *
import Maya_UtilLib as Utils
import math

# TODO:
# Affect only selected verts


class Bake:
    def __init__(self,
                 objects=None,
                 fromOrigin=False,
                 fromCenter=False,
                 fromPivot=False,
                 fromPoint=True,
                 clampPoint=(0, 0, 0),
                 clampDir=(0, 1, 0),
                 clampDecay=True,
                 clampSmooth=True,
                 mirror=False,
                 easing=None,
                 replaceGreen=False,
                 replaceRed=False,
                 replaceBlue=False,
                 replaceAlpha=False,
                 clearGreen=False,
                 clearRed=False,
                 clearBlue=False,
                 clearAlpha=False,
                 bakeMin=0.0,
                 bakeMax=1.0,
                 bakeOffset=0.0,
                 bakeScale=1.0):

        self.objects = objects
        self.fromOrigin = fromOrigin
        self.fromCenter = fromCenter
        self.fromPivot = fromPivot
        self.fromPoint = fromPoint
        self.clampPoint = dt.Point(clampPoint[0], clampPoint[1], clampPoint[2])
        self.clampDir = dt.Vector(clampDir[0], clampDir[1], clampDir[2])
        self.clampDecay = clampDecay
        self.clampSmooth = clampSmooth
        self.mirror = mirror

        self.easing = easing
        if self.easing is None:
            self.easing = Utils.Easing.Linear

        # Replace Color Channels
        self.rG = replaceGreen
        self.rR = replaceRed
        self.rB = replaceBlue
        self.rA = replaceAlpha

        # Clear|Zero Out Color Channels
        self.cG = clearGreen
        self.cR = clearRed
        self.cB = clearBlue
        self.cA = clearAlpha

        self.bakeMin = bakeMin
        self.bakeMax = bakeMax
        self.bakeOffset = bakeOffset
        self.bakeScale = bakeScale

        self.progressMax = 0
        self.progressCurrent = 0
        self.progressBar = None

    def SetStart(self,
                 fromPoint=False,
                 point=dt.Point(0, 0, 0),
                 fromOrigin=False,
                 fromCenter=False,
                 fromPivot=False):

        if fromPoint:
            self.clampPoint = point
            self.fromPoint = True
            self.fromOrigin = False
            self.fromCenter = False
            self.fromPivot = False

        if fromOrigin:
            self.fromPoint = False
            self.fromOrigin = True
            self.fromCenter = False
            self.fromPivot = False

        if fromCenter:
            self.fromPoint = False
            self.fromOrigin = False
            self.fromCenter = True
            self.fromPivot = False

        if fromPivot:
            self.fromPoint = False
            self.fromOrigin = False
            self.fromCenter = False
            self.fromPivot = True

    # Point Helper Methods
    def StartAtPoint(self, point):
        self.clampPoint = dt.Point(point[0], point[1], point[2])
        self.SetStart(fromPoint=True)

    def StartAtOrigin(self):
        self.SetStart(fromOrigin=True)

    def StartAtCenter(self):
        self.SetStart(fromCenter=True)

    def StartAtPivot(self):
        self.SetStart(fromPivot=True)

    def SetClampDir(self, value=dt.Vector(0, 1, 0)):
        self.clampDir = value

    def SetClampDecay(self, value=True):
        self.clampDecay = value

    def SetClampSmooth(self, value=True):
        self.clampSmooth = value

    def SetMirror(self, value=True):
        self.mirror = value

    def GetPoint(self):
        return self.clampPoint

    def GetVector(self):
        return self.clampDir

    def GetMirror(self):
        return self.mirror

    # Progress
    def ResetProgressBar(self):
        if self.progressBar is not None:
            self.progressBar.reset()

    def SetProgressMax(self):
        self.progressCurrent = 0
        self.progressMax = 0
        print('object Length:', len(self.objects))
        print('progressMax:', self.progressMax)
        for obj in self.objects:
            self.progressMax += len(obj.vtx)

        if self.progressBar is not None:
            self.progressBar.setRange(0, self.progressMax)
            self.progressBar.setValue(0)

    def TickProgressBar(self):
        self.progressCurrent += 1
        if self.progressBar is not None:
            self.progressBar.setValue(self.progressCurrent)

    # Bake Helpers
    def CreateColorSet(self):
        try:
            polyColorSet(delete=True, colorSet='bakeColor')
        except:
            pass
        polyColorSet(create=True, colorSet='bakeColor')
        polyColorPerVertex(rel=True, cdo=True)

    def SetColorSet(self):
        polyColorSet(currentColorSet=True, colorSet='bakeColor')

    def PaintColors(self, vertex, value):

        if value > self.bakeMax:
            value = self.bakeMax
        if value < self.bakeMin:
            value = self.bakeMin
        value += self.bakeOffset
        value *= self.bakeScale

        vColor = vertex.getColor()
        """@type : dt.Color"""

        # zero out existing value
        if self.cG:
            vColor.g = 0
        if self.cR:
            vColor.r = 0
        if self.cB:
            vColor.b = 0
        if self.cA:
            vColor.a = 0

        # replace existing with new value
        if self.rG:
            vColor.g = value
        if self.rR:
            vColor.r = value
        if self.rB:
            vColor.b = value
        if self.rA:
            vColor.a = value

        vertex.setColor(vColor)

    def FindPoint(self, obj):
        if self.fromOrigin:
            return dt.Point(0.0,0.0,0.0)

        if self.fromPivot:
            p = obj.getRotatePivot(space='world')
            return dt.Point(p[0],p[1],p[2])

        if self.fromCenter:
            bounds = obj.getBoundingBox(space='world')
            """@type: dt.BoundingBox"""
            c = bounds.center()
            return dt.Point(c[0],c[1],c[2])

        if self.fromPoint:
            return self.clampPoint

        return dt.Point(0.0,0.0,0.0)

    # Bake Methods
    def bakeBlack(self):
        if self.objects == "" or self.objects is None:
            self.objects = ls(selection=True)
        self.SetProgressMax()
        for obj in self.objects:
            for i in range(len(obj.vtx)):
                self.TickProgressBar()

                vColor = obj.vtx[i].getColor()
                """@type : dt.Color"""

                vColor.g = 0
                vColor.r = 0
                vColor.b = 0
                vColor.a = 1

                obj.vtx[i].setColor(vColor)
            self.CreateColorSet(obj)
        self.ResetProgressBar()

    def bakeWhite(self):
        if self.objects == "" or self.objects is None:
            self.objects = ls(selection=True)
        self.SetProgressMax()
        for obj in self.objects:
            for i in range(len(obj.vtx)):
                self.TickProgressBar()

                vColor = obj.vtx[i].getColor()
                """@type : dt.Color"""

                vColor.g = 1
                vColor.r = 1
                vColor.b = 1
                vColor.a = 1

                obj.vtx[i].setColor(vColor)
            self.CreateColorSet(obj)
        self.TickProgressBar()

    def RadialBounds(self,
                     easing=Utils.Easing.Linear,
                     clampEasing=Utils.Easing.Linear,
                     debugLocators=False,
                     inner=True):
        if self.objects == "" or self.objects is None:
            self.objects = ls(selection=True)

        self.CreateColorSet()
        self.SetProgressMax()
        for obj in self.objects:
            points = obj.getPoints(space='world')
            point = self.FindPoint(obj)
            bounds = obj.getBoundingBox(space='world')
            """@type: dt.BoundingBox"""

            for i in range(len(obj.vtx)):
                self.TickProgressBar()
                vertexDir = points[i] - point
                """@type: dt.Vector"""

                angle = self.clampDir.angle(vertexDir)

                if angle < math.pi / 2.0:
                    angleRatio = 1.0 - (angle / (math.pi / 2.0))
                else:
                    angleRatio = angle / math.pi

                # check clamp against point and vector plane
                if not self.mirror and angle > math.pi / 2.0:
                    value = 0
                else:
                    intersectPoint = Utils.VMath.ProjectPointOntoScaledSphere(bounds, points[i], inner)
                    if debugLocators:
                        spaceLocator(name='intersection', p=intersectPoint)
                        select(clear=True)

                    value = (vertexDir.length() / (intersectPoint - point).length())

                    if self.clampDecay:
                        value = (value + angleRatio) / 2.0

                value = easing(value)

                if self.clampSmooth:
                    value *= clampEasing(angleRatio)

                vertex = obj.vtx[i]
                self.PaintColors(vertex, value)
        self.ResetProgressBar()
        self.SetColorSet()

    def SphericalBounds(self,
                        easing=Utils.Easing.Linear,
                        clampEasing=Utils.Easing.Linear,
                        debugLocators=False,
                        inner=False):
        if self.objects == "" or self.objects is None:
            self.objects = ls(selection=True)

        self.CreateColorSet()
        self.SetProgressMax()
        for obj in self.objects:
            points = obj.getPoints(space='world')
            point = self.FindPoint(obj)
            bounds = obj.getBoundingBox(space='world')
            """@type: dt.BoundingBox"""

            for i in range(len(obj.vtx)):
                self.TickProgressBar()
                vertexDir = points[i] - point
                """@type: dt.Vector"""

                angle = self.clampDir.angle(vertexDir)

                if angle < math.pi / 2.0:
                    angleRatio = 1.0 - (angle / (math.pi / 2.0))
                else:
                    angleRatio = angle / math.pi

                # check clamp against point and vector plane
                if not self.mirror and angle > math.pi / 2.0:
                    value = 0.0
                else:
                    intersectPoint = Utils.VMath.ProjectPointOntoSphere(bounds, points[i], inner)
                    if debugLocators:
                        spaceLocator(name='intersection', p=intersectPoint)
                        select(clear=True)

                    value = (vertexDir.length() / (intersectPoint - point).length())

                    if self.clampDecay:
                        value = (value + angleRatio) / 2.0

                value = easing(value)

                if self.clampSmooth:
                    value *= clampEasing(angleRatio)

                vertex = obj.vtx[i]
                self.PaintColors(vertex, value)
            self.CreateColorSet(obj)
        self.ResetProgressBar()
        self.SetColorSet()

    def BoxBounds(self,
                  easing=Utils.Easing.Linear,
                  clampEasing=Utils.Easing.Linear,
                  debugLocators=False):
        if self.objects == "" or self.objects is None:
            self.objects = ls(selection=True)

        self.CreateColorSet()
        self.SetProgressMax()
        for obj in self.objects:
            points = obj.getPoints(space='world')
            point = self.FindPoint(obj)
            bounds = obj.getBoundingBox(space='world')
            """@type: dt.BoundingBox"""

            doubleLength = (bounds.width() + bounds.height() + bounds.depth()) / 3.0 * 3.0

            for i in range(len(obj.vtx)):
                self.TickProgressBar()
                vertexDir = points[i] - point
                """@type: dt.Vector"""

                angle = self.clampDir.angle(vertexDir)

                if angle < math.pi / 2.0:
                    angleRatio = 1.0 - (angle / (math.pi / 2.0))
                else:
                    angleRatio = angle / math.pi

                # check clamp against point and vector plane
                if not self.mirror and angle > math.pi / 2.0:
                    value = 0.0
                else:
                    rayPoint = (vertexDir.normal() * doubleLength) + point
                    rayDirection = point - rayPoint
                    intersectPoint = Utils.VMath.BoundingBoxIntersection(bounds, rayPoint, rayDirection)

                    if debugLocators:
                        spaceLocator(p=rayPoint)
                        spaceLocator(name='intersection', p=intersectPoint)
                        select(clear=True)

                    value = (vertexDir.length() / (intersectPoint - point).length())

                    if self.clampDecay:
                        value = (value + angleRatio) / 2.0

                value = easing(value)

                if self.clampSmooth:
                    value *= clampEasing(angleRatio)

                vertex = obj.vtx[i]
                self.PaintColors(vertex, value)
            self.CreateColorSet(obj)
        self.ResetProgressBar()
        self.SetColorSet()

    def Branching(self, easing=None):
        # TODO:
        # Voxelize
        # Get branch ends
        # Get shortest paths to origin
        # Weight branches
        # Smooth verts not weights
        pass

    def Surface(self, easing=None):
        pass
