# ---------------------------------------------------------------------
# File: __init__.py (for make_shaders)
# ---------------------------------------------------------------------
#
# Copyright (c) 16-Nov-2015, Robyn Hahn
# Revision: 12-Oct-2016
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
    "name": "Shaders for Poser Figures",
    "author": "Robyn Hahn",
    "version": (0, 4, 0),
    "blender": (2, 77, 0),
    "location": "View3D",
    "description": "Generates simple Cycles shaders for select Poser Figures",
    "warning": "minimally tested in Linux and Windows, not Mac. Spartan error-handling ...",
    "wiki_url": "",
    "category": "Material"}


if "bpy" in locals():
    import imp

    imp.reload(figure_defs)
    imp.reload(make_shaders)
    print("make_shaders: Reloaded multifiles")
else:
    from . import figure_defs
    from . import make_shaders
    print("make_shaders: Imported multifiles")

from make_shaders.make_shaders import buildShader
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

figur_name = ''
"""Convert type:dictionary figure list from matZones to type:list -
Need to sort a few issues, here:
[Error] AttributeError: 'matZones' object has no attribute 'items'

fig_dict = matZones('list_figs')
fig_list = [(v,k) for k, v in fig_dict.items()]"""

class MatShaderPanel(bpy.types.Panel):
    """Create shaders for your Poser figure: Panel"""
    bl_label = "Figure Files Util"
    bl_idname = "MATERIALS_PT_shaders"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        
        if context.object:
            obj = context.object
            figur_name = obj.name

            row = layout.row()
            row.label(text='Apply shaders to:')

            row = layout.row()
            row.label(text="Active object is: " + obj.name)
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
    """
    @classmethod
    def poll(cls, context):
        # object must be active
        if bpy.path.basename(bpy.context.blend_data.filepath):
            return context.active_object is not None
        # if the file has not been saved, basename will be None
        else:
            return bpy.path.basename(bpy.context.blend_data.filepath)

    def execute(self, context):
        # possibly check here that a known figure-name has been assigned to the object
        # if bpy.context.scene.objects.active.name in fig_list:
        shadersSetup()
        return {'FINISHED'}
        

def shadersSetup():
    lExit = False
    sMesg = 'N'

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
        sStr = sStr.strip()
        if sStr.startswith('"') and sStr.endswith('"'):
            sStr = sStr[1:-1]
        return sStr
    
    
    
    """ Keep from running this next section if issues with name"""
    def paintShaders():
        # defined in figure_defs.py
        dict_mats = matZones(figure)

        """ =============================================================
            Truncates strings like 3_SkinLeg:1 to 3_SkinLeg by detecting
            an extra chars in name, trapping curently for   . and :     
            ========================================================"""
        def getMatName(mtlName):
            sep = 'NF'
            if '.' in mtlName:
                sep = ('.')
            if ':' in mtlName:
                sep = (':')
            # truncate only if a . or : is found
            if not sep == 'NF':
                mtlName = mtlName.split(sep, 1)[0]
            # get the actual material type
            mtlType = dict_mats.figMat.get(mtlName)
            if mtlType is None:
                return sep
            else:
                return mtlType
    

        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            bpy.context.scene.render.engine = 'CYCLES'
        
        """ Fully-qualified path to the currently open .blend. 
        'path_list.csv' lives here. """ 
        blend_path = bpy.data.filepath
        blend_dir = os.path.dirname(blend_path)
        csv_listpath = os.path.join(blend_dir, "path_list.csv")
        
        # currently has 3 entries: list those, weed out empties
        csv_list = readList(csv_listpath)
        pathlist = dict(csv_list)
            
        # get the path to the images - [ WILL NEED ERROR CHECKING ]
        path_str = pathlist.get('img_path')
        path_str = cleanStr(path_str)
        imag_dir = os.path.dirname(path_str)
        img_list = os.path.join(imag_dir, "image_list.csv")
        pic_list = readList(img_list)
        imaglist = dict(pic_list)
        
        clrALimb = cleanStr(imaglist.get('clrALimb'))
        clrLLimb = cleanStr(imaglist.get('clrLLimb'))
        bmpALimb = cleanStr(imaglist.get('bmpALimb'))
        bmpLLimb = cleanStr(imaglist.get('bmpLLimb'))
        spcALimb = cleanStr(imaglist.get('spcALimb'))
        spcLLimb = cleanStr(imaglist.get('spclLimb'))
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
        
        # makes sure your figure is selected and nothing else
        # bpy.ops.object.select_all(action='DESELECT')
        
        # makes the current figure active
        bpy.context.scene.objects.active = bpy.data.objects[figure]
        curr_obj = bpy.data.objects[figure]
        bpy.context.object.active_material_index = 0
        all_slots = bpy.context.object.material_slots
        
        # iterate through the material slots...
        for i in range(len(all_slots)):
            img_Bmp = None
            img_Clr = None
            img_Spc = None
            
            # Passed parms
            ImgColr = None
            ImgBump = None
            ImgSpec = None
            
            bpy.context.object.active_material_index = i
            
            """ On occasion empty material slots are created during import from Poser.
            These empty slots will be ignored. """
            if not curr_obj.active_material == None:
                mat = curr_obj.active_material
                matName = curr_obj.active_material.name
                mat.use_nodes = True
                nodes = mat.node_tree.nodes 
                """ Added 11-10-2016: checks for valid material name """
                matType = getMatName(matName)
                if not matType == "NF":
                    if matType[0:4] == 'Eyes':
                        ImgBump == None
                        if matType[5:] == 'Lash':
                            img_Clr = clr_Lash
                        if matType[5:] == 'Clr':
                            img_Clr = clr_Eyes
                        if matType[5:] == 'Trn':
                            img_Clr = None
                  
                    if matType[0:4] == 'Skin':
                        if matType[5:] == 'Body':
                            img_Clr = clr_Body
                            if not bmp_Body == None:
                                img_Bmp = bmp_Body
                            if not spc_Body == None:
                                img_Spc = spc_Body
                        if matType[5:] == 'Face':
                            img_Clr = clr_Face
                            if not bmp_Face == None:
                                img_Bmp = bmp_Face
                            if not spc_Face == None:
                                img_Spc = spc_Face
                        if matType[5:] == 'Arms' or matType[5:] == 'Legs':
                            if clrALimb == clrLLimb:
                                img_Clr = clrALimb
                                if not bmpALimb == None:
                                    img_Bmp = bmpALimb
                                if not spcALimb == None:
                                    img_Spc = spcALimb 
                            else:
                                if matType[5:] == 'Arms':
                                    img_Clr = clrALimb
                                    if not bmpALimb == None:
                                        img_Bmp = bmpALimb
                                    if not spcALimb == None:
                                        img_Spc = spcALimb
                                else:
                                    img_Clr = clrLLimb
                                    if not bmpLLimb == None:
                                        img_Bmp = bmpLLimb
                                    if not spcALimb == None:
                                        img_Spc = spcLLimb
                    if matType == 'Mouth':
                        img_Clr = clrMouth
                        if not bmpMouth == None:
                            img_Bmp = bmpMouth
                    # fully qualified path added
                    if img_Clr is not None:
                        ImgColr = path_str + img_Clr
                        ImgColr = bpy.data.images.load(filepath=ImgColr)
                    if img_Bmp is not None:
                        ImgBump = path_str + img_Bmp
                        ImgBump = bpy.data.images.load(filepath=ImgBump)
                    if img_Spc is not None:
                        ImgSpec = path_str + img_Spc
                        ImgSpec = bpy.data.images.load(filepath=ImgSpec)
                    """ Sending:      figure (obj), material, colour, bump map, spec map
                                      (last two can be None)"""
                    new_mat = buildShader(curr_obj, matType, ImgColr, ImgBump, ImgSpec)
                else:
                  print ("Unable to assign shaders at this time.")
    
    
    
    """ =====================================================================================
         Iterate through the objects in the scene, run paintShader only for valid objects
        ================================================================================== """
    sScen = bpy.context.scene
    figName = bpy.context.scene.objects.active.name
    
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
