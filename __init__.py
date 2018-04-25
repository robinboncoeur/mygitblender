# ---------------------------------------------------------------------
# File: __init__.py (for figure_shaders)
# ---------------------------------------------------------------------
# Copyright (c) 16-Nov-2015, Robyn Hahn
# Revision: 05-Apr-2018
#
# ***** BEGIN GPL LICENSE BLOCK *****
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA.
# ***** END GPL LICENCE BLOCK *****

bl_info = {
  "name": "Shaders for Imported Figures",
  "author": "Robyn Hahn",
  "version": (0, 5, 7),
  "blender": (2, 79, 0),
  "location": "View3D",
  "description": "Generates simple Cycles shaders for imported OBJ Figures",
  "warning": "Reads settings from CSV only, does not save any to CSV, all stored in the .blend.",
  "wiki_url": "",
  "category": "Material"}


if "bpy" in locals():
  import imp

  imp.reload(figure_defs)
  imp.reload(make_shader)
else:
  from . import figure_defs
  from . import make_shader
"""
NOTE: ===> make_shaders before . is the folder
           make_shader after . is the file
           so, from folder_name.file_name import... etc
"""
from make_shaders.make_shader import buildShader
from make_shaders.figure_defs import matZones
import csv
import sys
import os
import bpy
from bpy.types import (
  Panel,
  Operator,
  PropertyGroup,
  AddonPreferences,
  )
from bpy.props import (
  EnumProperty,
  FloatProperty,
  StringProperty,
  PointerProperty,
  CollectionProperty,
  )


siniMsg = figure_defs.sMsg
thisOS_name = os.name

def showErrMsg(sMsg):
  if sMsg == "INVALIDMAT":
    longMsg = "375-Unable to assign shaders to one material: invalid mat zone."
  if sMsg == "PATH":
    longMsg = "500-Missing path_list.csv. Copy this file to the folder "
    longMsg += "containing your .blend and edit it."
  if sMsg == "IMGLIST":
    longMsg = "425-Your path_list.csv points to a folder missing the image_list.csv file."
  if sMsg == "IMAGE":
    longMsg = "230-image_list.csv points to a missing image file."
  if sMsg == "BADDICT":
    longMsg = "625-Either image_list.csv or path_list.csv "
    longMsg += "is missing a double-quote. Please double-check your files for typos."
  if sMsg == "NOPARMS":
    longMsg = "500-Missing parm_list.csv. Copy this file to the folder "
    longMsg += "containing your .blend and edit it."
  if sMsg == "BADPARM":
    longMsg = "400-A problem has been detected with your parm_list.csv file."
  if sMsg == "BADPATH":
    longMsg = "750-path_list.csv has an invalid path statement. Please refer to the "
    longMsg += "readme.md on the FigureShader git page for help on this issue."
  if len(sMsg) < 1:
    longMsg = "200-Another problem occurred."
  # this if len() assumes imgfile name.ext is going to be longer than 9 chars
  if not sMsg == "INVALIDMAT":
    if len(sMsg) > 9:
      longMsg = "650-The file:  [ " + sMsg + " ]  is missing, or the file name is spelled "
      longMsg += "incorrectly in image_list.csv in that images folder."

  return longMsg


""" create array of entries in the csv, gets turned into a dictionary"""
def readList(fname):
  rval = []
  sRet = "FILEEXISTS"
  try:
    with open(fname, 'r') as csvfile:
      pass
  except IOError as e:
    sRet = "NOPARMS"
  if sRet == "FILEEXISTS":
    with open(fname, 'r') as csvfile:
      r = csv.reader(csvfile, delimiter=',')
      for row in r:
        if not len(row) == 0:
          rval.append(row)
  else:
    rval=sRet
  return rval

def cleanStr(sStr):
  if not sStr is None:
    # Clean off empty string before or after
    sStr = sStr.strip()
    if sStr.startswith('"'):
      sStr = sStr[1:]
    if sStr.endswith('"'):
      sStr = sStr[:-1]
    # print("CleanStr()...post-cleaning, sStr is: " + sStr)
  return sStr

