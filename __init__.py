# ---------------------------------------------------------------------
# File: __init__.py (for figure_shaders)
# ---------------------------------------------------------------------
# Copyright (c) 16-Nov-2015, Robyn Hahn
# Revision: 17-May-2018
#
# ***** BEGIN GPL LICENSE BLOCK *****
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the:
# Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA.
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Shaders for Imported Figures",
    "author": "Robyn Hahn",
    "version": (0, 6, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "description": "Simple Cycles shaders for imported OBJ Figures",
    "warning": "",
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
from make_shaders.make_shader import BuildShader
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


def show_err_msg(str_msg):
    if str_msg == "INVLDMAT":
        long_msg = "375-Unable to assign shaders to one material: invalid mat zone."
    if str_msg == "NIMGLIST":
        long_msg = "425-Your parm_list.csv points to a folder missing the image_list.csv file."
    if str_msg == "SAVSUCC":
        long_msg = "260-Your settings have been saved successfully."
    if str_msg == "LODSUCC":
        long_msg = "230-Your settings loaded successfully."
    if str_msg == "BADDICT":
        long_msg = "625-Either image_list.csv or parm_list.csv "
        long_msg += "is missing a double-quote. Please double-check your files for typos."
    if str_msg == "NOPARMS":
        long_msg = "600-Missing parm_list.csv. Create this file after finding your images "
        long_msg += "folder by clicking [Save] in Figure Shader Settings."
    if str_msg == "WRONGIMG":
        long_msg = "900-The image_list.csv might be missing or have information on images "
        long_msg += "in another folder. Please double-check image_list.csv that the files "
        long_msg += "correspond to the entries in image_list.csv."
    if str_msg == "INVLSHAD":
        long_msg = "400-FigureShader only supports Principled Shader at this time."
    if str_msg == "BADPARM":
        long_msg = "400-A problem has been detected with your parm_list.csv file."
    if str_msg == "RLTVPATH":
        long_msg = "750-The path to your image files is in an invalid format. Please untick "
        long_msg += "the 'Relative Path' tickbox when you select the path to the image files."
    """
    this [if len()] assumes imgfile name.ext is going to be longer than 9 chars
    """
    if len(str_msg) > 9:
        long_msg = "750-The file:  [ " + str_msg + " ]  is missing, or the file name "
        long_msg += "is spelled incorrectly in image_list.csv in the images folder."

    return long_msg


def read_list(file_name):
    """
    Accepts: file_name - csv file name with fully-qualified path
    Returns: arr_return - either array of entries in the csv, or str NOVALS
    Note: str_return is multi-used, in that it is originally-arbitrarily-
    assigned the name of the file (parm) but if IOError occurs, takes
    the value NOVALS, preventing further processing. The function calling
    read_list() looks for NOVALS.
    """
    global arr_return
    arr_return = []
    str_return = file_name
    try:
        with open(file_name, 'r') as csvfile:
            pass
    except IOError as e:
        str_return = "NOVALS"
    if str_return == file_name:
        with open(file_name, 'r') as csvfile:
            r = csv.reader(csvfile, delimiter=',')
            for row in r:
                if not len(row) == 0:
                    arr_return.append(row)
    else:
        arr_return = str_return
    return arr_return


def clean_str(s_str):
    if not s_str is None:
        s_str = s_str.strip()
        if s_str.startswith('"'):
            s_str = s_str[1:]
        if s_str.endswith('"'):
            s_str = s_str[:-1]
    return s_str


def check_for_files():
    """
    -- blend_name: name-only of the currently open .blend file
    -- blend_dir: fully-qualified path to [blend_name] - 'parm_list.csv'
    -- blend_path: fully-qualified path with [blend_name]
    TODO: remove duplicate funtionality
    """
    str_return = "FILEEXISTS"
    blend_path = bpy.context.blend_data.filepath
    blend_dir = os.path.dirname(blend_path)
    try:
        csv_listpath = os.path.join(blend_dir, "parm_list.csv")
        with open(csv_listpath) as file:
            pass
    except IOError as e:
        str_return = "NOPARMS"

    if str_return == "FILEEXISTS":
        csv_listpath = os.path.join(blend_dir, "parm_list.csv")
        csv_list = read_list(csv_listpath)
        pathlist = dict(csv_list)
        s_img_path = pathlist.get('img_path')
        s_img_path = clean_str(s_img_path)
        if len(s_img_path) == 0:
            str_return = "WHEREIS"

        if str_return == "FILEEXISTS":
            imag_dir = os.path.dirname(s_img_path)
            img_list = os.path.join(imag_dir, "image_list.csv")
            try:
                with open(img_list) as file:
                    pass
            except IOError as e:
                str_return = "NIMGLIST"

            if str_return == "FILEEXISTS":
                """step through image_list.csv, check for invalid file references"""
                pic_list = read_list(img_list)
                try:
                    img_dict = dict(pic_list)
                except IOError as e:
                    str_return = "BADDICT"
                if str_return == "FILEEXISTS":
                    for attr, val in img_dict.items():
                        val = img_dict.get(attr, val)
                        img_file = clean_str(val)
                        if len(img_file) < 1:
                            pass
                        else:
                            path_and_file = os.path.join(imag_dir, img_file)
                            try:
                                with open(path_and_file) as file:
                                    pass
                            except IOError as e:
                                str_return = val
    return str_return


def chk_path_relative(str_path):
    #TODO: Dubious functionality, ln 207 seems to dominate
    if os.name == "posix":
      is_relative = True if str_path[:2] == "//" else False
    if os.name == "nt":
        dir_name = os.path.dirname
        len_dir_name = len(str(dir_name))
        str_path = str_path[:len_dir_name + 2]
    is_relative = True if str_path[:2] == "//" else False
    return is_relative


def chk_path_embedded(str_path):
    if os.name == "posix":
        is_embedded = True if str_path[:2] == "//" else False
    if os.name == "nt":
        substr = str_path[1:2]
        is_embedded = True if substr == ":" else False
    return is_embedded


def parm_dict_get(str_parm):
    """
    Accepts: str_parm - name of value to extract from csv (str)
    Returns: return_parm - a) the value associated to the name (str) or b) NOPARMS
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
    return_parm = ""
    parm_path = bpy.data.filepath
    parm_dir = os.path.dirname(parm_path)
    parm_list = os.path.join(parm_dir, 'parm_list.csv')
    try:
        with open(parm_list) as file:
            pass
    except IOError as e:
        return_parm = "NOPARMS"
    if not return_parm == "NOPARMS":
        parmlist = read_list(parm_list)
        if not parmlist == "NOVALS":
            parmdict = dict(parmlist)
            return_parm = parmdict.get(str_parm)
            return_parm = clean_str(return_parm)
    return return_parm


def parm_list_save(list_settings, parm_path):
    """
    This will write from a list (list_settings) to a file called parm_list.csv in
    the folder named in parm_path, creating the file if it does not already exist.
    As this is an action that is unlikely to generate errors, only pass SAVSUCC.
    """
    parm_dir = parm_path
    parm_list_path = os.path.join(parm_dir, 'parm_list.csv')
    write_file = open(parm_list_path, 'w')
    for item in list_settings:
        write_file.write(item + "\n")
    return "SAVSUCC"


def img_dict_get(str_image, str_path):
    """
    Accepts: str_image  - image name (str)
    .........str_path - path to image (str)
    Returns: strimage   - a) name of image file (str) or b) NIMGLIST
    image_list.csv is in image folder, folder path to image_list.csv is in
    parm_list.csv. Sample image_list.csv values:
    "clrALimb","RMElaineL.jpg"
    "clrLLimb","RMElaineL.jpg"
    "bmpALimb","RMElaineLBnh.jpg"
    "bmpLLimb","RMElaineLBnh.jpg"
    "spcALimb","RMElaineLS.jpg"
    "spcLLimb","RMElaineLS.jpg"
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
    """ keep in mind some image entries may be blank, hence this init of strimage """
    strimage = ""
    image_path = str_path
    image_dir = os.path.dirname(image_path)
    img_list = os.path.join(image_dir, 'image_list.csv')
    try:
        with open(img_list) as file:
            pass
    except IOError as e:
        strimage = "NIMGLIST"

    if strimage == "NIMGLIST":
        pass
    else:
        imagelist = read_list(img_list)
        if not imagelist == "NOVALS":
            imagedict = dict(imagelist)
            try:
                strimage = imagedict.get(str_image)
                strimage = clean_str(strimage)
            except TypeError as e:
                strimage = ""
    return strimage


