# Maya-VertexColor
Vertex Color Baking Tool

##Instillation instructions:

#Step 1:

If you do not already have a Maya.env file located at C:\Users\-User Name Here-\Documents\maya\-Maya Version-
Create an empty Maya.Env file and add the following to the file:
PYTHONPATH = -Path to Parent Repository Directory-

For example:
PYTHONPATH = C:/Users/Leo/Documents/maya/Tools;

Note: The repository exists as a child to the Tools directory.

You can reference multiple directories like this:
PYTHONPATH = C:/Users/Leo/Documents/maya/Tools;C:/Users/Leo/Documents/maya/Code/Misc;

#Step 2:

If you already have an existing userSetup.py script in your Maya scripts directory append the following.
If not create an empty userSetup.py script and add the following to the file:
#--------------------------------------------------------------------------------
import sys
import maya.utils as utils

def Loader():
	try:
		import Maya_Rigging
	except:
		pass
	try:
		import Maya_VertexColor
	except:
		pass
	import Maya_UtilLib
	Maya_UtilLib.Menu.Draw()

utils.executeDeferred('Loader()')
#--------------------------------------------------------------------------------