def parmDictGet(stringParm):
  """
  parm_list.csv is in .blend's current location (path)
  principledShader values:
  "fl01_sssval",".012"
  "fl02_sssrad",".220"
  "fl05_spcamt",".500"
  "fl11_sheenv",".200"
  "fl14_iorval","1.80"
  """
  sRet = "FILEEXISTS"
  parm_path = bpy.data.filepath
  parm_dir = os.path.dirname(parm_path)
  parm_listpath = os.path.join(parm_dir, 'parm_list.csv')
  parm_list = readList(parm_listpath)
  if not parm_list == "NOPARMS":
    parmdict = dict(parm_list)
    stringParm = parmdict.get(stringParm)
  if parm_list == "NOPARMS":
    stringParm = "NOPARMS"
  return stringParm

def updFigure(self, context):
  scn = bpy.context.scene
  sSelectedFigure = scn.objects[(scn.FS_FigureList)]
  for object in bpy.data.objects:
    object.select = False
  sSelectedFigure.select = True
  print ("Selected obj is: ", sSelectedFigure.name)

def updImgPath(self, context):
  pass
  scn = bpy.context.scene
  sSelectedFigure = scn.objects[(scn.FS_FigureList)]
  for object in bpy.data.objects:
    object.select = False
  sSelectedFigure.select = True
  #print ("Selected obj is: ", sSelectedFigure.name)

def pop_figList(self, context):
  """ enum property callback:
  expects a tuple containing (identifier, name, description) """
  allItems = [("NoID", "NoName","NoDesc")]
  if len(bpy.context.scene.objects) != 0:
    allItems = []
    for items in bpy.context.scene.objects:
      allItems.append((items.name,items.name,items.name))
  return allItems

def pop_imgList(self, context):
  allItems = [("1","pic1",""),
              ("2","pic2",""),
              ("3","pic3",""),
              ("4","pic4",""),
              ]
  return allItems

def pop_baseFig(self, context):
  allItems = [("V4","Victoria4",""),
              ("Mariko","Mariko",""),
              ("Dawn","Dawn",""),
              ("Antonia","Antonia",""),
              ]
  return allItems

def pop_shadType(self, context):
  allItems = [("PrinSSS","Principled SSS",""),
              ("NodeSSS","Node-Based SSS",""),
              ]
  return allItems

def pop_Parms():
  items=[ ("flSssVal","fl01_sssval",0.000),
          ("flSssRad","fl02_sssrad",0.000),
          ("flSpcAmt","fl05_spcamt",0.000),
          ("flSheenV","fl11_sheenv",0.000),
          ("flIorVal","fl14_iorval",0.000),
        ]
  return items



def getMessage(msgStr, retv=None):
  sep = ('-')
  if retv == "str":
    cMsg = msgStr.split(sep, 1)[1]
  else:
    cMsg = msgStr.split(sep)[0]
  return cMsg

class MessageOperator(bpy.types.Operator):
  bl_idname = "system.message"
  bl_label = "Message"
  type = StringProperty()
  message = StringProperty()
  mesglen = 0

  def execute(self, context):
    self.report({'INFO'}, self.message)
    print(self.message)
    return {'FINISHED'}

  def invoke(self, context, event):
    cMsgS = self.message
    self.message = getMessage(cMsgS,"str")
    cMsgS = getMessage(cMsgS)
    #print("cMsgS is: " + cMsgS)
    self.mesglen = int(cMsgS)
    wm = context.window_manager
    #self.mesglen = (len(self.message) * 5.5) + len(self.message)
    return wm.invoke_popup(self, width=self.mesglen, height=400)

  def draw(self, context):
    self.layout.label("Please Note")
    layout = self.layout
    row = layout.row(align=False)
    row.label(text=self.message)
    row = layout.row()
    row.alignment='RIGHT'
    row.operator("system.ok")

class OkOperator(bpy.types.Operator):
  bl_idname = "system.ok"
  bl_label = "OK"
  def execute(self, context):
    return {'FINISHED'}