def img_list_save(list_settings, img_dir):
    """
    This will write from a list (list_settings) to a file called image_list.csv in
    the folder named in pPath, creating the file if it does not already exist.
    As this is an action that is unlikely to generate errors, only pass SAVSUCC.
    """
    image_listpath = os.path.join(image_dir, 'image_list.csv')
    write_file = open(image_listpath, 'w')
    for item in list_settings:
        write_file.write(item + "\n")
    return "SAVSUCC"


def upd_img_path(self, context):
    scn = bpy.context.scene
    selected_figure = scn.objects[(scn.FS_FigureList)]
    for object in bpy.data.objects:
        object.select = False
    selected_figure.select = True


def upd_figure(self, context):
    scn = bpy.context.scene
    selected_fgr = scn.objects[(scn.ob_fig_tools.ep_curfig_enum)]
    for object in bpy.data.objects:
        object.select = False
    selected_fgr.select = True


def upd_entries():
    needs_saving = False
    fgr_tools = bpy.context.scene.ob_fig_tools
    path_bpy_name = bpy.path
    if chk_path_embedded(fgr_tools.sp_HeadClr):
        fgr_tools.sp_HeadClr = path_bpy_name.basename(fgr_tools.sp_HeadClr)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_HeadBmp):
        fgr_tools.sp_HeadBmp = path_bpy_name.basename(fgr_tools.sp_HeadBmp)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_HeadSpc):
        fgr_tools.sp_HeadSpc = path_bpy_name.basename(fgr_tools.sp_HeadSpc)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_BodyClr):
        fgr_tools.sp_BodyClr = path_bpy_name.basename(fgr_tools.sp_BodyClr)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_BodyBmp):
        fgr_tools.sp_BodyBmp = path_bpy_name.basename(fgr_tools.sp_BodyBmp)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_BodySpc):
        fgr_tools.sp_BodySpc = path_bpy_name.basename(fgr_tools.sp_BodySpc)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_LimbClr):
        fgr_tools.sp_LimbClr = path_bpy_name.basename(fgr_tools.sp_LimbClr)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_LimbBmp):
        fgr_tools.sp_LimbBmp = path_bpy_name.basename(fgr_tools.sp_LimbBmp)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_LimbSpc):
        fgr_tools.sp_LimbSpc = path_bpy_name.basename(fgr_tools.sp_LimbSpc)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_EyesClr):
        fgr_tools.sp_EyesClr = path_bpy_name.basename(fgr_tools.sp_EyesClr)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_OralClr):
        fgr_tools.sp_OralClr = path_bpy_name.basename(fgr_tools.sp_OralClr)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_OralBmp):
        fgr_tools.sp_OralBmp = path_bpy_name.basename(fgr_tools.sp_OralBmp)
        needs_saving = True
    if chk_path_embedded(fgr_tools.sp_LashTrn):
        fgr_tools.sp_LashTrn = path_bpy_name.basename(fgr_tools.sp_LashTrn)
        needs_saving = True
    return needs_saving


