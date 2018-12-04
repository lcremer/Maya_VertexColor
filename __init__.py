import Maya_VertexColor.Gradient
import Maya_UtilLib
import pymel.core as pm
from functools import partial


def MenuItem():
    pm.menuItem(parent=Maya_UtilLib.ui_name, subMenu=True, tearOff=True, label='Misc')
    pm.menuItem(label='Vertex Color', command=partial(Gradient.UI.open))


def AddMenuItem():
    Maya_UtilLib.Menu.add_module_menu(module='Maya_VertexColor', menu_func=MenuItem)
    Maya_UtilLib.Menu.draw()


AddMenuItem()
