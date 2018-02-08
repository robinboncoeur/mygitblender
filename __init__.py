# ---------------------------------------------------------------------
# File: __init__.py (for figure_shaders)
# ---------------------------------------------------------------------
#
# Copyright (c) 16-Nov-2015, Robyn Hahn
# Revision: 26-Jun-2017
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Shaders for Imported Figures",
    "author": "Robyn Hahn",
    "version": (0, 5, 0),
    "blender": (2, 79, 0),
    "location": "View3D",
    "description": "Generates simple Cycles shaders for imported OBJ Figures",
    "warning": "Adding support for Antonia ...",
    "wiki_url": "",
    "category": "Material"}


if "bpy" in locals():
    import imp

    imp.reload(figure_defs)
    imp.reload(make_shader)
    # print("Reloaded multiple files")
else:
    from . import figure_defs
    from . import make_shader
    # print("Imported multiple files")
# NOTE: ===> make_shaders before . is the folder
#            make_shaders after . is the file
#            so, from folder_name.file_name import... etc
from make_shaders.make_shader import buildShader
from make_shaders.figure_defs import matZones
import csv
import sys
import os
import bpy
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,)
from bpy.props import (StringProperty,
                       EnumProperty,)

# Developer tools - comment out on GoLive
"""
import code
namespace = globals().copy()
namespace.update(locals())
code.interact(local=namespace)
"""

thisOS_name = os.name
sMsg = ""

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

        if context.object:
            obj = context.object

            #row = layout.row()
            #row.label(text='Select your figure:')

            row = layout.row()
            row.label(text="Active object is: ")
            row = layout.row()
            row.label(obj.name)
            row = layout.row()
            # dropdown will go here
            row.prop(obj, "name")
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
    This is still not fully functional. Ideally, it
    would check if (appears in order of priority):
      1) context.active_object is not None
      2) context.active_object is a Poser figure
      3) context.active_object has the correct name
    ================================================
     the bpy.path.basename() returns the name of the currently active .blend, if un-named,
     return .F. - button does not activate until file is saved with a name
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
        shadersSetup()
        return {'FINISHED'}