def pop_fig_list(self, context):
    """ enum property callback:
    expects a tuple containing (identifier, name, description) """
    all_items = [("NoID", "NoName", "NoDesc")]
    if len(bpy.context.scene.objects) != 0:
        all_items = []
        for items in bpy.context.scene.objects:
            all_items.append((items.name, items.name, items.name))
    return all_items


def pop_img_list(self, context):
    all_items = [("1", "pic1", ""),
                ("2", "pic2", ""),
                ("3", "pic3", ""),
                ("4", "pic4", ""),
                ]
    return all_items


def pop_base_fig(self, context):
    all_items = [("V4", "Victoria4", ""),
                ("Mariko", "Mariko", ""),
                ("Dawn", "Dawn", ""),
                ("Antonia", "Antonia", ""),
                ]
    return all_items


def pop_shader_type(self, context):
    all_items = [("PrinSSS", "Principled SSS", ""),
                ("NodeSSS", "Node-Based SSS", ""),
                ]
    return all_items


def get_msg(msg_str, return_val=None):
    sep = ('-')
    if return_val == "str":
        strmsg = msg_str.split(sep, 1)[1]
    else:
        strmsg = msg_str.split(sep)[0]
    return strmsg


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
        msgstr = self.message
        self.message = get_msg(msgstr, "str")
        msgstr = get_msg(msgstr)
        self.mesglen = int(msgstr)
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
        row.alignment = 'RIGHT'
        row.operator("system.ok")


class OkOperator(bpy.types.Operator):
    bl_idname = "system.ok"
    bl_label = "OK"

    def execute(self, context):
        return {'FINISHED'}


