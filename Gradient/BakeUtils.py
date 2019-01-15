import pymel.core as pmc
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt
import Maya_UtilLib as Utils
import copy

pi = 3.14159


class BakeData:
    def __init__(self,
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
                 clamp_easing=None,
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
        self.fromOrigin = from_origin
        self.fromCenter = from_center
        self.fromPivot = from_pivot
        self.fromPoint = from_point
        self.clampPoint = dt.Point(clamp_point[0], clamp_point[1], clamp_point[2])
        self.clampDir = dt.Vector(clamp_dir[0], clamp_dir[1], clamp_dir[2])
        self.clampDecay = clamp_decay
        self.clampSmooth = clamp_smooth
        self.mirror = mirror

        self.easing = easing
        if self.easing is None:
            self.easing = Utils.Easing.Linear

        self.clamp_easing = clamp_easing
        if self.clamp_easing is None:
            self.clamp_easing = Utils.Easing.Linear

        # Replace Color Channels
        self.rG = replace_green
        self.rR = replace_red
        self.rB = replace_blue
        self.rA = replace_alpha

        # Clear|Zero Out Color Channels
        self.cG = clear_green
        self.cR = clear_red
        self.cB = clear_blue
        self.cA = clear_alpha

        self.bakeMin = bake_min
        self.bakeMax = bake_max
        self.bakeOffset = bake_offset
        self.bakeScale = bake_scale


# TODO: need to setup UI to allow naming the color set
def create_color_set(mesh):
    try:
        pmc.polyColorSet(mesh, delete=True, colorSet='bakeColor')
    except:
        pass
    pmc.polyColorSet(mesh, create=True, colorSet='bakeColor')
    pmc.polyColorPerVertex(mesh, rel=True, cdo=True)


def find_point(bake_data, mesh):
    # type: (BakeData, nt.Mesh)->dt.Point

    if bake_data.fromOrigin:
        return dt.Point(0.0, 0.0, 0.0)

    if bake_data.fromPivot:
        p = mesh.getRotatePivot(space='world')
        return dt.Point(p[0], p[1], p[2])

    if bake_data.fromCenter:
        bounds = mesh.getBoundingBox(space='world')
        """:type: dt.BoundingBox"""
        c = bounds.center()
        return dt.Point(c[0], c[1], c[2])

    if bake_data.fromPoint:
        return bake_data.clampPoint

    return dt.Point(0.0, 0.0, 0.0)


# TODO: use appropriate command to color mesh, no need to iterate over mesh
def bake_solid(mesh, color, update_notify):
    # type: (nt.Mesh, dt.Color, function) -> None
    for i in range(len(mesh.vtx)):
        mesh.vtx[i].setColor(color)
        # calling to update progress bar
        update_notify()
    pmc.polyColorPerVertex(mesh, rel=True, cdo=True)


def paint_colors(bake_data, mesh, index, value):
    # type: (BakeData, nt.Mesh, int, float)->None

    color = mesh.vtx[index].getColor()

    value += bake_data.bakeOffset
    value *= bake_data.bakeScale
    if value > bake_data.bakeMax:
        value = bake_data.bakeMax
    if value < bake_data.bakeMin:
        value = bake_data.bakeMin

    # TODO: test if its necessary to do this, see if deepCopy works too

    # zero out existing value
    if bake_data.cG:
        color.g = 0
    if bake_data.cR:
        color.r = 0
    if bake_data.cB:
        color.b = 0
    if bake_data.cA:
        color.a = 0

    # replace existing with new value
    if bake_data.rG:
        color.g = copy.deepcopy(value)
    if bake_data.rR:
        color.r = copy.deepcopy(value)
    if bake_data.rB:
        color.b = copy.deepcopy(value)
    if bake_data.rA:
        color.a = copy.deepcopy(value)

    mesh.vtx[index].setColor(color)


"""
What should be happening in these bakes is that we have a distance from point gradient
Where the value of that is modified by a distance from plane (ground) normal, where intersecting it nulls paint value
Then we can have a mirror distance gradient.
"""


def bake_radial_bounds(bake_data,
                       mesh,
                       update_notify,
                       debug_locators=False,
                       inner=True):
    # type: (BakeData, nt.Mesh, function, bool, bool) -> None

    points = mesh.getPoints(space='world')
    point = find_point(bake_data, mesh)
    bounds = mesh.getBoundingBox(space='world')
    """@:type: dt.BoundingBox"""

    create_color_set(mesh)
    for i in range(len(mesh.vtx)):
        vertex_dir = points[i] - point
        """@:type: dt.Vector"""

        angle = bake_data.clampDir.angle(vertex_dir)

        if angle < pi / 2.0:
            # the smaller the angle the fuller the contribution
            angle_ratio = 1.0 - (angle / (pi / 2.0))
        else:
            if bake_data.mirror:
                angle = bake_data.clampDir.angle(-vertex_dir)
                angle_ratio = 1.0 - (angle / (pi / 2.0))
            else:
                angle_ratio = 0

        intersect_point = Utils.VMath.project_point_onto_scaled_sphere(bounds, points[i], inner)

        if debug_locators:
            pmc.spaceLocator(name='intersection', p=intersect_point)
            pmc.select(clear=True)

        # the assumption here is that the length of vertex_dir is some portion of the vector of the intersect and point
        value = (vertex_dir.length() / (intersect_point - point).length())

        if bake_data.clampDecay:
            value = (value + angle_ratio) / 2.0

        value = bake_data.easing(value)

        if bake_data.clampSmooth:
            value *= bake_data.clamp_easing(angle_ratio)

        paint_colors(bake_data, mesh, i, value)
        update_notify()
    mesh.updateSurface()


def bake_spherical_bounds(bake_data,
                          mesh,
                          update_notify,
                          debug_locators=False,
                          inner=False):
    # type: (BakeData, nt.Mesh, function, bool, bool) -> None

    points = mesh.getPoints(space='world')
    point = find_point(bake_data, mesh)
    bounds = mesh.getBoundingBox(space='world')
    """@:type: dt.BoundingBox"""

    for i in range(len(mesh.vtx)):
        vertex_dir = points[i] - point
        """@:type: dt.Vector"""

        angle = bake_data.clampDir.angle(vertex_dir)

        if angle < pi / 2.0:
            angle_ratio = 1.0 - (angle / (pi / 2.0))
        else:
            angle_ratio = angle / pi

        # check clamp against point and vector plane
        if not bake_data.mirror and angle > pi / 2.0:
            value = 0.0
        else:
            intersect_point = Utils.VMath.project_point_onto_sphere(bounds, points[i], inner)
            if debug_locators:
                pmc.spaceLocator(name='intersection', p=intersect_point)
                pmc.select(clear=True)

            value = (vertex_dir.length() / (intersect_point - point).length())

            if bake_data.clampDecay:
                value = (value + angle_ratio) / 2.0

        value = bake_data.easing(value)

        if bake_data.clampSmooth:
            value *= bake_data.clamp_easing(angle_ratio)

        paint_colors(bake_data, mesh, i, value)
        update_notify()
    mesh.updateSurface()


def bake_box_bounds(bake_data,
                    mesh,
                    update_notify,
                    debug_locators=False):
    # type: (BakeData, nt.Mesh, function, bool) -> None

    points = mesh.getPoints(space='world')
    point = find_point(bake_data, mesh)
    bounds = mesh.getBoundingBox(space='world')
    """@:type: dt.BoundingBox"""

    double_length = (bounds.width() + bounds.height() + bounds.depth()) / 3.0 * 3.0

    for i in range(len(mesh.vtx)):
        vertex_dir = points[i] - point
        """@:type: dt.Vector"""

        angle = bake_data.clampDir.angle(vertex_dir)

        if angle < pi / 2.0:
            angle_ratio = 1.0 - (angle / (pi / 2.0))
        else:
            angle_ratio = angle / pi

        # check clamp against point and vector plane
        if not bake_data.mirror and angle > pi / 2.0:
            value = 0.0
        else:
            ray_point = (vertex_dir.normal() * double_length) + point
            ray_direction = point - ray_point
            intersect_point = Utils.VMath.bounding_box_intersection(bounds, ray_point, ray_direction)

            if debug_locators:
                pmc.spaceLocator(p=ray_point)
                pmc.spaceLocator(name='intersection', p=intersect_point)
                pmc.select(clear=True)

            value = (vertex_dir.length() / (intersect_point - point).length())

            if bake_data.clampDecay:
                value = (value + angle_ratio) / 2.0

        value = bake_data.easing(value)

        if bake_data.clampSmooth:
            value *= bake_data.clamp_easing(angle_ratio)

        paint_colors(bake_data, mesh, i, value)
        update_notify()
    mesh.updateSurface()


def bake_branching(bake_data, easing):
    # type: (BakeData, Utils.Easing) -> None
    pass
