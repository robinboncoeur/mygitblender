# ---------------------------------------------------------------------
# File: __init__.py (for figure_shaders)
# ---------------------------------------------------------------------
# Copyright (c) 16-Nov-2015, Robyn Hahn
# Revision: 07-May-2018
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
  "version": (0, 5, 9),
  "blender": (2, 79, 0),
  "location": "View3D",
  "description": "Generates simple Cycles shaders for imported OBJ Figures",
  "warning": "Beta: testing in Windows, error-handling revisions",
  "wiki_url": "https://github.com/robinboncoeur/FigureShaders/wiki",
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
  if sMsg == "INVLDMAT":
    longMsg = "375-Unable to assign shaders to one material: invalid mat zone."
  if sMsg == "NIMGLIST":
    longMsg = "425-Your parm_list.csv points to a folder missing the image_list.csv file."
  if sMsg == "SAVSUCC":
    longMsg = "260-Your settings have been saved successfully."
  if sMsg == "LODSUCC":
    longMsg = "230-Your settings loaded successfully."
  if sMsg == "BADDICT":
    longMsg = "625-Either image_list.csv or parm_list.csv "
    longMsg += "is missing a double-quote. Please double-check your files for typos."
  if sMsg == "NOPARMS":
    longMsg = "750-Missing parm_list.csv. Create this file after finding your images "
    longMsg += "folder by clicking [Save] in Figure Shader Settings."
  if sMsg == "WRONGIMG":
    longMsg = "900-The image_list.csv might be missing or have information on images "
    longMsg += "in another folder. Please double-check image_list.csv that the files "
    longMsg += "correspond to the entries in image_list.csv."
  if sMsg == "INVLSHAD":
    longMsg = "400-FigureShader only supports Principled Shader at this time."
  if sMsg == "BADPARM":
    longMsg = "400-A problem has been detected with your parm_list.csv file."
  if sMsg == "RLTVPATH":
    longMsg = "750-The path to your image files is in an invalid format. Please untick "
    longMsg += "the 'Relative Path' tickbox when you select the path to the image files."

  """
  this [if len()] assumes imgfile name.ext is going to be longer than 9 chars
  """
  if len(sMsg) > 9:
    longMsg = "750-The file:  [ " + sMsg + " ]  is missing, or the file name "
    longMsg += "is spelled incorrectly in image_list.csv in the images folder."

  return longMsg


def readList(fname):
  """
  Accepts: fname - csv file name with fully-qualified path
  Returns: arrVal - either array of entries in the csv, or str NOVALS
  """
  arrVal = []
  sReturn = fname
  try:
    with open(fname, 'r') as csvfile:
      pass
  except IOError as e:
    sReturn = "NOVALS"
  if sReturn == fname:
    with open(fname, 'r') as csvfile:
      r = csv.reader(csvfile, delimiter=',')
      for row in r:
        if not len(row) == 0:
          arrVal.append(row)
  else:
    arrVal = sReturn
  return arrVal

def cleanStr(sStr):
  if not sStr is None:
    sStr = sStr.strip()
    if sStr.startswith('"'):
      sStr = sStr[1:]
    if sStr.endswith('"'):
      sStr = sStr[:-1]
  return sStr

def chkPathRltv(strPath):
  #if os.name == "posix":
  #  isRelative = True if strPath[:2] == "//" else False
  if os.name == "nt":
    dirName = os.path.dirname
    lenDName = len(str(dirName))
    strPath = strPath[:lenDName + 2]
  isRelative = True if strPath[:2] == "//" else False
  #print ("isRelative is: " + "True" if isRelative else "False")
  return isRelative

def parmDictGet(strParm):
  """
  Accepts: strParm - name of value to extract from csv (str)
  Returns: retParm - a) the value associated to the name (str) or b) NOPARMS
  parm_list.csv is in the .blend current location (path)
  Sample PrincipledShader values in parm_list.csv:
  "img_path","/fully/qualified/image/path/"
  "fl01_sssval",".012"
  "fl02_sssrad",".220"
  "fl05_spcamt",".050"
  "fl06_spcruf",".850"
  "fl11_sheenv",".200"
  "fl14_iorval","1.80"
  """
  retParm = ""
  parm_path = bpy.data.filepath
  parm_dir = os.path.dirname(parm_path)
  parm_list = os.path.join(parm_dir, 'parm_list.csv')
  try:
    with open(parm_list) as file:
      pass
  except IOError as e:
    retParm = "NOPARMS"
  if not retParm == "NOPARMS":
    parmlist = readList(parm_list)
    if not parmlist == "NOVALS":
      parmdict = dict(parmlist)
      retParm = parmdict.get(strParm)
      retParm = cleanStr(retParm)
  return retParm