class PanelTools(PropertyGroup):
    bl_idname = "panel.shaderdata"
    bl_label = "Set up for Shaders"

    # ========== Shader Choice ==========================
    sp_sel_shader = StringProperty(
        name="selectedShader",
        description="chosen shader",
    )

    ep_shader_enum = EnumProperty(
        name="shaderType",
        description="Choose shader type:",
        items=pop_shader_type
    )

    # ========== Base Figure ============================
    sp_base_figure = StringProperty(
        name="baseFigure",
        description="core figure the mesh is based on",
        default="V4",
    )

    ep_base_fig_enum = EnumProperty(
        name="figureType",
        description="Choose base figure name",
        items=pop_base_fig
    )

    # ========== Selected Object ========================
    sp_sel_figure = StringProperty(
        name="selectedFigure",
        description="figure currently selected",
        default="",
    )

    ep_curfig_enum = EnumProperty(
        name="figureList",
        description="Choose figure for shaders",
        items=pop_fig_list,
        update=upd_figure,
        default=None
    )

    # ========== Path to Images =========================
    sp_imgpath = StringProperty(
        name="imagePath",
        description="Choose a directory:",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    # ========== Principled Shader Settings =============
    fp_sssval = FloatProperty(
        name="SSS Value",
        description="Increasing beyond .2, figure will glow a bit weird...",
        default=0.0800,
    )

    fp_sssrad = FloatProperty(
        name="SSS Radiate",
        description="Trying Radiant values...",
        default=0.1500,
    )

    fp_spcamt = FloatProperty(
        name="Spec Amount",
        description="Trying Specular amount values...",
        default=0.3200,
    )

    fp_spcruf = FloatProperty(
        name="Spec Roughness",
        description="Trying Specular roughness values...",
        default=0.260,
    )

    fp_sheenv = FloatProperty(
        name="Sheen Value",
        description="Trying Sheen values...",
        default=0.1600,
    )

    fp_iorval = FloatProperty(
        name="IOR Value",
        description="Suggested skin IOR value is 1.85...",
        default=1.850,
    )

    sp_HeadClr = StringProperty(
        name="HeadColour",
        description="Choose face colour file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_HeadBmp = StringProperty(
        name="HeadBump",
        description="Choose face bump file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_HeadSpc = StringProperty(
        name="HeadSpecular",
        description="Choose face specular file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    sp_BodyClr = StringProperty(
        name="BodyColour",
        description="Choose torso colour file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_BodyBmp = StringProperty(
        name="BodyBump",
        description="Choose torso bump file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_BodySpc = StringProperty(
        name="BodySpecular",
        description="Choose torso specular file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_LimbClr = StringProperty(
        name="LimbColour",
        description="Choose limb colour file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_LimbBmp = StringProperty(
        name="LimbBump",
        description="Choose limb bump file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    sp_LimbSpc = StringProperty(
        name="LimbSpecular",
        description="Choose limb specular file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    sp_EyesClr = StringProperty(
        name="EyesColour",
        description="Choose iris colour file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    sp_OralClr = StringProperty(
        name="MouthColour",
        description="Choose inner mouth colour file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    sp_OralBmp = StringProperty(
        name="MouthBump",
        description="Choose inner mouth bump file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    sp_LashTrn = StringProperty(
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
    bl_label = "Shader Settings"
    bl_context = "objectmode"
    bl_idname = "MATERIALS_PT_shaders"
    bl_category = "FigureShader"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        s_fgr_tool = scene.ob_fig_tools

        def mySplit():
            splitval = row.split(percentage=0.25)
            return splitval

        if context.object:
            box = layout.box()
            row = box.row()
            col = box.column(align=True)
            col.separator()
            subrow = col.row()
            subrow.operator("object.load_presets", text='Load')
            subrow.operator("object.save_presets", text='Save')
            layout.row().separator()
            row = box.row()
            col.separator()
            row = col.row()
            split = mySplit()
            col_left = split.column()
            col_right = split.column()
            col_left.label(text="Shader")
            col_right.prop(s_fgr_tool, "ep_shader_enum", text='')
            row = col.row()
            split = mySplit()
            col_left.label(text="Figure")
            col_right.prop(s_fgr_tool, "ep_curfig_enum", text='')
            layout.row().separator()
            row = box.row()
            col_left.label(text="Type")
            col_right.prop(s_fgr_tool, "ep_base_fig_enum", "")
            layout.row().separator()
            row = box.row()
            row.label(text="Principled Shader")
            row = box.row()
            row.prop(s_fgr_tool, "fp_sssval")
            row = box.row()
            row.prop(s_fgr_tool, "fp_sssrad")
            row = box.row()
            row.prop(s_fgr_tool, "fp_spcamt")
            row = box.row()
            row.prop(s_fgr_tool, "fp_spcruf")
            row = box.row()
            row.prop(s_fgr_tool, "fp_sheenv")
            row = box.row()
            row.prop(s_fgr_tool, "fp_iorval")
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
    bl_label = "Figure Images"
    bl_context = "objectmode"
    bl_idname = "MATERIALS_PT_images"
    bl_category = "FigureShader"

    def draw(self, context):
        layout = self.layout

        def mySplit():
            splitval = row.split(percentage=0.25)
            return splitval

        scene = bpy.context.scene
        s_fgr_tool = scene.ob_fig_tools

        if context.object:
            box = layout.box()
            col = box.column(align=True)
            col.separator()
            row = col.row()
            split = mySplit()
            col_left = split.column()
            col_right = split.column()
            col_left.label(text="Head-Clr")
            col_right.prop(s_fgr_tool, "sp_HeadClr", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Head-Bmp")
            col_right.prop(s_fgr_tool, "sp_HeadBmp", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Head-Spc")
            col_right.prop(s_fgr_tool, "sp_HeadSpc", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Body-Clr")
            col_right.prop(s_fgr_tool, "sp_BodyClr", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Body-Bmp")
            col_right.prop(s_fgr_tool, "sp_BodyBmp", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Body-Spc")
            col_right.prop(s_fgr_tool, "sp_BodySpc", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Limb-Clr")
            col_right.prop(s_fgr_tool, "sp_LimbClr", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Limb-Bmp")
            col_right.prop(s_fgr_tool, "sp_LimbBmp", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Limb-Spc")
            col_right.prop(s_fgr_tool, "sp_LimbSpc", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Eyes-Clr")
            col_right.prop(s_fgr_tool, "sp_EyesClr", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Mouth-Clr")
            col_right.prop(s_fgr_tool, "sp_OralClr", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Mouth-Bmp")
            col_right.prop(s_fgr_tool, "sp_OralBmp", text="")
            row = col.row()
            split = mySplit()
            col_left.label(text="Lashes-Trn")
            col_right.prop(s_fgr_tool, "sp_LashTrn", text="")
            row = col.row()
            box = layout.box()
            row = box.row()
            row.label(text="Image files location: ")
            row = box.row()
            row.prop(s_fgr_tool, "sp_imgpath", text="")
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
        def all_conds_met():
            b_all_met = False
            if bpy.path.basename(bpy.context.blend_data.filepath):
                xPath = bpy.path.basename(bpy.context.blend_data.filepath)
                b_all_met = True
            return b_all_met

        return all_conds_met()

    def execute(self, context):
        f_tools = bpy.context.scene.ob_fig_tools
        abs_img_path = bpy.path.abspath(f_tools.sp_imgpath)
        self.clear_img_panel()
        return {'FINISHED'}

    def clear_img_panel(self):
        f_tools = bpy.context.scene.ob_fig_tools
        f_tools.sp_HeadClr = ""
        f_tools.sp_HeadBmp = ""
        f_tools.sp_HeadSpc = ""
        f_tools.sp_BodyClr = ""
        f_tools.sp_BodyBmp = ""
        f_tools.sp_BodySpc = ""
        f_tools.sp_LimbClr = ""
        f_tools.sp_LimbBmp = ""
        f_tools.sp_LimbSpc = ""
        f_tools.sp_EyesClr = ""
        f_tools.sp_OralClr = ""
        f_tools.sp_OralBmp = ""
        f_tools.sp_LashTrn = ""


class LoadPresets(bpy.types.Operator):
    bl_idname = "object.load_presets"
    bl_label = "Loads Shader Presets from CSV"

    @classmethod
    def poll(cls, context):
        def all_conds_met():
            bAllMet = False
            if bpy.path.basename(bpy.context.blend_data.filepath):
                xPath = bpy.path.basename(bpy.context.blend_data.filepath)
                bAllMet = True
            return bAllMet

        return all_conds_met()

    def execute(self, context):
        s_err_msg = ""
        x_chk = None
        f_tools = bpy.context.scene.ob_fig_tools
        #absImgPath = bpy.path.abspath(f_tools.sp_imgpath)
        try:
            x_chk = parm_dict_get('img_path')
        except:
            x_chk = "NOPARMS"

        if x_chk == 'NOPARMS':
            s_err_msg = show_err_msg(x_chk)
            bpy.ops.system.message('INVOKE_DEFAULT',
                                   type="Error",
                                   message=s_err_msg,
                                   )
        elif x_chk == 'WHEREIS':
            s_err_msg = show_err_msg(x_chk)
            bpy.ops.system.message('INVOKE_DEFAULT',
                                   type="Error",
                                   message=s_err_msg,
                                   )
        else:
            """ Really clumsy, but it works """
            f_tools.sp_imgpath = clean_str(parm_dict_get('img_path'))
            f_tools.fp_sssval = float(parm_dict_get('fl01_sssval'))
            f_tools.fp_sssrad = float(parm_dict_get('fl02_sssrad'))
            f_tools.fp_spcamt = float(parm_dict_get('fl05_spcamt'))
            f_tools.fp_spcruf = float(parm_dict_get('fl06_spcruf'))
            f_tools.fp_sheenv = float(parm_dict_get('fl11_sheenv'))
            f_tools.fp_iorval = float(parm_dict_get('fl14_iorval'))
            s_err_msg = show_err_msg("LODSUCC")
            bpy.ops.system.message('INVOKE_DEFAULT',
                                   type="Error",
                                   message=s_err_msg,
                                   )

        return {'FINISHED'}


class SavePresets(bpy.types.Operator):
    bl_idname = "object.save_presets"
    bl_label = "Saves Shader Presets to CSV"

    @classmethod
    def poll(cls, context):
        def all_conds_met():
            b_all_met = False
            if bpy.path.basename(bpy.context.blend_data.filepath):
                xPath = bpy.path.basename(bpy.context.blend_data.filepath)
                b_all_met = True
            return b_all_met

        return all_conds_met()

    def execute(self, context):
        f_tools = bpy.context.scene.ob_fig_tools
        """ chk_path_relative returns .T. if path is relative """
        if chk_path_relative(f_tools.sp_imgpath):
            s_error_msg = show_err_msg("RLTVPATH")
            bpy.ops.system.message('INVOKE_DEFAULT',
                                   type="Error",
                                   message=s_error_msg,
                                   )
            return {'CANCELLED'}
        else:
            blend_path = bpy.context.blend_data.filepath
            blend_dir = os.path.dirname(blend_path)
            abs_img_path = bpy.path.abspath(f_tools.sp_imgpath)
            wrtfile = []
            simgp = '"' + abs_img_path + '"'
            ssval = '"' + format(f_tools.fp_sssval, 'f') + '"'
            ssrad = '"' + format(f_tools.fp_sssrad, 'f') + '"'
            ssamt = '"' + format(f_tools.fp_spcamt, 'f') + '"'
            ssruf = '"' + format(f_tools.fp_spcruf, 'f') + '"'
            ssshe = '"' + format(f_tools.fp_sheenv, 'f') + '"'
            ssior = '"' + format(f_tools.fp_iorval, 'f') + '"'
            wrtfile.append('"img_path", ' + simgp)
            wrtfile.append('"fl01_sssval", ' + ssval)
            wrtfile.append('"fl02_sssrad", ' + ssrad)
            wrtfile.append('"fl05_spcamt", ' + ssamt)
            wrtfile.append('"fl06_spcruf", ' + ssruf)
            wrtfile.append('"fl11_sheenv", ' + ssshe)
            wrtfile.append('"fl14_iorval", ' + ssior)
            x_chk = parm_list_save(wrtfile, blend_dir)
            s_error_msg = show_err_msg(x_chk)
            bpy.ops.system.message('INVOKE_DEFAULT',
                                   type="Error",
                                   message=s_error_msg,
                                   )
            return {'FINISHED'}


class LoadImages(bpy.types.Operator):
    bl_idname = "object.load_images"
    bl_label = "Loads image names from CSV"

    @classmethod
    def poll(cls, context):
        def all_conds_met():
            b_all_met = False
            if bpy.path.basename(bpy.context.blend_data.filepath):
                #xPath = bpy.path.basename(bpy.context.blend_data.filepath) #(not in use)
                b_all_met = True
            return b_all_met

        return all_conds_met()

    def clear_img_panel(self):
        f_tools = bpy.context.scene.ob_fig_tools
        f_tools.sp_HeadClr = ""
        f_tools.sp_HeadBmp = ""
        f_tools.sp_HeadSpc = ""
        f_tools.sp_BodyClr = ""
        f_tools.sp_BodyBmp = ""
        f_tools.sp_BodySpc = ""
        f_tools.sp_LimbClr = ""
        f_tools.sp_LimbBmp = ""
        f_tools.sp_LimbSpc = ""
        f_tools.sp_EyesClr = ""
        f_tools.sp_OralClr = ""
        f_tools.sp_OralBmp = ""
        f_tools.sp_LashTrn = ""

    def get_base_names(self):
        f_tools = bpy.context.scene.ob_fig_tools
        abs_img_path = bpy.path.abspath(f_tools.sp_imgpath)
        f_tools.sp_HeadClr = clean_str(img_dict_get('clr_Face', abs_img_path))
        f_tools.sp_HeadBmp = clean_str(img_dict_get('bmp_Face', abs_img_path))
        f_tools.sp_HeadSpc = clean_str(img_dict_get('spc_Face', abs_img_path))
        f_tools.sp_BodyClr = clean_str(img_dict_get('clr_Body', abs_img_path))
        f_tools.sp_BodyBmp = clean_str(img_dict_get('bmp_Body', abs_img_path))
        f_tools.sp_BodySpc = clean_str(img_dict_get('spc_Body', abs_img_path))
        f_tools.sp_LimbClr = clean_str(img_dict_get('clrALimb', abs_img_path))
        f_tools.sp_LimbBmp = clean_str(img_dict_get('bmpALimb', abs_img_path))
        f_tools.sp_LimbSpc = clean_str(img_dict_get('spcALimb', abs_img_path))
        f_tools.sp_EyesClr = clean_str(img_dict_get('clr_Eyes', abs_img_path))
        f_tools.sp_OralClr = clean_str(img_dict_get('clrMouth', abs_img_path))
        f_tools.sp_OralBmp = clean_str(img_dict_get('bmpMouth', abs_img_path))
        f_tools.sp_LashTrn = clean_str(img_dict_get('clr_Lash', abs_img_path))

    def addPath2Name(self):
        f_tools = bpy.context.scene.ob_fig_tools
        absImgPath = bpy.path.abspath(f_tools.sp_imgpath)
        f_tools.sp_HeadClr = absImgPath + f_tools.sp_HeadClr if f_tools.sp_HeadClr else ""
        f_tools.sp_HeadBmp = absImgPath + f_tools.sp_HeadBmp if f_tools.sp_HeadBmp else ""
        f_tools.sp_HeadSpc = absImgPath + f_tools.sp_HeadSpc if f_tools.sp_HeadSpc else ""
        f_tools.sp_BodyClr = absImgPath + f_tools.sp_BodyClr if f_tools.sp_BodyClr else ""
        f_tools.sp_BodyBmp = absImgPath + f_tools.sp_BodyBmp if f_tools.sp_BodyBmp else ""
        f_tools.sp_BodySpc = absImgPath + f_tools.sp_BodySpc if f_tools.sp_BodySpc else ""
        f_tools.sp_LimbClr = absImgPath + f_tools.sp_LimbClr if f_tools.sp_LimbClr else ""
        f_tools.sp_LimbBmp = absImgPath + f_tools.sp_LimbBmp if f_tools.sp_LimbBmp else ""
        f_tools.sp_LimbSpc = absImgPath + f_tools.sp_LimbSpc if f_tools.sp_LimbSpc else ""
        f_tools.sp_EyesClr = absImgPath + f_tools.sp_EyesClr if f_tools.sp_EyesClr else ""
        f_tools.sp_OralClr = absImgPath + f_tools.sp_OralClr if f_tools.sp_OralClr else ""
        f_tools.sp_OralBmp = absImgPath + f_tools.sp_OralBmp if f_tools.sp_OralBmp else ""
        f_tools.sp_LashTrn = absImgPath + f_tools.sp_LashTrn if f_tools.sp_LashTrn else ""

    def execute(self, context):
        items = []
        s_error = "FILEEXISTS"
        f_tools = bpy.context.scene.ob_fig_tools
        # TODO: not in use, remove?
        #absImgPath = bpy.path.abspath(f_tools.sp_imgpath)
        """
        1) Check image path is not as relative path format
        [    Scripts tend to have dramas with paths that are not absolute. ]
        """
        if chk_path_relative(f_tools.sp_imgpath):
            s_error_msg = show_err_msg("RLTVPATH")
            bpy.ops.system.message('INVOKE_DEFAULT',
                                   type="Error",
                                   message=s_error_msg,
                                   )
            return {'CANCELLED'}

        else:
            """
            2) Check for existence of parm_list.csv.
            [    parm_dict_get returns NOPARMS if parm_list.csv doesn't exist ]
            """
            try:
                s_error = parm_dict_get('img_path')
            except ValueError as e:
                s_error = "NOPARMS"
            if s_error == 'NOPARMS':
                s_error_msg = show_err_msg(s_error)
                bpy.ops.system.message('INVOKE_DEFAULT',
                                       type="Error",
                                       message=s_error_msg,
                                       )
                return {'CANCELLED'}

            else:
                """
                3) Check for existence of image_list.csv.
                [    s_error now holds the fully-qualified path name to the images ]
                """
                image_path = f_tools.sp_imgpath
                image_dir = os.path.dirname(image_path)
                img_list = os.path.join(image_dir, 'image_list.csv')
                s_error = img_dict_get('clr_Face', img_list)
                if s_error == 'NIMGLIST':
                    s_error_msg = show_err_msg(s_error)
                    bpy.ops.system.message('INVOKE_DEFAULT',
                                           type="Error",
                                           message=s_error_msg,
                                           )
                    return {'CANCELLED'}

                else:
                    """
                    4) Conditions all met, load images.
                    """
                    self.clear_img_panel()
                    self.get_base_names()
                    s_error_msg = show_err_msg("LODSUCC")
                    bpy.ops.system.message('INVOKE_DEFAULT',
                                           type="Error",
                                           message=s_error_msg,
                                           )
                    return {'FINISHED'}



class SaveImages(bpy.types.Operator):
    bl_idname = "object.save_images"
    bl_label = "Saves Image Names to CSV"

    @classmethod
    def poll(cls, context):
        def all_conds_met():
            b_all_met = False
            if bpy.path.basename(bpy.context.blend_data.filepath):
                #xPath = bpy.path.basename(bpy.context.blend_data.filepath)
                b_all_met = True
            return b_all_met

        return all_conds_met()

    def execute(self, context):
        f_tools = bpy.context.scene.ob_fig_tools
        imagePath = bpy.path.abspath(f_tools.sp_imgpath)
        get_bpy_pname = bpy.path
        wrtfile = []
        hdc = '"' + get_bpy_pname.basename(f_tools.sp_HeadClr) + '"'
        hdb = '"' + get_bpy_pname.basename(f_tools.sp_HeadBmp) + '"'
        hds = '"' + get_bpy_pname.basename(f_tools.sp_HeadSpc) + '"'
        byc = '"' + get_bpy_pname.basename(f_tools.sp_BodyClr) + '"'
        byb = '"' + get_bpy_pname.basename(f_tools.sp_BodyBmp) + '"'
        bys = '"' + get_bpy_pname.basename(f_tools.sp_BodySpc) + '"'
        lbc = '"' + get_bpy_pname.basename(f_tools.sp_LimbClr) + '"'
        lbb = '"' + get_bpy_pname.basename(f_tools.sp_LimbBmp) + '"'
        lbs = '"' + get_bpy_pname.basename(f_tools.sp_LimbSpc) + '"'
        eye = '"' + get_bpy_pname.basename(f_tools.sp_EyesClr) + '"'
        olc = '"' + get_bpy_pname.basename(f_tools.sp_OralClr) + '"'
        olb = '"' + get_bpy_pname.basename(f_tools.sp_OralBmp) + '"'
        trn = '"' + get_bpy_pname.basename(f_tools.sp_LashTrn) + '"'
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
        s_msg = img_list_save(wrtfile, imagePath)
        s_conf_msg = show_err_msg(s_msg)
        bpy.ops.system.message('INVOKE_DEFAULT',
                               type="Error",
                               message=s_conf_msg,
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
        def all_conds_met():
            b_all_met = False
            if bpy.path.basename(bpy.context.blend_data.filepath):
                #xPath = bpy.path.basename(bpy.context.blend_data.filepath)
                b_all_met = True
            return b_all_met

        return all_conds_met()

    def execute(self, context):
        def checked_settings():
            """ just a stub at this point """
            if upd_entries():
                SaveImages(self)
            parms_ready = True
            return parms_ready

        if checked_settings():
            shaders_setup()
        return {'FINISHED'}


def shaders_setup():
    sMissingFile = ""
    blend_name = ""
    scene = bpy.context.scene

    def paintShaders():
        """
        =============================================================
        These are defined in figure_defs.py. Cuurently defined for:
        V4, Dawn, Mariko, Antonia
        The var Figure is defined in check_for_files, just before
        paintShaders() is invoked.
        ========================================================
        """
        f_tools = scene.ob_fig_tools
        f_tools.sp_sel_shader = f_tools.ep_shader_enum
        f_tools.sp_base_figure = f_tools.ep_base_fig_enum
        dict_mats = matZones(f_tools.sp_base_figure)

        """
        =============================================================
        Truncates strings like 3_SkinLeg:1 to 3_SkinLeg by detecting
        an extra chars in name, trapping curently for   . and :
        ========================================================
        """

        def get_mat_name(mtlName):
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

        clrALimb = f_tools.sp_LimbClr
        clrLLimb = f_tools.sp_LimbClr
        bmpALimb = f_tools.sp_LimbBmp
        bmpLLimb = f_tools.sp_LimbBmp
        spcALimb = f_tools.sp_LimbSpc
        spcLLimb = f_tools.sp_LimbClr
        clr_Body = f_tools.sp_BodyClr
        bmp_Body = f_tools.sp_BodyBmp
        spc_Body = f_tools.sp_BodySpc
        clr_Face = f_tools.sp_HeadClr
        bmp_Face = f_tools.sp_HeadBmp
        spc_Face = f_tools.sp_HeadSpc
        clr_Eyes = f_tools.sp_EyesClr
        clrMouth = f_tools.sp_OralClr
        bmpMouth = f_tools.sp_OralBmp
        clr_Lash = f_tools.sp_LashTrn

        """ Not all figures have a bump or spec map. The bump maps can be replaced
        by procedural bump, the spec maps may need another solution, as yet undefined."""
        bmpALimb = None if '0' else bmpALimb
        bmpLLimb = None if '0' else bmpLLimb
        spcALimb = None if '0' else spcALimb
        spcLLimb = None if '0' else spcLLimb
        bmp_Body = None if '0' else bmp_Body
        spc_body = None if '0' else spc_Body
        bmp_Face = None if '0' else bmp_Face
        spc_Face = None if '0' else spc_Face
        bmpMouth = None if '0' else bmpMouth

        """ make the current figure active """
        sp_sel_figure = f_tools.ep_curfig_enum
        bpy.context.scene.objects.active = bpy.data.objects[sp_sel_figure]
        sp_sel_figure = bpy.data.objects[sp_sel_figure]
        bpy.context.object.active_material_index = 0
        all_slots = bpy.context.object.material_slots

        """ iterate through the material slots... """
        for i in range(len(all_slots)):
            img_clr = None
            bpy.context.object.active_material_index = i

            """
            On occasion empty material slots are created during import from Poser.
            These empty slots will be ignored.
            """
            if not sp_sel_figure.active_material == None:
                mat = sp_sel_figure.active_material
                mat_name = sp_sel_figure.active_material.name
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                mat_type = get_mat_name(mat_name)
                if not mat_type == "NF":
                    if mat_type[0:4] == 'Eyes':
                        if mat_type[5:] == 'Lash':
                            img_clr = clr_Lash
                        if mat_type[5:] == 'Clr':
                            img_clr = clr_Eyes
                        if mat_type[5:] == 'Trn':
                            img_clr = None

                    if mat_type[0:4] == 'Skin':
                        if mat_type[5:] == 'Body':
                            img_clr = clr_Body
                        if mat_type[5:] == 'Face':
                            img_clr = clr_Face
                        if mat_type[5:] == 'Arms' or mat_type[5:] == 'Legs':
                            if clrALimb == clrLLimb:
                                img_clr = clrALimb
                            else:
                                if mat_type[5:] == 'Arms':
                                    img_clr = clrALimb
                                else:
                                    img_clr = clrLLimb
                    if mat_type == 'Mouth':
                        img_clr = clrMouth
                    if img_clr is not None:
                        if len(img_clr) > 0:
                            if f_tools.sp_sel_shader == "PrinSSS":
                                img_clr = f_tools.sp_imgpath + img_clr
                                img_clr = bpy.data.images.load(filepath=img_clr)

                                """ Sending:          material-clrImage """
                                new_mat = BuildShader(sp_sel_figure, mat_type, img_clr)
                            else:
                                s_error_msg = show_err_msg("INVLSHAD")
                                bpy.ops.system.message('INVOKE_DEFAULT',
                                                       type="Error",
                                                       message=s_error_msg,
                                                       )
            else:
                s_error_msg = show_err_msg("INVLDMAT")
                bpy.ops.system.message('INVOKE_DEFAULT',
                                       type="Error",
                                       message=s_error_msg,
                                       )

    """
    ==============================================================================
    Iterate through the objects in the scene, run paintShader only for FILEEXISTS
    ==============================================================================
    """
    scn = bpy.context.scene
    sp_sel_figure = scn.ob_fig_tools.ep_curfig_enum
    sini_msg = check_for_files()
    if sini_msg == "FILEEXISTS":
        for obj in scn.objects:
            if obj.type == 'MESH':
                """ FINALLY: run the script!!! """
                ob_name = obj.name
                if ob_name == sp_sel_figure:
                    obj.select = True
                    paintShaders()
                    obj.select = False
    else:
        s_error_msg = show_err_msg(sini_msg)
        bpy.ops.system.message('INVOKE_DEFAULT',
                               type="Error",
                               message=s_error_msg,
                               )


def register():
    """ Note2Self: first in, best dressed -> last out """
    bpy.utils.register_module(__name__)
    bpy.types.Scene.ob_fig_tools = PointerProperty(
        name="fPanelTools",
        description="ob_fig_tools",
        type=PanelTools)


def unregister():
    del bpy.types.Scene.ob_fig_tools
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
