from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import OpenMayaUI as omui
from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance

from Maya_VertexColor.Gradient import Bake
from Maya_UtilLib import Easing
import pymel.core as pc
import Maya_UtilLib
import weakref

gradientMixinWindow = None


def open(*args):
    gradient_dockable_widget_ui()


def gradient_dockable_widget_ui(restore=False):
    # type: (bool) -> BakeTool
    global gradientMixinWindow

    restored_control = None
    if restore:
        restored_control = omui.MQtUtil.getCurrentParent()

    if gradientMixinWindow is None:
        gradientMixinWindow = BakeTool()
        gradientMixinWindow.setObjectName('vertexColorMixinWindow')

    if restore:
        mixin_ptr = omui.MQtUtil.findControl(gradientMixinWindow.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(long(mixin_ptr), long(restored_control))
    else:
        gradientMixinWindow.show(dockable=True, height=600, width=480,
                                 uiScript='GradientDockableWidgetUI(restore=True)')

    return gradientMixinWindow


class BakeTool(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    toolName = 'vertexColorWidget'
    """
    VertexColor UI Class
    """

    instances = list()
    CONTROL_NAME = 'bake_tool_workspace_control'
    DOCK_LABEL_NAME = 'bake tool workspace control'

    def __init__(self, parent=None):
        # creating main Bake object
        self.Bake = Bake.Bake()
        self.selected = []
        self.originLocators = []
        self.dirLocators = []
        self.bakeRadioType = 'pivot'
        self.Easing = Easing.Linear
        self.ClampEasing = Easing.Linear

        # self.delete_instance()

        super(BakeTool, self).__init__(parent=parent)

        BakeTool.delete_instance()
        self.__class__.instances.append(weakref.proxy(self))

        self.setObjectName(self.__class__.toolName)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('VertexColor Bake')
        self.setMinimumWidth(500)
        # self.setMaximumWidth(375)
        # self.setMaximumHeight(300)

        # main vertical layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)

        self.inner_layout = QtWidgets.QVBoxLayout(self)
        self.inner_layout.setAlignment(QtCore.Qt.AlignTop)

        self.font = QtGui.QFont()
        self.font.setPixelSize(12)
        self.font.setBold(True)

        # pre-declaring combo box variables
        self.bake_type_combobox = None
        self.bake_easing_combobox = None
        self.bake_clamp_easing_combobox = None

        self.bake_type()
        self.bakeValues()
        self.bakePoint()
        self.bakeGiven()
        self.bakeDirection()
        self.bakeClamp()
        self.bakeClearChannels()
        self.bakeColorChannels()
        self.bakeSolidButtons()
        self.bakeButton()
        self.progressBar()

        self.main_layout.addLayout(self.inner_layout)
        self.main_layout.setAlignment(self.inner_layout, QtCore.Qt.AlignTop)

        self.setLayout(self.main_layout)
        self.show(dockable=True)

    @staticmethod
    def delete_instance():
        for ins in BakeTool.instances:
            try:
                ins.setParent(None)
                ins.deleteLater()
            except:
                pass

            BakeTool.instances.remove(ins)
            del ins

    # def delete_instance(self):
    #     maya_main_window = Maya_UtilLib.main_window()
    #
    #     # Go through main window's children to find any previous instances
    #     for obj in maya_main_window.children():
    #         if type(obj) == QtWidgets.QDockWidget: #MayaQDockWidget:
    #             # if obj.widget().__class__ == self.__class__:
    #             #  Alternatively we can check with this, but it will fail if we re-evaluate the class
    #             if obj.widget().objectName() == self.__class__.toolName:  # Compare object names
    #                 # If they share the same name then remove it
    #                 print 'Deleting instance {0}'.format(obj)
    #                 # This will remove from right-click menu, but won't actually delete it!
    #                 # ( still under main_window.children() )
    #                 maya_main_window.removeDockWidget(obj)
    #                 # Delete it for good
    #                 obj.setParent(None)
    #                 obj.deleteLater()

    def bake_type(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        type_label = QtWidgets.QLabel('Type')
        h_layout.addWidget(type_label)
        # add spacer
        spacer = QtWidgets.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        self.bake_type_combobox = QtWidgets.QComboBox()
        self.bake_type_combobox.addItems(
            ['Radial In Bounds', 'Radial Out Bounds', 'Spherical In Bounds', 'Spherical Out Bounds', 'Box Bounds',
             'Branching (Coming Soon)'])

        h_layout.addWidget(self.bake_type_combobox)

        # Name Label
        easing_label = QtWidgets.QLabel('Easing')
        h_layout.addWidget(easing_label)
        # add spacer
        spacer = QtWidgets.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        self.bake_easing_combobox = QtWidgets.QComboBox()
        self.bake_easing_combobox.addItems(Easing.EasingList())
        h_layout.addWidget(self.bake_easing_combobox)

        self.inner_layout.addLayout(h_layout)

    def bakeValues(self):
        h_layout = QtWidgets.QHBoxLayout()

        min_label = QtWidgets.QLabel('Min')
        min_input = QtWidgets.QDoubleSpinBox()
        min_input.setValue(self.Bake.bake_data.bakeMin)
        min_input.setSingleStep(0.001)
        min_input.setDecimals(3)

        def updateMin():
            self.Bake.bake_data.bakeMin = float(min_input.text())

        min_input.valueChanged.connect(updateMin)

        max_label = QtWidgets.QLabel('Max')
        max_input = QtWidgets.QDoubleSpinBox()
        max_input.setValue(self.Bake.bake_data.bakeMax)
        max_input.setSingleStep(0.001)
        max_input.setDecimals(3)

        def updateMax():
            self.Bake.bake_data.bakeMax = float(max_input.text())

        max_input.valueChanged.connect(updateMax)

        offset_label = QtWidgets.QLabel('Offset')
        offset_input = QtWidgets.QDoubleSpinBox()
        offset_input.setValue(self.Bake.bake_data.bakeOffset)
        offset_input.setSingleStep(0.001)
        offset_input.setDecimals(3)

        def updateOffset():
            self.Bake.bake_data.bakeOffset = float(offset_input.text())

        offset_input.valueChanged.connect(updateOffset)

        scale_label = QtWidgets.QLabel('Scale')
        scale_input = QtWidgets.QDoubleSpinBox()
        scale_input.setValue(self.Bake.bake_data.bakeScale)
        scale_input.setSingleStep(0.001)
        scale_input.setDecimals(3)

        def updateScale():
            self.Bake.bake_data.bakeScale = float(scale_input.text())

        scale_input.valueChanged.connect(updateScale)

        h_layout.addWidget(min_label)
        h_layout.addWidget(min_input)
        h_layout.addWidget(max_label)
        h_layout.addWidget(max_input)
        h_layout.addWidget(offset_label)
        h_layout.addWidget(offset_input)
        h_layout.addWidget(scale_label)
        h_layout.addWidget(scale_input)

        self.inner_layout.addLayout(h_layout)

    def bakePoint(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        labelName = QtWidgets.QLabel('From')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        # Bake Origin: Origin, Center, Pivot, Point (Create Locator with Label that represents point)
        origin_radio_button = QtWidgets.QRadioButton('Origin')
        center_radio_button = QtWidgets.QRadioButton('Center')
        pivot_radio_button = QtWidgets.QRadioButton('Pivot')
        given_radio_button = QtWidgets.QRadioButton('Given')

        pivot_radio_button.setChecked(True)
        self.Bake.start_at_pivot()

        def originChanged():
            if origin_radio_button.isChecked():
                self.bakeRadioType = 'origin'
                self.Bake.start_at_origin()

        def centerChanged():
            if center_radio_button.isChecked():
                self.bakeRadioType = 'center'
                self.Bake.start_at_center()

        def pivotChanged():
            if pivot_radio_button.isChecked():
                self.bakeRadioType = 'pivot'
                self.Bake.start_at_pivot()

        def givenChanged():
            if given_radio_button.isChecked():
                self.bakeRadioType = 'given'
                self.Bake.start_at_point(self.Bake.bake_data.clampPoint)

        origin_radio_button.toggled.connect(originChanged)
        center_radio_button.toggled.connect(centerChanged)
        pivot_radio_button.toggled.connect(pivotChanged)
        given_radio_button.toggled.connect(givenChanged)

        h_layout.addWidget(origin_radio_button)
        h_layout.addWidget(center_radio_button)
        h_layout.addWidget(pivot_radio_button)
        h_layout.addWidget(given_radio_button)

        self.inner_layout.addLayout(h_layout)

    def bakeGiven(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        labelName = QtWidgets.QLabel('Given')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(53, 10)
        h_layout.addSpacerItem(spacer)

        x_label = QtWidgets.QLabel('X')
        x_input = QtWidgets.QLineEdit()
        x_input.setInputMask('0.000')
        x_input.setMaxLength(5)
        x_input.setText(str(self.Bake.bake_data.clampPoint[0]))

        def updateX():
            self.Bake.bake_data.clampPoint[0] = float(x_input.text())

        x_input.textChanged.connect(updateX)

        y_label = QtWidgets.QLabel('Y')
        y_input = QtWidgets.QLineEdit()
        y_input.setInputMask('0.000')
        y_input.setMaxLength(5)
        y_input.setText(str(self.Bake.bake_data.clampPoint[1]))

        def updateY():
            self.Bake.bake_data.clampPoint[1] = float(y_input.text())

        y_input.textChanged.connect(updateY)

        z_label = QtWidgets.QLabel('Z')
        z_input = QtWidgets.QLineEdit()
        z_input.setInputMask('0.000')
        z_input.setMaxLength(5)
        z_input.setText(str(self.Bake.bake_data.clampPoint[2]))

        def updateZ():
            self.Bake.bake_data.clampPoint[2] = float(z_input.text())

        z_input.textChanged.connect(updateZ)

        h_layout.addWidget(x_label)
        h_layout.addWidget(x_input)
        h_layout.addWidget(y_label)
        h_layout.addWidget(y_input)
        h_layout.addWidget(z_label)
        h_layout.addWidget(z_input)

        self.inner_layout.addLayout(h_layout)

    def bakeDirection(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        labelName = QtWidgets.QLabel('Direction')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(35, 10)
        h_layout.addSpacerItem(spacer)

        x_label = QtWidgets.QLabel('X')
        x_input = QtWidgets.QLineEdit()
        x_input.setInputMask('0.000')
        x_input.setMaxLength(5)
        x_input.setText(str(self.Bake.bake_data.clampDir[0]))

        def updateX():
            self.Bake.bake_data.clampDir[0] = float(x_input.text())

        x_input.textChanged.connect(updateX)

        y_label = QtWidgets.QLabel('Y')
        y_input = QtWidgets.QLineEdit()
        y_input.setInputMask('0.000')
        y_input.setMaxLength(5)
        y_input.setText(str(self.Bake.bake_data.clampDir[1]))

        def updateY():
            self.Bake.bake_data.clampDir[1] = float(y_input.text())

        y_input.textChanged.connect(updateY)

        z_label = QtWidgets.QLabel('Z')
        z_input = QtWidgets.QLineEdit()
        z_input.setInputMask('0.000')
        z_input.setMaxLength(5)
        z_input.setText(str(self.Bake.bake_data.clampDir[2]))

        def updateZ():
            self.Bake.bake_data.clampDir[2] = float(z_input.text())

        z_input.textChanged.connect(updateZ)

        h_layout.addWidget(x_label)
        h_layout.addWidget(x_input)
        h_layout.addWidget(y_label)
        h_layout.addWidget(y_input)
        h_layout.addWidget(z_label)
        h_layout.addWidget(z_input)

        self.inner_layout.addLayout(h_layout)

    def bakeClearChannels(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        labelName = QtWidgets.QLabel('Clear Channels')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        # Bake Channels: Green, Red, Blue, Alpha
        green_checkbox = QtWidgets.QCheckBox('Green')
        red_checkbox = QtWidgets.QCheckBox('Red')
        blue_checkbox = QtWidgets.QCheckBox('Blue')
        alpha_checkbox = QtWidgets.QCheckBox('Alpha')

        def updateG():
            self.Bake.bake_data.cG = green_checkbox.isChecked()

        green_checkbox.stateChanged.connect(updateG)

        def updateR():
            self.Bake.bake_data.cR = red_checkbox.isChecked()

        red_checkbox.stateChanged.connect(updateR)

        def updateB():
            self.Bake.bake_data.cB = blue_checkbox.isChecked()

        blue_checkbox.stateChanged.connect(updateB)

        def updateA():
            self.Bake.bake_data.cA = alpha_checkbox.isChecked()

        alpha_checkbox.stateChanged.connect(updateA)

        # TODO: store preferences for clear and bake colors
        green_checkbox.setChecked(False)
        red_checkbox.setChecked(False)
        blue_checkbox.setChecked(True)
        alpha_checkbox.setChecked(False)

        h_layout.addWidget(green_checkbox)
        h_layout.addWidget(red_checkbox)
        h_layout.addWidget(blue_checkbox)
        h_layout.addWidget(alpha_checkbox)
        self.inner_layout.addLayout(h_layout)

    def bakeColorChannels(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        labelName = QtWidgets.QLabel('Paint Channels')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        # Bake Channels: Green, Red, Blue, Alpha
        green_checkbox = QtWidgets.QCheckBox('Green')
        red_checkbox = QtWidgets.QCheckBox('Red')
        blue_checkbox = QtWidgets.QCheckBox('Blue')
        alpha_checkbox = QtWidgets.QCheckBox('Alpha')

        def updateG():
            self.Bake.bake_data.rG = green_checkbox.isChecked()

        green_checkbox.stateChanged.connect(updateG)

        def updateR():
            self.Bake.bake_data.rR = red_checkbox.isChecked()

        red_checkbox.stateChanged.connect(updateR)

        def updateB():
            self.Bake.bake_data.rB = blue_checkbox.isChecked()

        blue_checkbox.stateChanged.connect(updateB)

        def updateA():
            self.Bake.bake_data.rA = alpha_checkbox.isChecked()

        alpha_checkbox.stateChanged.connect(updateA)

        green_checkbox.setChecked(False)
        red_checkbox.setChecked(False)
        blue_checkbox.setChecked(True)
        alpha_checkbox.setChecked(False)

        h_layout.addWidget(green_checkbox)
        h_layout.addWidget(red_checkbox)
        h_layout.addWidget(blue_checkbox)
        h_layout.addWidget(alpha_checkbox)
        self.inner_layout.addLayout(h_layout)

    def bakeClamp(self):
        h_layout = QtWidgets.QHBoxLayout()

        # Name Label
        labelName = QtWidgets.QLabel('Clamp')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(60, 10)
        h_layout.addSpacerItem(spacer)

        clamp_checkbox = QtWidgets.QCheckBox('Mirror')
        h_layout.addWidget(clamp_checkbox)

        def updateMirror():
            self.Bake.bake_data.mirror = clamp_checkbox.isChecked()

        clamp_checkbox.stateChanged.connect(updateMirror)

        spacer = QtWidgets.QSpacerItem(21, 10)
        h_layout.addSpacerItem(spacer)

        # Name Label
        labelName = QtWidgets.QLabel('Easing')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtWidgets.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        self.bake_clamp_easing_combobox = QtWidgets.QComboBox()
        self.bake_clamp_easing_combobox.addItems(Easing.EasingList())
        h_layout.addWidget(self.bake_clamp_easing_combobox)
        self.inner_layout.addLayout(h_layout)

    def bakeSolidButtons(self):
        h_layout = QtWidgets.QHBoxLayout()
        black_button = QtWidgets.QPushButton('BAKE SELECTED BLACK')
        h_layout.addWidget(black_button)
        white_button = QtWidgets.QPushButton('BAKE SELECTED WHITE')
        h_layout.addWidget(white_button)
        self.inner_layout.addLayout(h_layout)

        black_button.clicked.connect(self.Bake.bake_black)
        white_button.clicked.connect(self.Bake.bake_white)

    def bakeButton(self):
        h_layout = QtWidgets.QHBoxLayout()
        bake_button = QtWidgets.QPushButton('BAKE SELECTED MESH')
        h_layout.addWidget(bake_button)
        self.inner_layout.addLayout(h_layout)

        def bake():
            self.Bake.objects = pc.ls(sl=True)
            bakeEasing = Easing.EasingDictionary()[self.bake_easing_combobox.currentText()]
            clampEasing = Easing.EasingDictionary()[self.bake_clamp_easing_combobox.currentText()]
            t = self.bake_type_combobox.currentText()
            if 'Radial In' in t:
                self.Bake.radial_bounds(bakeEasing, clampEasing, inner=True)
            if 'Radial Out' in t:
                self.Bake.radial_bounds(bakeEasing, clampEasing, inner=False)
            if 'Spherical In' in t:
                self.Bake.spherical_bounds(bakeEasing, clampEasing, inner=True)
            if 'Spherical Out' in t:
                self.Bake.spherical_bounds(bakeEasing, clampEasing, inner=False)
            if 'Box' in t:
                self.Bake.box_bounds(bakeEasing, clampEasing)
            if 'Branching' in t:
                self.Bake.branching(bakeEasing)
            self.Bake.objects = None

        bake_button.clicked.connect(bake)

    def progressBar(self):
        progress_bar = QtWidgets.QProgressBar()
        self.inner_layout.addWidget(progress_bar)
        self.Bake.progressBar = progress_bar