"""
ParmStore() and CsvXchng() are initialised using the Load button over the
PrincipledShader set. Used for retrieving from CSV, storing and (using the
Save Button) writing values to CSV.
class ParmTools(PropertyGroup):
  savedVals = CollectionProperty()
  floatField = StringProperty()
"""



class PanelTools(PropertyGroup):
  bl_idname = "panel.shaderdata"
  bl_label = "Set up for Shaders"

  #========== Shader Choice ==========================
  sSelShader = StringProperty(
    name="selectedShader",
    description="chosen shader",
    )

  shaderEnum = EnumProperty(
    name="shaderType",
    description="Choose shader type:",
    items=pop_shadType
    )

  #========== Base Figure ============================
  sBaseFgr = StringProperty(
    name="baseFigure",
    description="core figure the mesh is based on",
    default="V4",
    )

  baseFigEnum = EnumProperty(
    name="figureType",
    description="Choose base figure name",
    items=pop_baseFig
    )

  #========== Selected Object ========================
  sSelFgr = StringProperty(
    name="selectedFigure",
    description="figure currently selected",
    default="",
    )

  curFigEnum = EnumProperty(
    name="figureList",
    description="Choose figure for shaders",
    items=pop_figList,
    update=updFigure,
    default=None
    )

  #========== Path to Images =========================
  imgpath = StringProperty(
    name="imagePath",
    description="Choose a directory:",
    default="",
    maxlen=1024,
    subtype='DIR_PATH'
    )

  imageEnum = EnumProperty(
    name="selectedImages",
    description="Choose saved image groups:",
    items=pop_imgList,
    update=updImgPath,
    default=None
    )

  #========== Principled Shader Settings =============
  """
  shaderCollect = CollectionProperty(
    name="shaderSettings",
    description="saved Shader Settings",
    items=pop_Parms,
    )
  """

  flSssVal = FloatProperty(
    name="SSS Value",
    description="Increasing beyond .2 will make figure look waxy",
    default=0.2000,
    )

  flSssRad = FloatProperty(
    name="SSS Radiate",
    description="Trying Radiant values...",
    default=0.1500,
    )

  flSpcAmt = FloatProperty(
    name="Spec Tint",
    description="Trying Specular tint values...",
    default=0.1200,
    )

  flSpcRuf = FloatProperty(
    name="Spec Roughness",
    description="Trying Specular roughness values...",
    default=0.800,
    )

  flSheenV = FloatProperty(
    name="Sheen Value",
    description="Trying Sheen values...",
    default=0.0600,
    )

  flIorVal = FloatProperty(
    name="IOR Value",
    description="Suggested skin IOR value is 1.85...",
    default=1.850,
    )





class MatShaderPanel(bpy.types.Panel):
  """Create shaders for imported figures: Panel"""
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'TOOLS'
  bl_label = "Figure Shader"
  bl_context = "objectmode"
  bl_idname = "MATERIALS_PT_shaders"
  bl_category = "FigureShader"

  def draw(self, context):
    layout = self.layout
    scene = bpy.context.scene
    sFgrTool = scene.figTools

    if context.object:
      box = layout.box()
      row = box.row()
      row.label(text="Load or Save Settings")
      row = box.row()
      col = row.column()
      subrow = col.row()
      subrow.operator("object.load_presets", text='Load')
      subrow.operator("object.save_presets", text='Save')

      layout.row().separator()

      box = layout.box()
      row = box.row()
      row.label(text="-1- Select shader type: ")
      row = box.row()
      row.prop(sFgrTool,"shaderEnum",text='')
      row = box.row()
      row.label(text="-2- Find image files: ")
      row = box.row()
      row.prop(sFgrTool, "imgpath", text="")
      row = box.row()
      row.label(text="-3- Figure to paint: ")
      row = box.row()
      row.prop(sFgrTool,"curFigEnum",text='')
      row = box.row()
      row.label(text="-4- Figure Type: ")
      row = box.row()
      row.prop(sFgrTool, "baseFigEnum", "")
      box = layout.box()


      layout.row().separator()

      row = box.row()
      row.label(text="-5- Principled Settings: ")
      row = box.row()
      row.prop(sFgrTool, "flSssVal")
      row = box.row()
      row.prop(sFgrTool, "flSssRad")
      row = box.row()
      row.prop(sFgrTool, "flSpcAmt")
      row = box.row()
      row.prop(sFgrTool, "flSpcRuf")
      row = box.row()
      row.prop(sFgrTool, "flSheenV")
      row = box.row()
      row.prop(sFgrTool, "flIorVal")


      layout.row().separator()

      sub = layout.row(align=True)
      sub.alignment = 'CENTER'
      sub.scale_y = 2.0
      #OUTLINER_OB_ARMATURE
      sub.operator("object.run_script", text='Apply Shaders', icon='POSE_HLT')

    else:
      row = layout.row()
      row.label(text='No Object in Scene')


