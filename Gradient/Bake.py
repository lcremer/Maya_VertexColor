import copy
from BakeUtils import *


def get_selection(bake):
    # type: (Bake) -> None
    sel = pmc.ls(sl=True)
    meshes = pmc.listTransforms(type="mesh")
    selected_meshes = [x for x in sel if x in meshes]

    if len(selected_meshes) > 0:
        bake.objects = selected_meshes
    else:
        pmc.PopupError("Nothing selected to bake vertex colors onto")


# TODO:
# Affect only selected verts


class Bake:
    def __init__(self,
                 objects=None,
                 from_origin=False,
                 from_center=False,
                 from_pivot=False,
                 from_point=True,
                 clamp_point=(0, 0, 0),
                 clamp_dir=(0, 1, 0),
                 clamp_decay=True,
                 clamp_smooth=True,
                 mirror=False,
                 easing=None,
                 replace_green=False,
                 replace_red=False,
                 replace_blue=False,
                 replace_alpha=False,
                 clear_green=False,
                 clear_red=False,
                 clear_blue=False,
                 clear_alpha=False,
                 bake_min=0.0,
                 bake_max=1.0,
                 bake_offset=0.0,
                 bake_scale=1.0):

        self.objects = list()
        """@:type : list"""

        self.oldObjects = list()
        """@:type : list"""

        if objects is not None and len(objects) > 0:
            self.objects = objects

        self.bake_data = BakeData(from_origin,
                                  from_center,
                                  from_pivot,
                                  from_point,
                                  clamp_point,
                                  clamp_dir,
                                  clamp_decay,
                                  clamp_smooth,
                                  mirror,
                                  easing,
                                  None,
                                  replace_green,
                                  replace_red,
                                  replace_blue,
                                  replace_alpha,
                                  clear_green,
                                  clear_red,
                                  clear_blue,
                                  clear_alpha,
                                  bake_min,
                                  bake_max,
                                  bake_offset,
                                  bake_scale)

        # self.fromOrigin = from_origin
        # self.fromCenter = from_center
        # self.fromPivot = from_pivot
        # self.fromPoint = from_point
        # self.clampPoint = dt.Point(clamp_point[0], clamp_point[1], clamp_point[2])
        # self.clampDir = dt.Vector(clamp_dir[0], clamp_dir[1], clamp_dir[2])
        # self.clampDecay = clamp_decay
        # self.clampSmooth = clamp_smooth
        # self.mirror = mirror
        #
        # self.easing = easing
        # if self.easing is None:
        #     self.easing = Utils.Easing.Linear
        #
        # # Replace Color Channels
        # self.rG = replace_green
        # self.rR = replace_red
        # self.rB = replace_blue
        # self.rA = replace_alpha
        #
        # # Clear|Zero Out Color Channels
        # self.cG = clear_green
        # self.cR = clear_red
        # self.cB = clear_blue
        # self.cA = clear_alpha
        #
        # self.bakeMin = bake_min
        # self.bakeMax = bake_max
        # self.bakeOffset = bake_offset
        # self.bakeScale = bake_scale

        self.progressMax = 0
        self.progressCurrent = 0
        self.progressBar = None

    def set_start(self,
                  from_point=False,
                  point=dt.Point(0, 0, 0),
                  from_origin=False,
                  from_center=False,
                  from_pivot=False):

        if from_point:
            self.bake_data.clampPoint = point
            self.bake_data.fromPoint = True
            self.bake_data.fromOrigin = False
            self.bake_data.fromCenter = False
            self.bake_data.fromPivot = False

        if from_origin:
            self.bake_data.fromPoint = False
            self.bake_data.fromOrigin = True
            self.bake_data.fromCenter = False
            self.bake_data.fromPivot = False

        if from_center:
            self.bake_data.fromPoint = False
            self.bake_data.fromOrigin = False
            self.bake_data.fromCenter = True
            self.bake_data.fromPivot = False

        if from_pivot:
            self.bake_data.fromPoint = False
            self.bake_data.fromOrigin = False
            self.bake_data.fromCenter = False
            self.bake_data.fromPivot = True

    # Point Helper Methods
    def start_at_point(self, point):
        self.bake_data.clampPoint = dt.Point(point[0], point[1], point[2])
        self.set_start(from_point=True)

    def start_at_origin(self):
        self.set_start(from_origin=True)

    def start_at_center(self):
        self.set_start(from_center=True)

    def start_at_pivot(self):
        self.set_start(from_pivot=True)

    def set_clamp_dir(self, value=dt.Vector(0, 1, 0)):
        self.bake_data.clampDir = value

    def set_clamp_decay(self, value=True):
        self.bake_data.clampDecay = value

    def set_clamp_smooth(self, value=True):
        self.bake_data.clampSmooth = value

    def set_mirror(self, value=True):
        self.bake_data.mirror = value

    def get_point(self):
        return self.bake_data.clampPoint

    def get_vector(self):
        return self.bake_data.clampDir

    def get_mirror(self):
        return self.bake_data.mirror

    # Progress
    def reset_progress_bar(self):
        if self.progressBar is not None:
            self.progressBar.reset()

    def set_progress_max(self):
        self.progressCurrent = 0
        self.progressMax = 0
        print('object Length:', len(self.objects))
        print('progressMax:', self.progressMax)
        for obj in self.objects:
            self.progressMax += len(obj.vtx)

        if self.progressBar is not None:
            self.progressBar.setRange(0, self.progressMax)
            self.progressBar.setValue(0)

    def tick_progress_bar(self):
        self.progressCurrent += 1
        if self.progressBar is not None:
            self.progressBar.setValue(self.progressCurrent)

    # Bake Helpers
    # def create_color_set(self):
    #     try:
    #         pmc.polyColorSet(delete=True, colorSet='bakeColor')
    #     except:
    #         pass
    #         pmc.polyColorSet(create=True, colorSet='bakeColor')
    #         pmc.polyColorPerVertex(rel=True, cdo=True)
    #
    # def set_color_set(self):
    #     pmc.polyColorSet(currentColorSet=True, colorSet='bakeColor')

    # def paint_colors(self, vertex, value):
    #
    #     if value > self.bake_data.bakeMax:
    #         value = self.bake_data.bakeMax
    #     if value < self.bake_data.bakeMin:
    #         value = self.bake_data.bakeMin
    #     value += self.bake_data.bakeOffset
    #     value *= self.bake_data.bakeScale
    #
    #     v_color = vertex.getColor()
    #     """@type : dt.Color"""
    #
    #     # zero out existing value
    #     if self.bake_data.cG:
    #         v_color.g = 0
    #     if self.bake_data.cR:
    #         v_color.r = 0
    #     if self.bake_data.cB:
    #         v_color.b = 0
    #     if self.bake_data.cA:
    #         v_color.a = 0
    #
    #     # replace existing with new value
    #     if self.bake_data.rG:
    #         v_color.g = value
    #     if self.bake_data.rR:
    #         v_color.r = value
    #     if self.bake_data.rB:
    #         v_color.b = value
    #     if self.bake_data.rA:
    #         v_color.a = value
    #
    #     vertex.setColor(v_color)

    # def find_point(self, obj):
    #     if self.bake_data.fromOrigin:
    #         return dt.Point(0.0, 0.0, 0.0)
    #
    #     if self.bake_data.fromPivot:
    #         p = obj.getRotatePivot(space='world')
    #         return dt.Point(p[0], p[1], p[2])
    #
    #     if self.bake_data.fromCenter:
    #         bounds = obj.getBoundingBox(space='world')
    #         """@type: dt.BoundingBox"""
    #         c = bounds.center()
    #         return dt.Point(c[0], c[1], c[2])
    #
    #     if self.bake_data.fromPoint:
    #         return self.bake_data.clampPoint
    #
    #     return dt.Point(0.0, 0.0, 0.0)

    # Bake Methods
    def bake_black(self):
        v_color = dt.Color()
        v_color.r = 0
        v_color.g = 0
        v_color.b = 0
        v_color.a = 1
        get_selection(self)
        self.set_progress_max()
        for obj in self.objects:
            bake_solid(obj, v_color, self.tick_progress_bar)
        self.reset_progress_bar()

    def bake_white(self):
        v_color = dt.Color()
        v_color.r = 1
        v_color.g = 1
        v_color.b = 1
        v_color.a = 1
        get_selection(self)
        self.set_progress_max()
        for obj in self.objects:
            bake_solid(obj, v_color, self.tick_progress_bar)
        self.reset_progress_bar()

    def radial_bounds(self,
                      easing=Utils.Easing.Linear,
                      clamp_easing=Utils.Easing.Linear,
                      debug_locators=False,
                      inner=True):
        self.bake_data.easing = easing
        self.bake_data.clam_easing = clamp_easing
        get_selection(self)
        self.set_progress_max()
        for obj in self.objects:
            bake_radial_bounds(self.bake_data, obj, self.tick_progress_bar, debug_locators, inner)
        self.reset_progress_bar()

    def spherical_bounds(self,
                         easing=Utils.Easing.Linear,
                         clamp_easing=Utils.Easing.Linear,
                         debug_locators=False,
                         inner=False):
        self.bake_data.easing = easing
        self.bake_data.clam_easing = clamp_easing
        get_selection(self)
        self.set_progress_max()
        for obj in self.objects:
            bake_spherical_bounds(self.bake_data, obj, self.tick_progress_bar, debug_locators, inner)
        self.reset_progress_bar()

    def box_bounds(self,
                   easing=Utils.Easing.Linear,
                   clamp_easing=Utils.Easing.Linear,
                   debug_locators=False):
        self.bake_data.easing = easing
        self.bake_data.clam_easing = clamp_easing
        get_selection(self)
        self.set_progress_max()
        for obj in self.objects:
            bake_box_bounds(self.bake_data, obj, self.tick_progress_bar, debug_locators)
        self.reset_progress_bar()

    def branching(self, easing=None):
        # TODO:
        # Voxelize
        # Get branch ends
        # Get shortest paths to origin
        # Weight branches
        # Smooth verts not weights
        pass

    def surface(self, easing=None):
        pass
