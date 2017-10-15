import pymel.core as pm
import maya.mel
from functools import partial
# Function creates a material which is applied to the selected object.

dieletricSpecularValues = [0.05, 0.9]
metalicSpecularValues = [0.9, 0.9]

GlobalNodeName = 'SET_JT_RenderMan_GlobalNode_MaterialSCRIPT_01'

# global Node used to connect different material Tree nodes to for future reference.
if pm.objExists('SET_JT_RenderMan_GlobalNode_MaterialSCRIPT_01') == False:

    GlobalNode = pm.sets(empty=True, n='SET_JT_RenderMan_GlobalNode_MaterialSCRIPT_01')
    pm.lockNode(GlobalNode, l=True)


# use the lock and unlock to keep set safe

def lockGlobal():
    pm.lockNode(GlobalNode, l=True)


def unlockGlobal():
    pm.lockNode(GlobalNode, l=False)


def addSetToGlobal(set):
    unlockGlobal()
    pm.select(set, ne=True, r=True)
    pm.sets(GlobalNodeName, edit=True, fe=True)
    lockGlobal()

def listExsistingMaterialsInSets():
    exsistingMaterials = []
    Sets = pm.sets(GlobalNodeName,q=True)
    for x in Sets:
        list = pm.sets(x,q=True)
        for y in list:
            if pm.objectType(y) == 'PxrSurface':
                exsistingMaterials.append(y)
    return exsistingMaterials
    
class ShaderTree():
    def __init__(self, name):
        self.TreeName = name
        self.MixerLayersAvailibility = {'baselayer': False, 'layer1': False, 'layer2': False, 'layer3': False,
                                        'layer4': False}
        self.listObjectsAppliedTo = []
        self.IDAttr = 'ID_' + name + '_01'
        self.Shader = ''
        self.Set = ''
        self.TreeSet = ''
        self.Mixer = ''
        self.Layers = []
        self.Textures = []
    # method to create shader and shaderSet
    def addShader(self,shader):
        self.Shader = shader
        self.Set = pm.listConnections(self.Shader,type='shadingEngine')[0]
        self.Mixer = pm.listConnections(self.Shader,type='PxrLayerMixer')
        self.Layers = pm.listConnections(self.Mixer,type='PxrLayer')
    def createShader(self):
        self.Shader = pm.shadingNode('PxrSurface', asShader=True, n='MAT_' + self.TreeName)
        self.Set = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.Shader + 'SG')
        self.TreeSet = pm.sets(empty=True, name='SET_' + self.TreeName)
        pm.connectAttr(self.Shader + ".outColor", self.Set + ".surfaceShader", f=True)
        addSetToGlobal(self.TreeSet)
        pm.select(self.Shader, r=True)
        pm.sets(self.TreeSet, e=True, forceElement=True)
        pm.select(self.Set, r=True)
        pm.sets(self.TreeSet, e=True, forceElement=True)

    # apply shader to selected objects
    def applyShaderToSelected(self):
        List = pm.ls(sl=True)
        for object in List:
            pm.select(object)
            pm.hyperShade(a=self.Shader)
            pm.sets(self.Set, e=True, forceElement=True)
            self.listObjectsAppliedTo.append(object)

    # add a mixer to the shader
    def addMixer(self):
        self.Mixer = pm.shadingNode('PxrLayerMixer', asTexture=True, n='MIX_' + self.TreeName)
        pm.connectAttr(self.Mixer + '.pxrMaterialOut', self.Shader + '.inputMaterial', f=True)
        pm.select(self.Mixer, r=True)
        pm.sets(self.TreeSet, e=True, forceElement=True)

    # add layers to the mixer node
    def addLayer(self):
        Rman_Layer = pm.shadingNode('PxrLayer', asTexture=True, n='LAYER_' + self.TreeName)
        if self.MixerLayersAvailibility['baselayer'] == False:
            pm.connectAttr(Rman_Layer + '.pxrMaterialOut', self.Mixer + '.baselayer')
            self.Layers.append(Rman_Layer)
            self.MixerLayersAvailibility['baselayer'] = True
            pm.select(Rman_Layer, r=True)
            pm.sets(self.TreeSet, e=True, forceElement=True)
        elif self.MixerLayersAvailibility['layer1'] == False:
            pm.connectAttr(Rman_Layer + '.pxrMaterialOut', self.Mixer + '.layer1')
            self.Layers.append(Rman_Layer)
            self.MixerLayersAvailibility['layer1'] = True
            pm.select(Rman_Layer, r=True)
            pm.sets(self.TreeSet, e=True, forceElement=True)
        elif self.MixerLayersAvailibility['layer2'] == False:
            pm.connectAttr(Rman_Layer + '.pxrMaterialOut', self.Mixer + '.layer2')
            self.Layers.append(Rman_Layer)
            self.MixerLayersAvailibility['layer2'] = True
            pm.select(Rman_Layer, r=True)
            pm.sets(self.TreeSet, e=True, forceElement=True)
        elif self.MixerLayersAvailibility['layer3'] == False:
            pm.connectAttr(Rman_Layer + '.pxrMaterialOut', self.Mixer + '.layer3')
            self.Layers.append(Rman_Layer)
            self.MixerLayersAvailibility['layer3'] = True
            pm.select(Rman_Layer, r=True)
            pm.sets(self.TreeSet, e=True, forceElement=True)
        elif self.MixerLayersAvailibility['layer4'] == False:
            pm.connectAttr(Rman_Layer + '.pxrMaterialOut', self.Mixer + '.layer4')
            self.Layers.append(Rman_Layer)
            self.MixerLayersAvailibility['layer4'] = True
            pm.select(Rman_Layer, r=True)
            pm.sets(self.TreeSet, e=True, forceElement=True)
        else:
            pm.warning('No Further Layers Available')

    # add texture nodes to the shader
    def addTexture(self, input, file, name):
        Rman_Texture = pm.shadingNode('PxrTexture', asTexture=True, n='TEX_' + self.TreeName)
        Rman_Manifold2D = pm.shadingNode('PxrManifold2D', asTexture=True, n='MAN2D_' + self.TreeName)
        pm.connectAttr(Rman_Manifold2D + '.result', Rman_Texture + '.manifold')
        self.Textures.append([Rman_Texture, Rman_Manifold2D])
        pm.select(Rman_Texture, Rman_Manifold2D, r=True)
        pm.sets(self.TreeSet, e=True, forceElement=True)

