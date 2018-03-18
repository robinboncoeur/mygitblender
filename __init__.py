# ---------------------------------------------------------------------
# File: __init__.py (for figure_shaders)
# ---------------------------------------------------------------------
# Copyright (c) 16-Nov-2015, Robyn Hahn
# Revision: 24-Feb-2018
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
  "version": (0, 5, 4),
  "blender": (2, 79, 0),
  "location": "View3D",
  "description": "Generates simple Cycles shaders for imported OBJ Figures",
  "warning": "Select Figure by name, then associate Figure type ...",
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
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from bpy.props import (StringProperty,
                       EnumProperty,
                       PointerProperty,
                       )

sMsg = ""
thisOS_name = os.name


def updateFigList(self, context):
  """ enum property callback:
  expects a tuple containing (identifier, name, description) """
  allItems = [("NoID", "NoName","NoDesc")]
  if len(bpy.context.scene.objects) != 0:
    allItems = []
    for items in bpy.context.scene.objects:
      allItems.append((items.name,items.name,items.name))

  return allItems

def SelectFigure(self, context):
  scn = bpy.context.scene
  sSelectedFigure = scn.objects[(scn.FS_FigureList)]
  for object in bpy.data.objects:
    object.select = False
  sSelectedFigure.select = True
  print ("Selected obj is: ", sSelectedFigure.name)


class MessageOperator(bpy.types.Operator):
  bl_idname = "error.message"
  bl_label = "Message"
  type = StringProperty()
  message = StringProperty()

  def execute(self, context):
    self.report({'INFO'}, self.message)
    print(self.message)
    return {'FINISHED'}

  def invoke(self, context, event):
    wm = context.window_manager
    return wm.invoke_popup(self, width=300, height=400)

  def draw(self, context):
    self.layout.label("FYI:")
    row = self.layout.split(0.15)
    layout = self.layout
    row = layout.row()
    row.label(text="Error: ")
    row = layout.row()
    row.label(text=self.message)
    #row.prop(self, "message")
    row = layout.row()
    row = self.layout.split(0.85)
    #row.label("")
    row.operator("error.ok")

#   The OK button in the error dialog
class OkOperator(bpy.types.Operator):
  bl_idname = "error.ok"
  bl_label = "OK"
  def execute(self, context):
    return {'FINISHED'}