class LoadPresets(bpy.types.Operator):
  bl_idname = "object.load_presets"
  bl_label = "Loads Shader Presets from CSV"
  @classmethod
  def poll(cls, context):
    def allCondsMet():
      bAllMet = False
      if bpy.path.basename(bpy.context.blend_data.filepath):
        xPath = bpy.path.basename(bpy.context.blend_data.filepath)
        bAllMet = True
      return bAllMet
    return allCondsMet()

  def execute(self, context):
    print("Loading Principled shader vals... ")
    fTools = bpy.context.scene.figTools
    xStr = parmDictGet('fl01_sssval')
    try:
      print("xStr = " + xStr)
    except:
      print("xStr = None")
    items = []

    if xStr == 'NOPARMS':
      sErrorMsg = showErrMsg(xStr)
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
    elif xStr == 'BADPARM':
      sErrorMsg = showErrMsg(xStr)
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
    else:
      """ Really clumsy, but it works """
      #"img_path", "/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/V4/"
      fTools.imgpath = cleanStr(parmDictGet('img_path'))
      fTools.flSssVal = float(parmDictGet('fl01_sssval'))
      fTools.flSssRad = float(parmDictGet('fl02_sssrad'))
      fTools.flSpcAmt = float(parmDictGet('fl05_spcamt'))
      fTools.flSpcRuf = float(parmDictGet('fl06_spcruf'))
      fTools.flSheenV = float(parmDictGet('fl11_sheenv'))
      fTools.flIorVal = float(parmDictGet('fl14_iorval'))
      """
      items.append[("1","fl01_sssval",str(fTools.flSssVal))]
      items.append[("2","fl02_sssrad",str(fTools.flSssRad))]
      items.append[("3","fl05_spcamt",str(fTools.flSpcAmt))]
      items.append[("4","fl11_sheenv",str(fTools.flSheenV))]
      items.append[("5","fl14_iorval",str(fTools.flIorVal))]
      """

    return {'FINISHED'}


class SavePresets(bpy.types.Operator):
  bl_idname = "object.save_presets"
  bl_label = "Saves Shader Presets to CSV"
  @classmethod
  def poll(cls, context):
    def allCondsMet():
      bAllMet = False
      if bpy.path.basename(bpy.context.blend_data.filepath):
        xPath = bpy.path.basename(bpy.context.blend_data.filepath)
        bAllMet = True
      return bAllMet
    return allCondsMet()

  def execute(self, context):
    print("Saving shader vals... ")
    #loadAllPresets()
    return {'FINISHED'}



