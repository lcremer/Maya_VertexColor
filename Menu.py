from functools import partial

import Maya_UtilLib
from Maya_UtilLib.Labels import ui_name
from Maya_VertexColor import Gradient
from pymel import core as pm


def menu_item():
    pm.menuItem(parent=ui_name, subMenu=True, tearOff=True, label='Misc')
    pm.menuItem(label='Vertex Color', command=partial(Gradient.UI.open))


def add_menu_item():
    Maya_UtilLib.Menu.add_module_menu(module='Maya_VertexColor', menu_func=menu_item)
    Maya_UtilLib.Menu.draw()
