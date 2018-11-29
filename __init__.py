import Maya_VertexColor.Gradient
import Maya_UtilLib
import pymel.core as pm
from functools import partial


def MenuItem():
    pm.menuItem(parent='CustomTools', subMenu=True, tearOff=True, label='Misc')
    pm.menuItem(label='Vertex Color', command=partial(Gradient.UI.Open))


def AddMenuItem():
    Maya_UtilLib.Menu.AddModuleMenu(module='Maya_VertexColor', menuFunc=MenuItem)
    Maya_UtilLib.Menu.Draw()

AddMenuItem()