def shadersSetup():
    print ("Starting shadersSetup function...")
    sMissingFile = ""
    blend_name = ""
    """ ================================================================
         Returns the name of the figure if it matches the short list.
         Will need to develop a more flexible, dict-based solution.
         This is admittedly an awkward and poorly-scalable approach.
        ============================================================="""
    def getFigName(sName):
        bFound = False
        if sName.startswith('V4'):
            sName = sName[:2]
            bFound = True
        if sName.startswith('Mariko'):
            sName = sName[:6]
            bFound = True
        if  sName.startswith('Dawn'):
            sName = sName[:4]
            bFound = True
        if  sName.startswith('Antonia'):
            sName = sName[:7]
            print ("Shaders Setup for Antonia...")
            bFound = True
        if not bFound:
            sName = 'NF'
        return sName


    def readList(fname):
        rval = []
        with open(fname, 'r') as csvfile:
            r = csv.reader(csvfile, delimiter=',')
            for row in r:
                if not len(row) == 0:
                    rval.append(row)
        return rval


    def cleanStr(sStr):
        # print("CleanStr()...pre-cleaning, sStr is: " + sStr)
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
        """ =============================================================
            These are defined in figure_defs.py. Cuurently defined for:
             V4
             Dawn
             Mariko
             and now, Antonia
            ========================================================"""
        dict_mats = matZones(figure)

        """ =============================================================
            Truncates strings like 3_SkinLeg:1 to 3_SkinLeg by detecting
            an extra chars in name, trapping curently for   . and :
            ========================================================"""
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

        # get the path to the images
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
        bpy.context.scene.objects.active = bpy.data.objects[figure]
        curr_obj = bpy.data.objects[figure]
        bpy.context.object.active_material_index = 0
        all_slots = bpy.context.object.material_slots

        # iterate through the material slots...
        for i in range(len(all_slots)):
            print ("identified the figure... " + figure)
            #img_Bmp = None
            img_Clr = None
            #img_Spc = None

            # Passed parms
            ImgColr = None
            dblBump = 0.00
            dblSpec = 0.00

            bpy.context.object.active_material_index = i

            """ On occasion empty material slots are created during import from Poser.
            These empty slots will be ignored. """
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
                        #ImgBump == None
                        if matType[5:] == 'Lash':
                            img_Clr = clr_Lash
                        if matType[5:] == 'Clr':
                            img_Clr = clr_Eyes
                        if matType[5:] == 'Trn':
                            img_Clr = None

                    if matType[0:4] == 'Skin':
                        if matType[5:] == 'Body':
                            img_Clr = clr_Body
                            #if not bmp_Body == None:
                            #    img_Bmp = bmp_Body
                            #if not spc_Body == None:
                            #    img_Spc = spc_Body
                        if matType[5:] == 'Face':
                            img_Clr = clr_Face
                            #if not bmp_Face == None:
                            #    img_Bmp = bmp_Face
                            #if not spc_Face == None:
                            #    img_Spc = spc_Face
                        if matType[5:] == 'Arms' or matType[5:] == 'Legs':
                            if clrALimb == clrLLimb:
                                img_Clr = clrALimb
                                #if not bmpALimb == None:
                                #    img_Bmp = bmpALimb
                                #if not spcALimb == None:
                                #    img_Spc = spcALimb
                            else:
                                if matType[5:] == 'Arms':
                                    img_Clr = clrALimb
                                    #if not bmpALimb == None:
                                    #    img_Bmp = bmpALimb
                                    #if not spcALimb == None:
                                    #    img_Spc = spcALimb
                                else:
                                    img_Clr = clrLLimb
                                    #if not bmpLLimb == None:
                                    #    img_Bmp = bmpLLimb
                                    #if not spcALimb == None:
                                    #    img_Spc = spcLLimb
                    if matType == 'Mouth':
                        img_Clr = clrMouth
                        #if not bmpMouth == None:
                        #    img_Bmp = bmpMouth
                    # fully qualified path added
                    if img_Clr is not None:
                        ImgColr = path_str + img_Clr
                        ImgColr = bpy.data.images.load(filepath=ImgColr)
                    #if img_Bmp is not None:
                    #    ImgBump = path_str + img_Bmp
                    #    ImgBump = bpy.data.images.load(filepath=ImgBump)
                    #if img_Spc is not None:
                    #    ImgSpec = path_str + img_Spc
                    #    ImgSpec = bpy.data.images.load(filepath=ImgSpec)
                    """ Sending:      figure (obj), material, colour, bump map, spec map
                                      (last two can be None)"""
                    new_mat = buildShader(curr_obj, matType, ImgColr, dblBump, dblSpec)
                else:
                  print ("Unable to assign shaders at this time.")


    """ =====================================================================================
        Error handling: [1] missing csv files
        ..............: [2] missing image files (incl incorrect spelling of file)
        ==================================================================================
    -- blend_name: name-only of the currently open .blend file
    -- blend_dir: fully-qualified path to [blend_name] - 'path_list.csv' lives here
    -- blend_path: fully-qualified path with [blend_name]                                      """
    def check4Files():
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
                # print("A-thisOS_Name is: " + thisOS_name)
                path_str = pathlist.get('img_pathP')
            if thisOS_name == 'nt':
                path_str = pathlist.get('img_pathN')
                # print("B-thisOS_Name is: " + thisOS_name)
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
                # print("Positive: " + sRet)
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


    """ =====================================================================================
         Iterate through the objects in the scene, run paintShader only for valid objects
        ================================================================================== """
    sScen = bpy.context.scene
    figName = bpy.context.scene.objects.active.name

    sMsg = check4Files()
    longMsg = ""
    if sMsg == "FILEEXISTS":
        for obj in sScen.objects:
            if obj.type == 'MESH':
                #figName = bpy.context.scene.objects.active.name
                oName = obj.name
                newName = getFigName(oName)
                if newName == 'NF':
                    obj.select = False
                else:
                    obj.select = True
                    obj.name = newName
                    figure = newName
                    paintShaders()
                    obj.name = oName
                    obj.select = False
    else:
        # print(sMsg)
        if sMsg == "PATH":
            longMsg = "Missing path_list.csv. Copy this file to the folder containing your .blend and edit it."
        if sMsg == "IMGLIST":
            longMsg = "Your path_list.csv points to a folder missing the image_list.csv file."
        if sMsg == "IMAGE":
            longMsg = "image_list.csv points to a missing image file."
        if len(sMsg) < 1:
            longMsg = "Another problem occurred."
        if len(sMsg) > 9:
            longMsg = sMsg + " is missing, or the file is spelled wrong in image_list.csv..."
        print(longMsg)




# Note2Self: first in, best dressed -> last out
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.figur_obj = bpy.props.StringProperty(name="Figure Type",
      default="",
      description="Defines the base mesh name of your figure")
    """
    bpy.types.Scene.fig_enum = bpy.props.EnumProperty(
        items=fig_list,
        name="Figure List",
        default="identi_2",
        update=fig_list_enum
    )
    """

def unregister():
    # del bpy.types.Scene.my_enum
    del bpy.types.Scene.figur_obj
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