# the object too apply the material node too

# is this an exsisting material or no?

# is it dieletric or metalic or both?

# does it have roughness, normal, diffuse, incandesense, subsurface ?

# renderman preset material list : glass, frosted glass, oil, copper, etc

#  option applyShaderToSelectedto delete material tree

# list of already made material trees, use ID attributes to organize

class Renderman_MaterialTool():

    def __init__(self):

        self.windowName = 'window'

        self.windowWidth = 400
        self.windowHeight = 600

        self.widgets = {}
        self.MaterialList = {}
        
        exsistingMaterials = listExsistingMaterialsInSets()
        for mat in exsistingMaterials:
            self.MaterialList[mat] = ShaderTree(mat.partition('MAT_')[2])
            self.MaterialList[mat].addShader(mat)
            
        self.createWindow(self.windowName, self.windowWidth, self.windowHeight)

        

    def createWindow(self,windowname,windowWidth,windowHeight):

        if pm.window(windowname,exists=True) ==True :
            pm.deleteUI(windowname)

        self.widgets['Window'] = pm.window(windowname, w = windowWidth, h = windowHeight, mxb = False, t=windowname)

        self.widgets['mainLayout'] = pm.columnLayout(w = windowWidth, h = windowHeight,adj=True)

        pm.button(l='Create new material tree',c=partial(self.MakeMaterial))
        
        pm.text(label="List of Materials:   ")

        MaterialsOptionMenu = pm.textScrollList("MaterialList", w=300)
        #self.MaterialsOptionMenuPopulate()

        pm.button(l='Apply Material',c=partial(self.ApplyMaterial))

        pm.button(l='Enable Layers',c=partial(self.EnableLayers))

        pm.button(l='Add Layer',c=partial(self.AddLayers))


        pm.showWindow(self.widgets['Window'])
    def MaterialsOptionMenuPopulate(self,*args):
        for x in self.MaterialList :
            pm.textScrollList("MaterialList",e=True,append = x.Shader)
    def MakeMaterial(self,*args):

        result = pm.promptDialog(
            title='Name Material',
            message='Enter Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
        if result == 'OK':
            Name = pm.promptDialog(query=True, text=True)
        
        self.MaterialList['MAT_'+Name] = ShaderTree(Name)
        ShaderTree(Name).createShader()
        pm.textScrollList("MaterialList",e=True,append = self.MaterialList['MAT_'+Name].Shader)


    def ApplyMaterial(self,*args):
        selectedMaterial = pm.textScrollList("MaterialList", q=True, si=True)
        print selectedMaterial
        self.MaterialList[selectedMaterial].applyShaderToSelected()
    def EnableLayers(self,*args):
        selectedMaterial = pm.textScrollList("MaterialList", q=True, si=True)
        self.MaterialList[selectedMaterial].addMixer()
    def AddLayers(self,*args):
        selectedMaterial = pm.textScrollList("MaterialList", q=True, si=True)
        self.MaterialList[selectedMaterial].addLayer()
        
UI = Renderman_MaterialTool()
UI.MaterialList[0]