def parmListSave(lstSettings, pPath):
  """
  This will write from a list (lstSettings) to a file called parm_list.csv in
  the folder named in pPath, creating the file if it does not already exist.
  As this is an action that is unlikely to generate errors, only pass SAVSUCC.
  """
  parm_dir = pPath
  parm_listpath = os.path.join(parm_dir, 'parm_list.csv')
  wrtFile = open(parm_listpath, 'w')
  for item in lstSettings:
    wrtFile.write(item + "\n")
  return "SAVSUCC"

def imgDictGet(stringImg, stringPath):
  """
  Accepts: stringImg  - image name (str)
  .........stringPath - path to image (str)
  Returns: strImage   - a) name of image file (str) or b) NIMGLIST
  image_list.csv is in image folder, folder path to image_list.csv is in
  parm_list.csv. Sample image_list.csv values:
  "clrALimb","RMElaineL.jpg"
  "clrLLimb","RMElaineL.jpg"
  "bmpALimb","RMElaineLBnh.jpg"
  "bmpLLimb","RMElaineLBnh.jpg"
  "spcALimb","RMElaineLS.jpg"
  "spclLimb","RMElaineLS.jpg"
  "clr_Body","RMElaineT.jpg"
  "bmp_Body","RMElaineTB.jpg"
  "spc_Body","RMElaineTS.jpg"
  "clr_Face","RMElaineHCnh.jpg"
  "bmp_Face","RMElaineHBnh.jpg"
  "spc_Face","RMElaineHSnh.jpg"
  "clr_Eyes","RMElaineEyeBrn.jpg"
  "clrMouth","RMElaineTf.jpg"
  "bmpMouth","RMElaineTfB.jpg"
  "clr_Lash","RMElaineLshFul.png"
  """
  """ keep in mind some image entries may be blank, hence this init of strImage """
  strImage = ""
  image_path = stringPath
  image_dir = os.path.dirname(image_path)
  img_list = os.path.join(image_dir, 'image_list.csv')
  try:
    with open(img_list) as file:
      pass
  except IOError as e:
    strImage = "NIMGLIST"

  if not strImage == "NIMGLIST":
    imagelist = readList(img_list)
    if not imagelist == "NOVALS":
      imagedict = dict(imagelist)
      try:
        strImage = imagedict.get(stringImg)
        strImage = cleanStr(strImage)
      except TypeError as e:
        strImage = ""
  return strImage

def imgListSave(lstSettings, iPath):
  """
  This will write from a list (lstSettings) to a file called image_list.csv in
  the folder named in pPath, creating the file if it does not already exist.
  As this is an action that is unlikely to generate errors, only pass SAVSUCC.
  """
  image_dir = iPath
  image_listpath = os.path.join(image_dir, 'image_list.csv')
  wrtFile = open(image_listpath, 'w')
  for item in lstSettings:
    wrtFile.write(item + "\n")
  return "SAVSUCC"

def updImgPath(self, context):
  #pass
  scn = bpy.context.scene
  sSelectedFigure = scn.objects[(scn.FS_FigureList)]
  for object in bpy.data.objects:
    object.select = False
  sSelectedFigure.select = True

def updFigure(self, context):
  scn = bpy.context.scene
  sSelectedFigure = scn.objects[(scn.FS_FigureList)]
  for object in bpy.data.objects:
    object.select = False
  sSelectedFigure.select = True

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