class panelTools(PropertyGroup):
  sBaseFgr = StringProperty(
    name="Figure Base",
    description="which core figure the mesh is based on",
  )

  sSelFgr = StringProperty(
    name="Selected Figure",
    description="figure currently selected",
  )

  baseFigEnum = EnumProperty(
      name="FigureType:",
      description="Choose base figure name.",
      items=[ ("V4", "Victoria4", ""),
              ("Mariko","Mariko",""),
              ("Dawn","Dawn",""),
              ("Antonia","Antonia",""),
             ]
      )

  curFigEnum = EnumProperty(
      name="FigureList:",
      description="Choose figure for shaders.",
      items=updateFigList,
      update=SelectFigure,
      default=None
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
      row = layout.row()
      row.label(text="Select the figure for SkinShaders: ")
      row = layout.row()
      #row.prop(scene,"FS_FigureList",text='')
      row.prop(sFgrTool,"curFigEnum",text='')
      row = layout.row()
      row.label(text="Select the Figure Type: ")
      row = layout.row()
      row.prop(sFgrTool, "baseFigEnum", "name")
      row = layout.row()
      row.operator("object.run_script", text='Apply Shaders')
    else:
      row = layout.row()
      row.label(text='No Object in Scene')


class runScript(bpy.types.Operator):
  """ Conditionally runs Make Shaders """
  bl_idname = "object.run_script"
  bl_label = "Invokes Shader Script"

  """
  ================================================
   bpy.path.basename() returns the name of the
   currently active .blend.
   If un-named, returns .F. and so button does
   not activate until file is saved with a name.
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
    sBaseFgr = bpy.context.scene.figTools.baseFigEnum
    sSelFgr =  bpy.context.scene.figTools.curFigEnum
    #print("Current figure is: " + sBaseFgr)
    #print("Current object is: " + sSelFgr)
    shadersSetup(sBaseFgr, sSelFgr)
    return {'FINISHED'}


def shadersSetup(BaseFigure, SelectFigure):
  sMissingFile = ""
  blend_name = ""
  cBaseFig = BaseFigure
  cSeltFig = SelectFigure

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

  def readList(fname):
    rval = []
    with open(fname, 'r') as csvfile:
      r = csv.reader(csvfile, delimiter=',')
      for row in r:
        if not len(row) == 0:
          rval.append(row)
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
      print(mtlType)

      if mtlType is None:
        return sep
      else:
        return mtlType

    if bpy.context.scene.render.engine == 'BLENDER_RENDER':
      bpy.context.scene.render.engine = 'CYCLES'

    blend_path = bpy.data.filepath
    blend_dir = os.path.dirname(blend_path)
    csv_listpath = os.path.join(blend_dir, 'path_list.csv')

    # currently has 3 entries: list those, weed out empties
    csv_list = readList(csv_listpath)
    pathlist = dict(csv_list)

    # gets the path to the images
    if thisOS_name == 'posix':
      path_str = pathlist.get('img_pathP')
    if thisOS_name == 'nt':
      path_str = pathlist.get('img_pathN')
    path_str = cleanStr(path_str)
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
      print ("identified the figure... " + cSeltFig)
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
        print ("matName = " + matName)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        """ Added 11-10-2016: checks for valid material name """
        matType = getMatName(matName)
        print ("matType = " + matType)
        if not matType == "NF":
          print ("matType = " + matType)
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
          """ Sending:      figure (obj), material, colour, bump map, spec map
                            (last two can be None)"""
          new_mat = buildShader(curr_obj, matType, ImgColr, dblBump, dblSpec)
      else:
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
      # print("csv_listpath is: " + csv_listpath)
      csv_list = readList(csv_listpath)
      pathlist = dict(csv_list)
      if thisOS_name == 'posix':
          print("A-thisOS_Name is: " + thisOS_name)
          path_str = pathlist.get('img_pathP')
      if thisOS_name == 'nt':
          path_str = pathlist.get('img_pathN')
          print("B-thisOS_Name is: " + thisOS_name)
      path_str = cleanStr(path_str)
      print("Cleaned path string: " + path_str)
      imag_dir = os.path.dirname(path_str)
      # print("The os path is: " + imag_dir)
      img_list = os.path.join(imag_dir, "image_list.csv")
      # print("The whole path is: " + img_list)
      try:
        with open(img_list) as file:
          pass
      except IOError as e:
        print("could not open: " + img_list)
        sRet = "IMGLIST"

      if sRet == "FILEEXISTS":
        # step through the image_list.csv to check for invalid file references
        imgFile = ""
        pathFile = ""
        retImgName = ""
        pic_list = readList(img_list)
        nVal = len(pic_list)
        nInt = 0
        imgDict = dict(pic_list)
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

  def showErrMsg(sMsg):
    if sMsg == "PATH":
      longMsg = "Missing path_list.csv. "+"\r\n"
      longMsg += "Copy this file to the folder "+"\r"
      longMsg += "containing your .blend and edit it."
    if sMsg == "IMGLIST":
      longMsg = "Your path_list.csv points to a folder missing the image_list.csv file."
    if sMsg == "IMAGE":
      longMsg = "image_list.csv points to a missing image file."
    if len(sMsg) < 1:
      longMsg = "Another problem occurred."
    if len(sMsg) > 9:
      longMsg = sMsg + " is missing, or the file is spelled wrong in image_list.csv..."

    return longMsg

  """
  ==============================================================================
  Iterate through the objects in the scene, run paintShader only for FILEEXISTS
  ==============================================================================
  """
  scn = bpy.context.scene
  #figName = bpy.context.scene.objects.active.name

  sMsg = check4Files()
  sErrorMsg = ""
  longMsg = ""
  if sMsg == "FILEEXISTS":
    for obj in scn.objects:
      if obj.type == 'MESH':
        # FINALLY: run the script!!!
        oName = obj.name
        print("The current figure name is: " + oName)
        if oName == cSeltFig:
          print("oName = " + cSeltFig)
          obj.select = True
          paintShaders()
          #obj.name = oName
          obj.select = False
  else:
    sErrorMsg = showErrMsg(sMsg)
    bpy.ops.error.message('INVOKE_DEFAULT',
      type = "Error",
      message = sErrorMsg,
      )
  #print ("The error is: " + sErrorMsg)
  #return



# Note2Self: first in, best dressed -> last out
def register():
  bpy.utils.register_module(__name__)
  bpy.types.Scene.figTools = PointerProperty(type=panelTools)

def unregister():
  del bpy.types.Scene.figTools
  bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
  register()