class RunScript(bpy.types.Operator):
  """ Conditionally runs Make Shaders """
  bl_idname = "object.run_script"
  bl_label = "Invokes Shader Script"

  """
  =============================================================================
   bpy.path.basename() returns the name of the currently active .blend. If un-
   named, returns .F. Button does not activate until file is saved with a name.
  ================================================
  """
  @classmethod
  def poll(cls, context):
    def allCondsMet():
      bAllMet = False
      if bpy.path.basename(bpy.context.blend_data.filepath):
        xPath = bpy.path.basename(bpy.context.blend_data.filepath)
        bAllMet = True
      return bAllMet

    return allCondsMet()

  def execute(self, context):
    sSelShader = bpy.context.scene.figTools.shaderEnum
    sBaseFgr = bpy.context.scene.figTools.baseFigEnum
    sSelFgr =  bpy.context.scene.figTools.curFigEnum
    #print("Selected shader is: " + sSelShader)
    shadersSetup(sBaseFgr, sSelFgr, sSelShader)
    return {'FINISHED'}


def shadersSetup(BaseFigure, SelectedFigure, SelectedShader):
  sMissingFile = ""
  blend_name = ""
  crShader = SelectedShader
  cBaseFig = BaseFigure
  cSeltFig = SelectedFigure

  """
  ================================================================
  Returned the name of the figure if it matched the short list.
  ToDo: Check if the materials in the image_list.csv have
  any corresponding material zones in the selected figure.
  4 functions:
  -readList()
  -cleanStr()
  -paintShaders(): main function
  -check4Files()
  =============================================================
  """



  def paintShaders():
    """
    =============================================================
    These are defined in figure_defs.py. Cuurently defined for:
    V4, Dawn, Mariko, Antonia
    The var Figure is defined in Check4Files, just before
    paintShaders() is invoked.
    ========================================================
    """
    dict_mats = matZones(cBaseFig)

    """
    =============================================================
    Truncates strings like 3_SkinLeg:1 to 3_SkinLeg by detecting
    an extra chars in name, trapping curently for   . and :
    ========================================================
    """
    def getMatName(mtlName):
      sep = 'NF'
      # Blender has added a .001 or .002
      if '.' in mtlName:
        sep = ('.')
      if ':' in mtlName:
        sep = (':')
      # truncate only if a . or : is found
      if not sep == 'NF':
        mtlName = mtlName.split(sep, 1)[0]
      # get the actual material type from the material dictionary
      mtlType = dict_mats.figMat.get(mtlName)
      #print(mtlType)

      if mtlType is None:
        return sep
      else:
        return mtlType

    if bpy.context.scene.render.engine == 'BLENDER_RENDER':
      bpy.context.scene.render.engine = 'CYCLES'

    """ Read the csv files for image location info
    # current location of .blend and path_list.csv
    blend_path = bpy.data.filepath
    blend_dir = os.path.dirname(blend_path)
    csv_listpath = os.path.join(blend_dir, 'path_list.csv')

    # readList() make array of path entries, weed out empties
    csv_list = readList(csv_listpath)
    pathlist = dict(csv_list)

    # gets the path to the images
    if thisOS_name == 'posix':
      path_str = pathlist.get('img_pathP')
    if thisOS_name == 'nt':
      path_str = pathlist.get('img_pathN')
    path_str = cleanStr(path_str) """
    path_str = bpy.context.scene.figTools.imgpath
    imag_dir = os.path.dirname(path_str)
    img_list = os.path.join(imag_dir, 'image_list.csv')
    pic_list = readList(img_list)
    imaglist = dict(pic_list)

    clrALimb = cleanStr(imaglist.get('clrALimb'))
    clrLLimb = cleanStr(imaglist.get('clrLLimb'))
    bmpALimb = cleanStr(imaglist.get('bmpALimb'))
    bmpLLimb = cleanStr(imaglist.get('bmpLLimb'))
    spcALimb = cleanStr(imaglist.get('spcALimb'))
    spcLLimb = cleanStr(imaglist.get('spcLLimb'))
    clr_Body = cleanStr(imaglist.get('clr_Body'))
    bmp_Body = cleanStr(imaglist.get('bmp_Body'))
    spc_Body = cleanStr(imaglist.get('spc_Body'))
    clr_Face = cleanStr(imaglist.get('clr_Face'))
    bmp_Face = cleanStr(imaglist.get('bmp_Face'))
    spc_Face = cleanStr(imaglist.get('spc_Face'))
    clr_Eyes = cleanStr(imaglist.get('clr_Eyes'))
    clrMouth = cleanStr(imaglist.get('clrMouth'))
    bmpMouth = cleanStr(imaglist.get('bmpMouth'))
    clr_Lash = cleanStr(imaglist.get('clr_Lash'))

    """ Not all figures have a bump or spec map. The bump maps can be replaced
    by procedural bump, the spec maps may need another solution, as yet undefined."""
    bmpALimb = None if '0' else bmpALimb
    bmpLLimb = None if '0' else bmpLLimb
    spcALimb = None if '0' else spcALimb
    spcLLimb = None if '0' else spcLLimb
    bmp_Body = None if '0' else bmp_Body
    spc_Body = None if '0' else spc_Body
    bmp_Face = None if '0' else bmp_Face
    spc_Face = None if '0' else spc_Face
    bmpMouth = None if '0' else bmpMouth

    # makes the current figure active
    bpy.context.scene.objects.active = bpy.data.objects[cSeltFig]
    curr_obj = bpy.data.objects[cSeltFig]
    bpy.context.object.active_material_index = 0
    all_slots = bpy.context.object.material_slots

    # iterate through the material slots...
    for i in range(len(all_slots)):
      #print ("identified the figure... " + cSeltFig)
      #img_Bmp = None
      img_Clr = None
      #img_Spc = None

      # Passed parms
      ImgColr = None
      dblBump = 0.00
      dblSpec = 0.00

      bpy.context.object.active_material_index = i

      """
      On occasion empty material slots are created during import from Poser.
      These empty slots will be ignored.
      """
      if not curr_obj.active_material == None:
        mat = curr_obj.active_material
        matName = curr_obj.active_material.name
        #print ("matName = " + matName)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        """ Added 11-10-2016: checks for valid material name """
        matType = getMatName(matName)
        #print ("matType = " + matType)
        if not matType == "NF":
          #print ("matType = " + matType)
          if matType[0:4] == 'Eyes':
            if matType[5:] == 'Lash':
              img_Clr = clr_Lash
            if matType[5:] == 'Clr':
              img_Clr = clr_Eyes
            if matType[5:] == 'Trn':
              img_Clr = None

          if matType[0:4] == 'Skin':
            if matType[5:] == 'Body':
              img_Clr = clr_Body
            if matType[5:] == 'Face':
              img_Clr = clr_Face
            if matType[5:] == 'Arms' or matType[5:] == 'Legs':
              if clrALimb == clrLLimb:
                img_Clr = clrALimb
              else:
                if matType[5:] == 'Arms':
                  img_Clr = clrALimb
                else:
                  img_Clr = clrLLimb
          if matType == 'Mouth':
            img_Clr = clrMouth
          # fully qualified path added
          if img_Clr is not None:
            ImgColr = path_str + img_Clr
            ImgColr = bpy.data.images.load(filepath=ImgColr)
          """ Sending:      figure(obj)--shadertype-material-clrImage--bumpmap--specmap
                            (last two can be None)"""
          new_mat = buildShader(curr_obj, crShader, matType, ImgColr, dblBump, dblSpec)
      else:
        sErrorMsg = showErrMsg("INVALIDMAT")
        bpy.ops.system.message('INVOKE_DEFAULT',
          type = "Error",
          message = sErrorMsg,
          )
        print ("Unable to assign shaders at this time.")


  def check4Files():
    """
    ==============================================================================
    Error handling: [1] missing csv files
    ..............: [2] missing image files (incl incorrect spelling of file)
    ==============================================================================
    -- blend_name: name-only of the currently open .blend file
    -- blend_dir: fully-qualified path to [blend_name] - 'path_list.csv' lives here
    -- blend_path: fully-qualified path with [blend_name]
    """
    #print("Starting shadersSetup function...")
    #print("Made it to check4Files() ---->")

    sRet = "FILEEXISTS"
    blend_name = bpy.path.basename(bpy.context.blend_data.filepath)
    # print(blend_name)
    blend_path = bpy.context.blend_data.filepath
    # print(blend_path)
    blend_dir = os.path.dirname(blend_path)
    # print(blend_dir)

    # readlist() attempts to create list from csv file, if this fails, exit the process
    #  with a .F., which the if() then returns a msg
    """ First, check for path_list"""
    try:
      csv_listpath = os.path.join(blend_dir, "path_list.csv")
      with open(csv_listpath) as file:
        pass
    except IOError as e:
      sRet = "PATH"

    if sRet == "FILEEXISTS":
      # check if image_list.csv is in the right place (or exists)
      csv_listpath = os.path.join(blend_dir, "path_list.csv")
      #print("csv_listpath is: " + csv_listpath)
      csv_list = readList(csv_listpath)
      pathlist = dict(csv_list)
      if thisOS_name == 'posix':
          #print("A-thisOS_Name is: " + thisOS_name)
          path_str = pathlist.get('img_pathP')
      if thisOS_name == 'nt':
          path_str = pathlist.get('img_pathN')
          #print("B-thisOS_Name is: " + thisOS_name)
      path_str = cleanStr(path_str)
      #try:
      if len(path_str) == 0:
      #    pass
      #except:
        sRet = "BADPATH"

      if sRet == "FILEEXISTS":
        #print("sRet is: " + sRet)
        imag_dir = os.path.dirname(path_str)
        # print("The os path is: " + imag_dir)
        img_list = os.path.join(imag_dir, "image_list.csv")
        # print("The whole path is: " + img_list)
        try:
          with open(img_list) as file:
            pass
        except IOError as e:
          #print("could not open: " + img_list)
          sRet = "IMGLIST"

        if sRet == "FILEEXISTS":
          # step through the image_list.csv to check for invalid file references
          imgFile = ""
          pathFile = ""
          retImgName = ""
          pic_list = readList(img_list)
          nVal = len(pic_list)
          nInt = 0
          try:
            imgDict = dict(pic_list)
          except:
            #print("could not create dictionary... ")
            sRet = "BADDICT"

          if sRet == "FILEEXISTS":
            for attr, val in imgDict.items():
              # print("attr: " + attr + ", val: " + val)
              val = imgDict.get(attr, val)
              imgFile = cleanStr(val)
              # print("the current imgFile is: " + imgFile)
              if len(imgFile) < 1:
                # print("val-IN: " + val)
                pass
              else:
                pathFile = os.path.join(imag_dir, imgFile)
                # print("the current pathFile is: " + pathFile)
                try:
                  with open(pathFile) as file:
                    pass
                except IOError as e:
                  # print("could not open: " + val)
                  sRet = val
    return sRet


  """
  ==============================================================================
  Iterate through the objects in the scene, run paintShader only for FILEEXISTS
  ==============================================================================
  """
  scn = bpy.context.scene
  #figName = bpy.context.scene.objects.active.name

  siniMsg = check4Files()
  sErrorMsg = ""
  if siniMsg == "FILEEXISTS":
    for obj in scn.objects:
      if obj.type == 'MESH':
        # FINALLY: run the script!!!
        oName = obj.name
        #print("The current figure name is: " + oName)
        if oName == cSeltFig:
          #print("oName = " + cSeltFig)
          obj.select = True
          paintShaders()
          #obj.name = oName
          obj.select = False
  else:
    sErrorMsg = showErrMsg(siniMsg)
    bpy.ops.system.message('INVOKE_DEFAULT',
      type = "Error",
      message = sErrorMsg,
      )


# Note2Self: first in, best dressed -> last out
def register():
  bpy.utils.register_module(__name__)
  bpy.types.Scene.figTools = PointerProperty(
    name="fgrPanelTools",
    description="figTools",
    type=PanelTools)
#  bpy.typ.Scene.shaderCtls = PointerProperty(
#    name="parmTools",
#    description="shaderCtls",
#    type="ParmTools")

def unregister():
#  del bpy.types.Scene.shaderCtls
  del bpy.types.Scene.figTools
  bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
  register()