def getMessage(msgStr, retVal=None):
  sep = ('-')
  if retVal == "str":
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
  @classmethod
  def poll(cls, context):
    return True

  def invoke(self, context, event):
    cMsgS = self.message
    self.message = getMessage(cMsgS,"str")
    cMsgS = getMessage(cMsgS)
    self.mesglen = int(cMsgS)
    wm = context.window_manager
    return wm.invoke_popup(self, width=self.mesglen, height=400)

  def execute(self, context):
    self.report({'INFO'}, self.message)
    return {'FINISHED'}

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
  simgpath = StringProperty(
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
  flSssVal = FloatProperty(
    name="SSS Value",
    description="Increasing beyond .2, figure will glow a bit weird...",
    default=0.0800,
    )

  flSssRad = FloatProperty(
    name="SSS Radiate",
    description="Trying Radiant values...",
    default=0.1500,
    )

  flSpcAmt = FloatProperty(
    name="Spec Amount",
    description="Trying Specular amount values...",
    default=0.3200,
    )

  flSpcRuf = FloatProperty(
    name="Spec Roughness",
    description="Trying Specular roughness values...",
    default=0.260,
    )

  flSheenV = FloatProperty(
    name="Sheen Value",
    description="Trying Sheen values...",
    default=0.1600,
    )

  flIorVal = FloatProperty(
    name="IOR Value",
    description="Suggested skin IOR value is 1.85...",
    default=1.850,
    )

  sHeadClr = StringProperty(
    name="HeadColour",
    description="Choose face colour file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )
  sHeadBmp = StringProperty(
    name="HeadBump",
    description="Choose face bump file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )
  sHeadSpc = StringProperty(
    name="HeadSpecular",
    description="Choose face specular file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )

  sBodyClr = StringProperty(
    name="BodyColour",
    description="Choose torso colour file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )
  sBodyBmp = StringProperty(
    name="BodyBump",
    description="Choose torso bump file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )
  sBodySpc = StringProperty(
    name="BodySpecular",
    description="Choose torso specular file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )

  sLimbClr = StringProperty(
    name="LimbColour",
    description="Choose limb colour file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )
  sLimbBmp = StringProperty(
    name="LimbBump",
    description="Choose limb bump file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )
  sLimbSpc = StringProperty(
    name="LimbSpecular",
    description="Choose limb specular file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )

  sEyesClr = StringProperty(
    name="EyesColour",
    description="Choose iris colour file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )

  sOralClr = StringProperty(
    name="MouthColour",
    description="Choose inner mouth colour file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )

  sOralBmp = StringProperty(
    name="MouthBump",
    description="Choose inner mouth bump file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
    )

  sLashTrn = StringProperty(
    name="LashesTrans",
    description="Choose eyelash transparency file:",
    default="",
    maxlen=1024,
    subtype='FILE_PATH',
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
      row = box.row()
      row.label(text="Shader Settings")
      row = box.row()
      layout.row().separator()
      col = row.column()
      subrow = col.row()
      subrow.operator("object.load_presets", text='Load')
      subrow.operator("object.save_presets", text='Save')
      row = box.row()
      layout.row().separator()
      row = box.row()
      row.label(text="-1- Find image files: ")
      row = box.row()
      row.prop(sFgrTool, "simgpath", text="")
      row = box.row()
      row.label(text="-2- Select shader type: ")
      row = box.row()
      row.prop(sFgrTool,"shaderEnum",text='')
      row = box.row()
      row.label(text="-3- Figure to paint: ")
      row = box.row()
      row.prop(sFgrTool,"curFigEnum",text='')
      row = box.row()
      row.label(text="-4- Figure Type: ")
      row = box.row()
      row.prop(sFgrTool, "baseFigEnum", "")
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
      row = box.row()
      sub = box.row(align=True)
      sub.alignment = 'CENTER'
      sub.scale_y = 2.0
      sub.operator("object.run_script", text='Apply Shaders', icon='POSE_HLT')
      row = box.row()
    else:
      row = layout.row()
      row.label(text='No Object in Scene')


class ImageEditPanel(bpy.types.Panel):
  """User-associate image to material zone: Panel"""
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'TOOLS'
  bl_label = "Image Settings"
  bl_context = "objectmode"
  bl_idname = "MATERIALS_PT_images"
  bl_category = "FigureShader"

  def draw(self, context):
    layout = self.layout

    def mySplit():
      splitval = row.split(percentage=0.25)
      return splitval

    scene = bpy.context.scene
    sFgrTool = scene.figTools

    if context.object:
      box = layout.box()
      col = box.column(align=True)
      col.separator()
      row = col.row()
      split = mySplit()
      col_left = split.column()
      col_right = split.column()
      col_left.label(text="Head-Clr")
      col_right.prop(sFgrTool, "sHeadClr", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Head-Bmp")
      col_right.prop(sFgrTool, "sHeadBmp", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Head-Spc")
      col_right.prop(sFgrTool, "sHeadSpc", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Body-Clr")
      col_right.prop(sFgrTool, "sBodyClr", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Body-Bmp")
      col_right.prop(sFgrTool, "sBodyBmp", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Body-Spc")
      col_right.prop(sFgrTool, "sBodySpc", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Limb-Clr")
      col_right.prop(sFgrTool, "sLimbClr", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Limb-Bmp")
      col_right.prop(sFgrTool, "sLimbBmp", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Limb-Spc")
      col_right.prop(sFgrTool, "sLimbSpc", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Eyes-Clr")
      col_right.prop(sFgrTool, "sEyesClr", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Mouth-Clr")
      col_right.prop(sFgrTool, "sOralClr", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Mouth-Bmp")
      col_right.prop(sFgrTool, "sOralBmp", text="")
      row = col.row()
      split = mySplit()
      col_left.label(text="Lashes-Trn")
      col_right.prop(sFgrTool, "sLashTrn", text="")
      row = col.row()
      box = layout.box()
      row = box.row()
      row.label(text="Image files location: ")
      row = box.row()
      row.prop(sFgrTool, "simgpath", text="")
      row = box.row()
      col = row.column()
      subrow = col.row()
      subrow.operator("object.clear_field", text='Clear')
      subrow.operator("object.load_images", text='Load')
      subrow.operator("object.save_images", text='Save')
      row = box.row()


class ClearFields(bpy.types.Operator):
  bl_idname = "object.clear_field"
  bl_label = "Clears Image Fields"
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
    fTools = bpy.context.scene.figTools
    absImgPath = bpy.path.abspath(fTools.simgpath)
    self.clearImgPanel()
    return {'FINISHED'}

  def clearImgPanel(self):
    fTools = bpy.context.scene.figTools
    fTools.sHeadClr = ""
    fTools.sHeadBmp = ""
    fTools.sHeadSpc = ""
    fTools.sBodyClr = ""
    fTools.sBodyBmp = ""
    fTools.sBodySpc = ""
    fTools.sLimbClr = ""
    fTools.sLimbBmp = ""
    fTools.sLimbSpc = ""
    fTools.sEyesClr = ""
    fTools.sOralClr = ""
    fTools.sOralBmp = ""
    fTools.sLashTrn = ""

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
    fTools = bpy.context.scene.figTools
    absImgPath = bpy.path.abspath(fTools.simgpath)
    try:
      xChk = parmDictGet('img_path')
    except:
      xChk = "NOPARMS"

    if xChk == 'NOPARMS':
      sErrorMsg = showErrMsg(xChk)
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
    elif xChk == 'WHEREIS':
      sErrorMsg = showErrMsg(xChk)
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
    else:
      """ Really clumsy, but it works """
      fTools.simgpath = cleanStr(parmDictGet('img_path'))
      fTools.flSssVal = float(parmDictGet('fl01_sssval'))
      fTools.flSssRad = float(parmDictGet('fl02_sssrad'))
      fTools.flSpcAmt = float(parmDictGet('fl05_spcamt'))
      fTools.flSpcRuf = float(parmDictGet('fl06_spcruf'))
      fTools.flSheenV = float(parmDictGet('fl11_sheenv'))
      fTools.flIorVal = float(parmDictGet('fl14_iorval'))
      sErrorMsg = showErrMsg("LODSUCC")
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )

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
    fTools = bpy.context.scene.figTools
    """ chkPathRltv returns .T. if path is relative """
    if chkPathRltv(fTools.simgpath):
      sErrorMsg = showErrMsg("RLTVPATH")
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
      return {'CANCELLED'}
    else:
      blend_path = bpy.context.blend_data.filepath
      blend_dir = os.path.dirname(blend_path)
      absImgPath = bpy.path.abspath(fTools.simgpath)
      wrtfile = []
      simgp = '"' + absImgPath + '"'
      ssval = '"' + format(fTools.flSssVal,'f') + '"'
      ssrad = '"' + format(fTools.flSssRad,'f') + '"'
      ssamt = '"' + format(fTools.flSpcAmt,'f') + '"'
      ssruf = '"' + format(fTools.flSpcRuf,'f') + '"'
      ssshe = '"' + format(fTools.flSheenV,'f') + '"'
      ssior = '"' + format(fTools.flIorVal,'f') + '"'
      wrtfile.append('"img_path", ' + simgp)
      wrtfile.append('"fl01_sssval", ' + ssval)
      wrtfile.append('"fl02_sssrad", ' + ssrad)
      wrtfile.append('"fl05_spcamt", ' + ssamt)
      wrtfile.append('"fl06_spcruf", ' + ssruf)
      wrtfile.append('"fl11_sheenv", ' + ssshe)
      wrtfile.append('"fl14_iorval", ' + ssior)
      xChk = parmListSave(wrtfile, blend_dir)
      sErrorMsg = showErrMsg(xChk)
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
      return {'FINISHED'}

class LoadImages(bpy.types.Operator):
  bl_idname = "object.load_images"
  bl_label = "Loads image names from CSV"
  @classmethod
  def poll(cls, context):
    def allCondsMet():
      bAllMet = False
      if bpy.path.basename(bpy.context.blend_data.filepath):
        xPath = bpy.path.basename(bpy.context.blend_data.filepath)
        bAllMet = True
      return bAllMet
    return allCondsMet()

  def clearImgPanel(self):
    fTools = bpy.context.scene.figTools
    fTools.sHeadBmp = ""
    fTools.sHeadSpc = ""
    fTools.sBodyClr = ""
    fTools.sBodyBmp = ""
    fTools.sBodySpc = ""
    fTools.sLimbClr = ""
    fTools.sLimbBmp = ""
    fTools.sLimbSpc = ""
    fTools.sEyesClr = ""
    fTools.sOralClr = ""
    fTools.sOralBmp = ""
    fTools.sLashTrn = ""

  def getBaseNames(self):
    fTools = bpy.context.scene.figTools
    absImgPath = bpy.path.abspath(fTools.simgpath)
    fTools.sHeadClr = cleanStr(imgDictGet('clr_Face', absImgPath))
    fTools.sHeadBmp = cleanStr(imgDictGet('bmp_Face', absImgPath))
    fTools.sHeadSpc = cleanStr(imgDictGet('spc_Face', absImgPath))
    fTools.sBodyClr = cleanStr(imgDictGet('clr_Body', absImgPath))
    fTools.sBodyBmp = cleanStr(imgDictGet('bmp_Body', absImgPath))
    fTools.sBodySpc = cleanStr(imgDictGet('spc_Body', absImgPath))
    fTools.sLimbClr = cleanStr(imgDictGet('clrALimb', absImgPath))
    fTools.sLimbBmp = cleanStr(imgDictGet('bmpALimb', absImgPath))
    fTools.sLimbSpc = cleanStr(imgDictGet('spcALimb', absImgPath))
    fTools.sEyesClr = cleanStr(imgDictGet('clr_Eyes', absImgPath))
    fTools.sOralClr = cleanStr(imgDictGet('clrMouth', absImgPath))
    fTools.sOralBmp = cleanStr(imgDictGet('bmpMouth', absImgPath))
    fTools.sLashTrn = cleanStr(imgDictGet('clr_Lash', absImgPath))

  def addPath2Name(self):
    fTools = bpy.context.scene.figTools
    absImgPath = bpy.path.abspath(fTools.simgpath)
    fTools.sHeadClr = absImgPath + fTools.sHeadClr if fTools.sHeadClr else ""
    fTools.sHeadBmp = absImgPath + fTools.sHeadBmp if fTools.sHeadBmp else ""
    fTools.sHeadSpc = absImgPath + fTools.sHeadSpc if fTools.sHeadSpc else ""
    fTools.sBodyClr = absImgPath + fTools.sBodyClr if fTools.sBodyClr else ""
    fTools.sBodyBmp = absImgPath + fTools.sBodyBmp if fTools.sBodyBmp else ""
    fTools.sBodySpc = absImgPath + fTools.sBodySpc if fTools.sBodySpc else ""
    fTools.sLimbClr = absImgPath + fTools.sLimbClr if fTools.sLimbClr else ""
    fTools.sLimbBmp = absImgPath + fTools.sLimbBmp if fTools.sLimbBmp else ""
    fTools.sLimbSpc = absImgPath + fTools.sLimbSpc if fTools.sLimbSpc else ""
    fTools.sEyesClr = absImgPath + fTools.sEyesClr if fTools.sEyesClr else ""
    fTools.sOralClr = absImgPath + fTools.sOralClr if fTools.sOralClr else ""
    fTools.sOralBmp = absImgPath + fTools.sOralBmp if fTools.sOralBmp else ""
    fTools.sLashTrn = absImgPath + fTools.sLashTrn if fTools.sLashTrn else ""

  def execute(self, context):
    #print ("Trying to load image names...")
    items = []
    xErr = "FILEEXISTS"
    fTools = bpy.context.scene.figTools
    absImgPath = bpy.path.abspath(fTools.simgpath)
    """
    1) Check image path is not as relative path format
    [    Scripts tend to have dramas with paths that are not absolute. ]
    """
    if chkPathRltv(fTools.simgpath):
      sErrorMsg = showErrMsg("RLTVPATH")
      bpy.ops.system.message('INVOKE_DEFAULT',
        type = "Error",
        message = sErrorMsg,
        )
      return {'CANCELLED'}

    else:
      """
      2) Check for existence of parm_list.csv.
      [    parmDictGet returns NOPARMS if parm_list.csv doesn't exist ]
      """
      try:
        xErr = parmDictGet('img_path')
      except ValueError as e:
        xErr = "NOPARMS"
      if xErr == 'NOPARMS':
        sErrorMsg = showErrMsg(xErr)
        bpy.ops.system.message('INVOKE_DEFAULT',
          type = "Error",
          message = sErrorMsg,
          )
        return {'CANCELLED'}

      else:
        """
        3) Check for existence of image_list.csv.
        [    xErr now holds the fully-qualified path name to the images
        """
        #print ("currently xErr is: " + xErr)
        try:
          xErr = imgDictGet('clr_Face', xErr)
        except:
          xErr = "NIMGLIST"
        #print ("currently xErr is: " + xErr)
        if xErr == 'NIMGLIST':
          sErrorMsg = showErrMsg(xErr)
          bpy.ops.system.message('INVOKE_DEFAULT',
            type = "Error",
            message = sErrorMsg,
            )
          return {'CANCELLED'}

        else:
          """
          4) Conditions all met, load images.
          """
          self.clearImgPanel()
          self.getBaseNames()
          sErrorMsg = showErrMsg("LODSUCC")
          bpy.ops.system.message('INVOKE_DEFAULT',
            type = "Error",
            message = sErrorMsg,
            )
          return {'FINISHED'}

class SaveImages(bpy.types.Operator):
  bl_idname = "object.save_images"
  bl_label = "Saves Image Names to CSV"
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
    fTools = bpy.context.scene.figTools
    imagePath = bpy.path.abspath(fTools.simgpath)
    getBN = bpy.path
    wrtfile = []
    hdc = '"' + getBN.basename(fTools.sHeadClr) + '"'
    hdb = '"' + getBN.basename(fTools.sHeadBmp) + '"'
    hds = '"' + getBN.basename(fTools.sHeadSpc) + '"'
    byc = '"' + getBN.basename(fTools.sBodyClr) + '"'
    byb = '"' + getBN.basename(fTools.sBodyBmp) + '"'
    bys = '"' + getBN.basename(fTools.sBodySpc) + '"'
    lbc = '"' + getBN.basename(fTools.sLimbClr) + '"'
    lbb = '"' + getBN.basename(fTools.sLimbBmp) + '"'
    lbs = '"' + getBN.basename(fTools.sLimbSpc) + '"'
    eye = '"' + getBN.basename(fTools.sEyesClr) + '"'
    olc = '"' + getBN.basename(fTools.sOralClr) + '"'
    olb = '"' + getBN.basename(fTools.sOralBmp) + '"'
    trn = '"' + getBN.basename(fTools.sLashTrn) + '"'
    wrtfile.append('"clrALimb", ' + lbc)
    wrtfile.append('"clrLLimb", ' + lbc)
    wrtfile.append('"bmpALimb", ' + lbb)
    wrtfile.append('"bmpLLimb", ' + lbb)
    wrtfile.append('"spcALimb", ' + lbs)
    wrtfile.append('"spcLLimb", ' + lbs)
    wrtfile.append('"clr_Body", ' + byc)
    wrtfile.append('"bmp_Body", ' + byb)
    wrtfile.append('"spc_Body", ' + bys)
    wrtfile.append('"clr_Face", ' + hdc)
    wrtfile.append('"bmp_Face", ' + hdb)
    wrtfile.append('"spc_Face", ' + hds)
    wrtfile.append('"clr_Eyes", ' + eye)
    wrtfile.append('"clrMouth", ' + olc)
    wrtfile.append('"bmpMouth", ' + olb)
    wrtfile.append('"clr_Lash", ' + trn)
    xErr = imgListSave(wrtfile, imagePath)
    sErrorMsg = showErrMsg(xErr)
    bpy.ops.system.message('INVOKE_DEFAULT',
      type = "Error",
      message = sErrorMsg,
      )
    return {'FINISHED'}



class RunScript(bpy.types.Operator):
  """ Conditionally runs Make Shaders """
  bl_idname = "object.run_script"
  bl_label = "Invokes Shader Script"

  """
  =============================================================================
   bpy.path.basename() returns the name of the currently active .blend. If un-
   named, returns False. Button does not activate until file is saved with a name.
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
    if checkedSettings():
      shadersSetup()
    return {'FINISHED'}

def checkedSettings():
  """ just a stub at this point """
  parmsReady = True
  return parmsReady

def shadersSetup():
  sMissingFile = ""
  blend_name = ""
  scene = bpy.context.scene
  fTools = scene.figTools
  strImgPath = bpy.path.abspath(fTools.simgpath)
  sSelShader = fTools.shaderEnum
  sBaseFgr = fTools.baseFigEnum
  sSelFgr =  fTools.curFigEnum




  def paintShaders():
    """
    =============================================================
    These are defined in figure_defs.py. Cuurently defined for:
    V4, Dawn, Mariko, Antonia
    The var Figure is defined in Check4Files, just before
    paintShaders() is invoked.
    ========================================================
    """
    dict_mats = matZones(sBaseFgr)

    """
    =============================================================
    Truncates strings like 3_SkinLeg:1 to 3_SkinLeg by detecting
    an extra chars in name, trapping curently for   . and :
    ========================================================
    """
    def getMatName(mtlName):
      sep = 'NF'
      """ Blender has added a .001 or .002 """
      if '.' in mtlName:
        sep = ('.')
      if ':' in mtlName:
        sep = (':')
      """ truncate only if a . or : is found """
      if not sep == 'NF':
        mtlName = mtlName.split(sep, 1)[0]
      """ get the actual material type from the material dictionary """
      mtlType = dict_mats.figMat.get(mtlName)

      if mtlType is None:
        return sep
      else:
        return mtlType

    if bpy.context.scene.render.engine == 'BLENDER_RENDER':
      bpy.context.scene.render.engine = 'CYCLES'

    clrALimb = fTools.sLimbClr
    clrLLimb = fTools.sLimbClr
    bmpALimb = fTools.sLimbBmp
    bmpLLimb = fTools.sLimbBmp
    spcALimb = fTools.sLimbSpc
    spcLLimb = fTools.sLimbClr
    clr_Body = fTools.sBodyClr
    bmp_Body = fTools.sBodyBmp
    spc_Body = fTools.sBodySpc
    clr_Face = fTools.sHeadClr
    bmp_Face = fTools.sHeadBmp
    spc_Face = fTools.sHeadSpc
    clr_Eyes = fTools.sEyesClr
    clrMouth = fTools.sOralClr
    bmpMouth = fTools.sOralBmp
    clr_Lash = fTools.sLashTrn

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

    """ make the current figure active """
    bpy.context.scene.objects.active = bpy.data.objects[sSelFgr]
    curr_obj = bpy.data.objects[sSelFgr]
    bpy.context.object.active_material_index = 0
    all_slots = bpy.context.object.material_slots

    """ iterate through the material slots... """
    for i in range(len(all_slots)):
      img_Clr = None
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
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        """ Added 11-10-2016: checks for valid material name """
        matType = getMatName(matName)
        if not matType == "NF":
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
          if img_Clr is not None:
            if len(img_Clr) > 0:
              if sSelShader == "PrinSSS":
                img_Clr = fTools.simgpath + img_Clr
                img_Clr = bpy.data.images.load(filepath=img_Clr)
                """
                Sending:      figure(obj)--shadertype-material-clrImage--bumpmap--specmap
                                  (last two can be None)
                Eventually, this will be called parameterless.
                """
                new_mat = buildShader(curr_obj, sSelShader, matType, img_Clr, dblBump, dblSpec)
              else:
                sErrorMsg = showErrMsg("INVLSHAD")
                bpy.ops.system.message('INVOKE_DEFAULT',
                  type = "Error",
                  message = sErrorMsg,
                  )
      else:
        sErrorMsg = showErrMsg("INVLDMAT")
        bpy.ops.system.message('INVOKE_DEFAULT',
          type = "Error",
          message = sErrorMsg,
          )


  def check4Files():
    """
    ===========================================================================
    >>>>    Error handling    <<<<
    ===========================================================================
    -- blend_name: name-only of the currently open .blend file
    -- blend_dir: fully-qualified path to [blend_name] - 'parm_list.csv'
    -- blend_path: fully-qualified path with [blend_name]
    """
    sRet = "FILEEXISTS"
    blend_name = bpy.path.basename(bpy.context.blend_data.filepath)
    blend_path = bpy.context.blend_data.filepath
    blend_dir = os.path.dirname(blend_path)

    """
    readlist() attempts to create list from csv file, if this fails, exit
    process with False, which the if() then returns a msg. First, check
    for parm_list.csv.
    """
    try:
      csv_listpath = os.path.join(blend_dir, "parm_list.csv")
      with open(csv_listpath) as file:
        pass
    except IOError as e:
      sRet = "NOPARMS"

    if sRet == "FILEEXISTS":
      csv_listpath = os.path.join(blend_dir, "parm_list.csv")
      csv_list = readList(csv_listpath)
      pathlist = dict(csv_list)
      strImgPath = pathlist.get('img_path')
      strImgPath = cleanStr(strImgPath)
      if len(strImgPath) == 0:
        sRet = "WHEREIS"

      if sRet == "FILEEXISTS":
        imag_dir = os.path.dirname(strImgPath)
        img_list = os.path.join(imag_dir, "image_list.csv")
        try:
          with open(img_list) as file:
            pass
        except IOError as e:
          sRet = "NIMGLIST"

        if sRet == "FILEEXISTS":
          """step through image_list.csv, check for invalid file references"""
          imgFile = ""
          pathFile = ""
          retImgName = ""
          pic_list = readList(img_list)
          nVal = len(pic_list)
          nInt = 0
          try:
            imgDict = dict(pic_list)
          except:
            sRet = "BADDICT"

          if sRet == "FILEEXISTS":
            for attr, val in imgDict.items():
              val = imgDict.get(attr, val)
              imgFile = cleanStr(val)
              if len(imgFile) < 1:
                pass
              else:
                pathFile = os.path.join(imag_dir, imgFile)
                try:
                  with open(pathFile) as file:
                    pass
                except IOError as e:
                  sRet = val
    return sRet


  """
  ==============================================================================
  Iterate through the objects in the scene, run paintShader only for FILEEXISTS
  ==============================================================================
  """
  scn = bpy.context.scene
  siniMsg = check4Files()
  sErrorMsg = ""
  if siniMsg == "FILEEXISTS":
    for obj in scn.objects:
      if obj.type == 'MESH':
        """ FINALLY: run the script!!! """
        oName = obj.name
        if oName == sSelFgr:
          obj.select = True
          paintShaders()
          obj.select = False
  else:
    sErrorMsg = showErrMsg(siniMsg)
    bpy.ops.system.message('INVOKE_DEFAULT',
      type = "Error",
      message = sErrorMsg,
      )


def register():
  """ Note2Self: first in, best dressed -> last out """
  bpy.utils.register_module(__name__)
  bpy.types.Scene.figTools = PointerProperty(
    name="fgrPanelTools",
    description="figTools",
    type=PanelTools)

def unregister():
  del bpy.types.Scene.figTools
  bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
  register()
