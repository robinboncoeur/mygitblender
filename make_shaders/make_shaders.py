# ---------------------------------------------------------------------
# File: make_shaders.py
# ---------------------------------------------------------------------
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

import bpy

# builds very simple shaders for skin, eyes (incl trans), lashes and mouth
class buildShader():
    def __init__(self, cObj, cRegion, ImgClr = None, ImgBum = None, ImgSpc = None):
        self.selObj = cObj
        self.Region = cRegion
        self.ImgCol = ImgClr
        self.ImgBmp = ImgBum
        self.noBump = False if ImgBum else True
        self.ImgSpc = ImgSpc
        self.noSpec = False if ImgSpc else True

        self.selObj.select = True
        self.selMats = self.selObj.active_material
        self.selMats.use_nodes = True
        self.treeNodes = self.selMats.node_tree
        self.nodeLinks = self.treeNodes.links
        for n in self.treeNodes.nodes:
            self.treeNodes.nodes.remove(n)
        
        #    def shaderDesign(self)
        # Sets up nodes as required by region
        if self.Region[0:4] == 'Skin' or self.Region == 'Mouth' or self.Region[5:] == 'Clr' or self.Region[5:] == 'Lash':
            self.shaTcd = self.treeNodes.nodes.new('ShaderNodeTexCoord')
            self.shaMap = self.treeNodes.nodes.new('ShaderNodeMapping')
            self.TexCol = self.treeNodes.nodes.new('ShaderNodeTexImage')
            self.TexCol.image = self.ImgCol
            self.TexCol.color_space = 'COLOR'
            self.shDif1 = self.treeNodes.nodes.new('ShaderNodeBsdfDiffuse')

        # no bump map was provided: create a procedural bump instead
        if self.Region[0:4] == 'Skin':
            if not self.noBump:
                self.TexBmp = self.treeNodes.nodes.new('ShaderNodeTexImage')    
                self.TexBmp.image = self.ImgBmp
                self.TexBmp.color_space = 'NONE'                
            else:
                self.TexBmp = self.treeNodes.nodes.new('ShaderNodeTexNoise')
            if not self.noSpec:
                self.TexSpc = self.treeNodes.nodes.new('ShaderNodeTexImage')    
                self.TexSpc.image = self.ImgSpc
                self.TexSpc.color_space = 'NONE'                
            
            # nodes common to all skin
            self.shaTrl = self.treeNodes.nodes.new('ShaderNodeBsdfTranslucent')
            self.shDif2 = self.treeNodes.nodes.new('ShaderNodeBsdfDiffuse')
            self.clrMix = self.treeNodes.nodes.new('ShaderNodeMixRGB')
            self.mathMl = self.treeNodes.nodes.new('ShaderNodeMath')
            self.shaMx3 = self.treeNodes.nodes.new('ShaderNodeMixShader')

        if self.Region[0:4] == 'Skin' or self.Region == 'Mouth':
            self.shGls1 = self.treeNodes.nodes.new('ShaderNodeBsdfGlossy')
        if self.Region[0:4] == 'Skin' or self.Region[5:] == 'Trn':   
            self.shaMx2 = self.treeNodes.nodes.new('ShaderNodeMixShader')
        if self.Region == 'Eyes_Clr':
            self.shaGla = self.treeNodes.nodes.new('ShaderNodeBsdfGlass')
        if self.Region == 'Eyes_Trn' or self.Region == 'Eyes_Lash':
            self.shaTra = self.treeNodes.nodes.new('ShaderNodeBsdfTransparent')
        if self.Region == 'Eyes_Trn':
            self.shGls1 = self.treeNodes.nodes.new('ShaderNodeBsdfGlossy')
            self.shaGla = self.treeNodes.nodes.new('ShaderNodeBsdfGlass')

        self.shaMx1 = self.treeNodes.nodes.new('ShaderNodeMixShader')
        self.shaOut = self.treeNodes.nodes.new('ShaderNodeOutputMaterial')
        
        # Skin and Eyes mat slot names have _suffixes 
        if self.Region[0:4] == 'Skin':
            self.makeSkin()
        if self.Region[0:4] == 'Eyes':
            self.makeEyes(self.Region)
        if self.Region == 'Mouth':
            self.makeMouth()

    def makeSkin(self):            
        # Diffuse vals
        self.shDif1.inputs[1].default_value = .15        
        self.shDif2.inputs[1].default_value = .12        
        # Translucent vals
        self.shaTrl.inputs[0].default_value = [.8, .22, .06, 1]
        # Glossy vals
        self.shGls1.inputs[1].default_value = .12
        # Mix-RGB vals
        self.clrMix.inputs[0].default_value = .1
        self.clrMix.inputs[2].default_value = [.5, .35, .275, 1]
        # Multiply vals
        self.mathMl.operation = 'MULTIPLY'
        if self.noBump:
            self.mathMl.inputs[1].default_value = .065
        else:
            self.mathMl.inputs[1].default_value = .01
        # Default Noise node vals
        if self.noBump:
            self.TexBmp.inputs[1].default_value = 120
            self.TexBmp.inputs[2].default_value = 25
            self.TexBmp.inputs[3].default_value = 120
        
        self.shaTcd.location = -950, 300
        self.shaMap.location = -750, 300
        if not self.noSpec:
            self.TexCol.location = -300, 650
            self.TexBmp.location = -300, 350
            self.TexSpc.location = -300, 100
        else:
            self.TexCol.location = -300, 400
            self.TexBmp.location = -300, 100
        self.shDif1.location = 0, 400
        self.shaTrl.location = 0, 200
        self.clrMix.location = 0, 100
        self.shaMx3.location = 200, 400
        self.shDif2.location = 200, 150
        self.shaMx2.location = 400, 400
        self.shGls1.location = 400, 100
        self.shaMx1.location = 600, 400
        self.mathMl.location = 600, 100
        self.shaOut.location = 800, 300

        # Tex coord and mapping
        self.nodeLinks.new(self.shaTcd.outputs[2], self.shaMap.inputs[0])
        self.nodeLinks.new(self.shaMap.outputs[0], self.TexCol.inputs[0])
        self.nodeLinks.new(self.shaMap.outputs[0], self.TexBmp.inputs[0])
        # clr and bmp
        self.nodeLinks.new(self.TexCol.outputs[0], self.shDif1.inputs[0])
        self.nodeLinks.new(self.TexCol.outputs[0], self.clrMix.inputs[1])
        self.nodeLinks.new(self.TexBmp.outputs[0], self.mathMl.inputs[0])
        # Mixing colourMap with Translucent ( reddish )
        self.nodeLinks.new(self.shDif1.outputs[0], self.shaMx3.inputs[1])
        self.nodeLinks.new(self.shaTrl.outputs[0], self.shaMx3.inputs[2])
        self.shaMx3.inputs[0].default_value = .065
        # Mixing ClrMap/Translu and ClrMix ( beige )
        self.nodeLinks.new(self.shaMx3.outputs[0], self.shaMx2.inputs[1])
        self.nodeLinks.new(self.clrMix.outputs[0], self.shDif2.inputs[0])
        self.nodeLinks.new(self.shDif2.outputs[0], self.shaMx2.inputs[2])
        self.shaMx2.inputs[0].default_value = .05
        # Mixing ClrMap/Transl/ClrMix and Glossy
        self.nodeLinks.new(self.shaMx2.outputs[0], self.shaMx1.inputs[1])
        self.nodeLinks.new(self.shGls1.outputs[0], self.shaMx1.inputs[2])
        self.shaMx1.inputs[0].default_value = .05
        # Output
        self.nodeLinks.new(self.shaMx1.outputs[0], self.shaOut.inputs[0])
        self.nodeLinks.new(self.mathMl.outputs[0], self.shaOut.inputs[2])
        
        return self.selMats
    

    def makeEyes(self, surfType):
        if surfType[5:] == 'Trn':
            # Glossy
            self.shGls1.inputs[1].default_value = .2
            # Glass
            self.shaGla.inputs[1].default_value = .001
            self.shaGla.inputs[2].default_value = 1.2

            self.shGls1.location = -200, 300
            self.shaGla.location = -200, 150
            self.shaTra.location = 0, 300
            self.shaMx2.location = 0, 200
            self.shaMx1.location = 200, 300
            self.shaOut.location = 400, 300

            # Mixing Glass and Glossy
            self.nodeLinks.new(self.shGls1.outputs[0], self.shaMx2.inputs[1])
            self.nodeLinks.new(self.shaGla.outputs[0], self.shaMx2.inputs[2])
            self.shaMx2.inputs[0].default_value = .065
            # Mixing Glass/Glossy and Tansparent
            self.nodeLinks.new(self.shaTra.outputs[0], self.shaMx1.inputs[1])
            self.nodeLinks.new(self.shaMx2.outputs[0], self.shaMx1.inputs[2])
            self.shaMx1.inputs[0].default_value = .13
            # Output
            self.nodeLinks.new(self.shaMx1.outputs[0], self.shaOut.inputs[0])
            return self.selMats

        if surfType[5:] == 'Clr':
            self.shaGla.inputs[1].default_value = .001
            self.shaGla.inputs[2].default_value = 1.2

            self.shaTcd.location = -950, 300
            self.shaMap.location = -750, 300
            self.TexCol.location = -200, 300
            self.shaGla.location = 0, 150
            self.shDif1.location = 0, 300
            self.shaMx1.location = 200, 300
            self.shaOut.location = 400, 300
            self.nodeLinks.new(self.shaTcd.outputs[2], self.shaMap.inputs[0])
            self.nodeLinks.new(self.shaMap.outputs[0], self.TexCol.inputs[0])
            self.nodeLinks.new(self.TexCol.outputs[0], self.shDif1.inputs[0])
            # Mixing colourMap with Glass
            self.nodeLinks.new(self.shDif1.outputs[0], self.shaMx1.inputs[1])
            self.nodeLinks.new(self.shaGla.outputs[0], self.shaMx1.inputs[2])
            self.shaMx1.inputs[0].default_value = .065
            # Output
            self.nodeLinks.new(self.shaMx1.outputs[0], self.shaOut.inputs[0])
            return self.selMats

        if surfType[5:] == 'Lash':
            self.shaTcd.location = -950, 300
            self.shaMap.location = -750, 300
            self.TexCol.location = -200, 300
            self.shaTra.location = 0, 300
            self.shDif1.location = 0, 150
            self.shaMx1.location = 200, 300
            self.shaOut.location = 400, 300
            self.nodeLinks.new(self.shaTcd.outputs[2], self.shaMap.inputs[0])
            self.nodeLinks.new(self.shaMap.outputs[0], self.TexCol.inputs[0])
            self.nodeLinks.new(self.TexCol.outputs[0], self.shDif1.inputs[0])
            # Eyelash transmap using .PNG file
            self.nodeLinks.new(self.TexCol.outputs[1], self.shaMx1.inputs[0])
            self.nodeLinks.new(self.shaTra.outputs[0], self.shaMx1.inputs[1])
            self.nodeLinks.new(self.shDif1.outputs[0], self.shaMx1.inputs[2])
            # Output
            self.nodeLinks.new(self.shaMx1.outputs[0], self.shaOut.inputs[0])
            return self.selMats


    def makeMouth(self):
        self.shDif1.inputs[1].default_value = .3
        self.shaMx1.inputs[0].default_value = .164

        self.shaTcd.location = -950, 300
        self.shaMap.location = -750, 300
        self.TexCol.location = -200, 300
        self.shGls1.location = 0, 150
        self.shDif1.location = 0, 300
        self.shaMx1.location = 200, 300
        self.shaOut.location = 400, 300
        self.nodeLinks.new(self.shaTcd.outputs[2], self.shaMap.inputs[0])
        self.nodeLinks.new(self.shaMap.outputs[0], self.TexCol.inputs[0])
        self.nodeLinks.new(self.TexCol.outputs[0], self.shDif1.inputs[0])
        # Mixing colourMap with Glass
        self.nodeLinks.new(self.shDif1.outputs[0], self.shaMx1.inputs[1])
        self.nodeLinks.new(self.shGls1.outputs[0], self.shaMx1.inputs[2])
        self.shaMx1.inputs[0].default_value = .065
        # Output
        self.nodeLinks.new(self.shaMx1.outputs[0], self.shaOut.inputs[0])
        return self.selMats

# --== End of Class buildShader() ==--

