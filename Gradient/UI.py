from PySide import QtGui, QtCore
from maya.app.general.mayaMixin import MayaQDockWidget
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from Maya_VertexColor.Gradient import Bake
from Maya_UtilLib.UI import getMayaWindow
from Maya_UtilLib import Easing
import pymel.core as pc


class BakeTool(MayaQWidgetDockableMixin, QtGui.QDialog):
    toolName = 'vertexColorWidget'
    """
    VertexColor UI Class
    """
    def __init__(self, parent=None):
        # creating main Bake object
        self.Bake = Bake.Bake()
        self.selected = []
        self.originLocators = []
        self.dirLocators = []
        self.bakeRadioType = 'pivot'
        self.Easing = Easing.Linear
        self.ClampEasing = Easing.Linear

        self.delete_instance()

        super(self.__class__, self).__init__(parent=parent)
        self.mayaMainWindow = getMayaWindow()
        self.setObjectName(self.__class__.toolName)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('VertexColor Bake')
        self.setMinimumWidth(375)
        self.setMaximumWidth(375)
        self.setMaximumHeight(300)

        # main vertical layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)

        self.inner_layout = QtGui.QVBoxLayout(self)
        self.inner_layout.setAlignment(QtCore.Qt.AlignTop)

        self.font = QtGui.QFont()
        self.font.setPixelSize(12)
        self.font.setBold(True)

        # pre-declaring combo box variables
        self.bake_type_combobox = None
        self.bake_easing_combobox = None
        self.bake_clamp_easing_combobox = None

        self.bakeType()
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

    def delete_instance(self):
        mayaMainWindow = getMayaWindow()

        # Go through main window's children to find any previous instances
        for obj in mayaMainWindow.children():
            if type(obj) == MayaQDockWidget:
                # if obj.widget().__class__ == self.__class__:
                #  Alternatively we can check with this, but it will fail if we re-evaluate the class
                if obj.widget().objectName() == self.__class__.toolName:  # Compare object names
                    # If they share the same name then remove it
                    print 'Deleting instance {0}'.format(obj)
                    # This will remove from right-click menu, but won't actually delete it!
                    # ( still under mainWindow.children() )
                    mayaMainWindow.removeDockWidget(obj)
                    # Delete it for good
                    obj.setParent(None)
                    obj.deleteLater()

    def bakeType(self):
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        type_label = QtGui.QLabel('Type')
        h_layout.addWidget(type_label)
        # add spacer
        spacer = QtGui.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        self.bake_type_combobox = QtGui.QComboBox()
        self.bake_type_combobox.addItems(['Radial In Bounds', 'Radial Out Bounds', 'Spherical In Bounds', 'Spherical Out Bounds', 'Box Bounds', 'Branching (Coming Soon)'])

        h_layout.addWidget(self.bake_type_combobox)

        # Name Label
        easing_label = QtGui.QLabel('Easing')
        h_layout.addWidget(easing_label)
        # add spacer
        spacer = QtGui.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        self.bake_easing_combobox = QtGui.QComboBox()
        self.bake_easing_combobox.addItems(Easing.EasingList())
        h_layout.addWidget(self.bake_easing_combobox)

        self.inner_layout.addLayout(h_layout)

    def bakeValues(self):
        h_layout = QtGui.QHBoxLayout()

        min_label = QtGui.QLabel('Min')
        min_input = QtGui.QDoubleSpinBox()
        min_input.setValue(self.Bake.bakeMin)
        min_input.setSingleStep(0.001)
        min_input.setDecimals(3)

        def updateMin():
            self.Bake.bakeMin = float(min_input.text())

        min_input.valueChanged.connect(updateMin)

        max_label = QtGui.QLabel('Max')
        max_input = QtGui.QDoubleSpinBox()
        max_input.setValue(self.Bake.bakeMax)
        max_input.setSingleStep(0.001)
        max_input.setDecimals(3)

        def updateMax():
            self.Bake.bakeMax = float(max_input.text())

        max_input.valueChanged.connect(updateMax)

        offset_label = QtGui.QLabel('Offset')
        offset_input = QtGui.QDoubleSpinBox()
        offset_input.setValue(self.Bake.bakeOffset)
        offset_input.setSingleStep(0.001)
        offset_input.setDecimals(3)

        def updateOffset():
            self.Bake.bakeOffset = float(offset_input.text())

        offset_input.valueChanged.connect(updateOffset)

        scale_label = QtGui.QLabel('Scale')
        scale_input = QtGui.QDoubleSpinBox()
        scale_input.setValue(self.Bake.bakeScale)
        scale_input.setSingleStep(0.001)
        scale_input.setDecimals(3)

        def updateScale():
            self.Bake.bakeScale = float(scale_input.text())

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
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        labelName = QtGui.QLabel('From')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        # Bake Origin: Origin, Center, Pivot, Point (Create Locator with Label that represents point)
        origin_radio_button = QtGui.QRadioButton('Origin')
        center_radio_button = QtGui.QRadioButton('Center')
        pivot_radio_button = QtGui.QRadioButton('Pivot')
        given_radio_button = QtGui.QRadioButton('Given')

        pivot_radio_button.setChecked(True)
        self.Bake.StartAtPivot()

        def originChanged():
            if origin_radio_button.isChecked():
                self.bakeRadioType = 'origin'
                self.Bake.StartAtOrigin()

        def centerChanged():
            if center_radio_button.isChecked():
                self.bakeRadioType = 'center'
                self.Bake.StartAtCenter()

        def pivotChanged():
            if pivot_radio_button.isChecked():
                self.bakeRadioType = 'pivot'
                self.Bake.StartAtPivot()

        def givenChanged():
            if given_radio_button.isChecked():
                self.bakeRadioType = 'given'
                self.Bake.StartAtPoint(self.Bake.clampPoint)

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
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        labelName = QtGui.QLabel('Given')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(53, 10)
        h_layout.addSpacerItem(spacer)

        x_label = QtGui.QLabel('X')
        x_input = QtGui.QLineEdit()
        x_input.setInputMask('0.000')
        x_input.setMaxLength(5)
        x_input.setText(str(self.Bake.clampPoint[0]))

        def updateX():
            self.Bake.clampPoint[0] = float(x_input.text())

        x_input.textChanged.connect(updateX)

        y_label = QtGui.QLabel('Y')
        y_input = QtGui.QLineEdit()
        y_input.setInputMask('0.000')
        y_input.setMaxLength(5)
        y_input.setText(str(self.Bake.clampPoint[1]))

        def updateY():
            self.Bake.clampPoint[1] = float(y_input.text())

        y_input.textChanged.connect(updateY)

        z_label = QtGui.QLabel('Z')
        z_input = QtGui.QLineEdit()
        z_input.setInputMask('0.000')
        z_input.setMaxLength(5)
        z_input.setText(str(self.Bake.clampPoint[2]))

        def updateZ():
            self.Bake.clampPoint[2] = float(z_input.text())

        z_input.textChanged.connect(updateZ)

        h_layout.addWidget(x_label)
        h_layout.addWidget(x_input)
        h_layout.addWidget(y_label)
        h_layout.addWidget(y_input)
        h_layout.addWidget(z_label)
        h_layout.addWidget(z_input)

        self.inner_layout.addLayout(h_layout)

    def bakeDirection(self):
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        labelName = QtGui.QLabel('Direction')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(35, 10)
        h_layout.addSpacerItem(spacer)

        x_label = QtGui.QLabel('X')
        x_input = QtGui.QLineEdit()
        x_input.setInputMask('0.000')
        x_input.setMaxLength(5)
        x_input.setText(str(self.Bake.clampDir[0]))

        def updateX():
            self.Bake.clampDir[0] = float(x_input.text())

        x_input.textChanged.connect(updateX)

        y_label = QtGui.QLabel('Y')
        y_input = QtGui.QLineEdit()
        y_input.setInputMask('0.000')
        y_input.setMaxLength(5)
        y_input.setText(str(self.Bake.clampDir[1]))

        def updateY():
            self.Bake.clampDir[1] = float(y_input.text())

        y_input.textChanged.connect(updateY)

        z_label = QtGui.QLabel('Z')
        z_input = QtGui.QLineEdit()
        z_input.setInputMask('0.000')
        z_input.setMaxLength(5)
        z_input.setText(str(self.Bake.clampDir[2]))

        def updateZ():
            self.Bake.clampDir[2] = float(z_input.text())

        z_input.textChanged.connect(updateZ)

        h_layout.addWidget(x_label)
        h_layout.addWidget(x_input)
        h_layout.addWidget(y_label)
        h_layout.addWidget(y_input)
        h_layout.addWidget(z_label)
        h_layout.addWidget(z_input)

        self.inner_layout.addLayout(h_layout)

    def bakeClearChannels(self):
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        labelName = QtGui.QLabel('Clear Channels')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        # Bake Channels: Green, Red, Blue, Alpha
        green_checkbox = QtGui.QCheckBox('Green')
        red_checkbox = QtGui.QCheckBox('Red')
        blue_checkbox = QtGui.QCheckBox('Blue')
        alpha_checkbox = QtGui.QCheckBox('Alpha')

        def updateG():
            self.Bake.cG = green_checkbox.isChecked()

        green_checkbox.stateChanged.connect(updateG)

        def updateR():
            self.Bake.cR = red_checkbox.isChecked()

        red_checkbox.stateChanged.connect(updateR)

        def updateB():
            self.Bake.cB = blue_checkbox.isChecked()

        blue_checkbox.stateChanged.connect(updateB)

        def updateA():
            self.Bake.cA = alpha_checkbox.isChecked()

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
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        labelName = QtGui.QLabel('Paint Channels')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        # Bake Channels: Green, Red, Blue, Alpha
        green_checkbox = QtGui.QCheckBox('Green')
        red_checkbox = QtGui.QCheckBox('Red')
        blue_checkbox = QtGui.QCheckBox('Blue')
        alpha_checkbox = QtGui.QCheckBox('Alpha')

        def updateG():
            self.Bake.rG = green_checkbox.isChecked()

        green_checkbox.stateChanged.connect(updateG)

        def updateR():
            self.Bake.rR = red_checkbox.isChecked()

        red_checkbox.stateChanged.connect(updateR)

        def updateB():
            self.Bake.rB = blue_checkbox.isChecked()

        blue_checkbox.stateChanged.connect(updateB)

        def updateA():
            self.Bake.rA = alpha_checkbox.isChecked()

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
        h_layout = QtGui.QHBoxLayout()

        # Name Label
        labelName = QtGui.QLabel('Clamp')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(60, 10)
        h_layout.addSpacerItem(spacer)

        clamp_checkbox = QtGui.QCheckBox('Mirror')
        h_layout.addWidget(clamp_checkbox)

        def updateMirror():
            self.Bake.mirror = clamp_checkbox.isChecked()

        clamp_checkbox.stateChanged.connect(updateMirror)

        spacer = QtGui.QSpacerItem(21, 10)
        h_layout.addSpacerItem(spacer)

        # Name Label
        labelName = QtGui.QLabel('Easing')
        h_layout.addWidget(labelName)
        # add spacer
        spacer = QtGui.QSpacerItem(15, 10)
        h_layout.addSpacerItem(spacer)

        self.bake_clamp_easing_combobox = QtGui.QComboBox()
        self.bake_clamp_easing_combobox.addItems(Easing.EasingList())
        h_layout.addWidget(self.bake_clamp_easing_combobox)
        self.inner_layout.addLayout(h_layout)

    def bakeSolidButtons(self):
        h_layout = QtGui.QHBoxLayout()
        black_button = QtGui.QPushButton('BAKE SELECTED BLACK')
        h_layout.addWidget(black_button)
        white_button = QtGui.QPushButton('BAKE SELECTED WHITE')
        h_layout.addWidget(white_button)
        self.inner_layout.addLayout(h_layout)

        black_button.clicked.connect(self.Bake.bakeBlack)
        white_button.clicked.connect(self.Bake.bakeWhite)

    def bakeButton(self):
        h_layout = QtGui.QHBoxLayout()
        bake_button = QtGui.QPushButton('BAKE SELECTED MESH')
        h_layout.addWidget(bake_button)
        self.inner_layout.addLayout(h_layout)

        def bake():
            self.Bake.objects = pc.ls(sl=True)
            bakeEasing = Easing.EasingDictionary()[self.bake_easing_combobox.currentText()]
            clampEasing = Easing.EasingDictionary()[self.bake_clamp_easing_combobox.currentText()]
            t = self.bake_type_combobox.currentText()
            if 'Radial In' in t:
                self.Bake.RadialBounds(bakeEasing, clampEasing, inner=True)
            if 'Radial Out' in t:
                self.Bake.RadialBounds(bakeEasing, clampEasing, inner=False)
            if 'Spherical In' in t:
                self.Bake.SphericalBounds(bakeEasing, clampEasing, inner=True)
            if 'Spherical Out' in t:
                self.Bake.SphericalBounds(bakeEasing, clampEasing, inner=False)
            if 'Box' in t:
                self.Bake.BoxBounds(bakeEasing, clampEasing)
            if 'Branching' in t:
                self.Bake.Branching(bakeEasing)
            self.Bake.objects = None

        bake_button.clicked.connect(bake)

    def progressBar(self):
        self.inner_layout.addWidget(self.Bake.progressBar)
