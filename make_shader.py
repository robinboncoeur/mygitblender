# ---------------------------------------------------------------------
# File: make_shader.py
# ---------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License or (your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ***** END GPL LICENCE BLOCK *****

import bpy
from bpy_extras.io_utils import ImportHelper
from __main__ import *

class BuildShader():
  def __init__(self, cSelObj, cRegion, ImgClr = None):
    self.Region = cRegion
    self.ImgCol = ImgClr
    self.valCoo = 2 if ImgClr else 0
    self.shPrin = ""
    self.matOut = ""
    self.shImag = ""
    self.shClrMix = ""
    self.shVCRamp = ""
    self.rampMixr = ""

    self.f_tools = bpy.context.scene.ob_fig_tools
    self.sSlctdObj = cSelObj
    self.sSlctdSdr = self.f_tools.sSelShader
    self.shvsssval = self.f_tools.fp_sssval
    self.shvsssrad = self.f_tools.fp_sssrad
    self.shvspcamt = self.f_tools.fp_spcamt
    self.shvspcruf = self.f_tools.fp_spcruf
    self.shvsheenv = self.f_tools.fp_sheenv
    self.shviorval = self.f_tools.fp_iorval

    self.sSlctdObj.select = True
    self.selMats = self.sSlctdObj.active_material
    self.selMats.use_nodes = True
    self.treeNodes = self.selMats.node_tree
    self.nodeLinks = self.treeNodes.links
    self.nodes = {}

    """ First, clear all existing nodes in material list """
    for n in self.treeNodes.nodes:
      self.treeNodes.nodes.remove(n)

    """ Second, run script to create material node sets """
    if self.sSlctdSdr == "SimpleS":
      pass
    else:
      #bpy.ops.system.message('INVOKE_DEFAULT',
      #  type = "Error",
      #  message = "200-The current figure is: " + self.f_tools.curFigEnum,
      #  )
      self.buildShaderset(ImgClr)



  """ ================================
  ===> All node-builder functions <===
  ================================ """
  def addRGBMix(self, ptX, ptY, nClamp, flFactor, mixType):
    """ adds an RGBMix node """
    nodeRGB = self.treeNodes.nodes.new("ShaderNodeMixRGB")
    nodeRGB.location = (ptX, ptY)
    self.nodes["RGB Mix"] = nodeRGB
    nodeRGB.blend_type = mixType
    nodeRGB.inputs[0].default_value = flFactor
    nodeRGB.label = "Mix RGB"
    return nodeRGB

  def addColorRamp(self, ptX, ptY, cRClrA, cRClrB, cRClrC, cRPosA, cRPosB=0, cRPosC=0, cMode=None, Interp=None):
    """ adds an ColorRamp node """
    nodeClrRamp = self.treeNodes.nodes.new("ShaderNodeValToRGB")
    nodeClrRamp.location = (ptX, ptY)
    self.nodes["ColorRamp"] = nodeClrRamp
    nodeClrRamp.color_ramp.elements[0].position = cRPosA
    nodeClrRamp.color_ramp.elements[0].color = cRClrA
    nodeClrRamp.color_ramp.elements[1].position = cRPosB
    nodeClrRamp.color_ramp.elements[1].color = cRClrB
    if (cRPosC > 0):
      nodeClrRamp.color_ramp.elements.new(2)
      nodeClrRamp.color_ramp.elements[2].position = cRPosC
      nodeClrRamp.color_ramp.elements[2].color = cRClrC
    return nodeClrRamp

  def addNoise(self, ptX, ptY, flScale, flDetail, flDistortion):
    """ adds a Noise node """
    nodeNoise = self.treeNodes.nodes.new("ShaderNodeTexNoise")
    nodeNoise.location = (ptX, ptY)
    self.nodes["Tex Noise"] = nodeNoise
    nodeNoise.inputs[1].default_value = flScale
    nodeNoise.inputs[2].default_value = flDetail
    nodeNoise.inputs[3].default_value = flDistortion
    nodeNoise.label = "Noise"
    return nodeNoise

  def addVoronoi(self, ptX, ptY, flColoring):
    """ adds a Voronoi node: intColoring range 0 - 1 """
    nodeVoro = self.treeNodes.nodes.new("ShaderNodeTexVoronoi")
    nodeVoro.location = (ptX, ptY)
    self.nodes["Voronoi"] = nodeVoro
    #nodeVoro.inputs[0].default_value = flColoring
    nodeVoro.label = "Voronoi"
    return nodeVoro

  def addTexcoordMap(self, coordOut, ptX, ptY, mName):
    """ add a texture coordinate and mapping nodes """
    texCoord = self.treeNodes.nodes.new("ShaderNodeTexCoord")
    texCoord.location = (ptX, ptY)
    self.nodes["Tex Coord"] = texCoord
    mapping = self.treeNodes.nodes.new("ShaderNodeMapping")
    mapping.location = (ptX + 175, ptY)
    mapping.name = mName
    self.nodes["Mapping"] = mapping
    self.nodeLinks.new(texCoord.outputs[coordOut], mapping.inputs[0])
    return mapping

  def addImageTex(self, texImg, ptX, ptY, nodeName):
    """add an image texture node"""
    imageTexture = self.treeNodes.nodes.new("ShaderNodeTexImage")
    imageTexture.image = texImg
    imageTexture.location = (ptX, ptY)
    imageTexture.label = nodeName
    return imageTexture

  def addBump(self, ptX, ptY, flStrength, flDistance):
    nodeBump = self.treeNodes.nodes.new("ShaderNodeBump")
    nodeBump.location = (ptX, ptY)
    nodeBump.inputs[0].default_value = flStrength
    nodeBump.inputs[1].default_value = flDistance
    nodeBump.label = "Bumps"
    return nodeBump

  def addshMix(self, ptX, ptY, flFactor=None):
    nodeshMix = self.treeNodes.nodes.new("ShaderNodeMixShader")
    nodeshMix.location = (ptX, ptY)
    nodeshMix.inputs['Fac'].default_value = flFactor if (flFactor) else .5
    nodeshMix.label = "Mix Shader"
    return nodeshMix

  def addshDiffuse(self, ptX, ptY, flRoughness=None, tupColor=None):
    nodeshDiff = self.treeNodes.nodes.new("ShaderNodeBsdfDiffuse")
    nodeshDiff.location = (ptX, ptY)
    nodeshDiff.inputs['Color'].default_value = tupColor if (tupColor) else (1, 1, 1, 1)
    nodeshDiff.inputs['Roughness'].default_value = flRoughness if (flRoughness) else 0
    nodeshDiff.label = "Diffuse BSDF"
    return nodeshDiff

  def addshGloss(self, ptX, ptY, flRoughness=None, tupColor=None):
    nodeshGloss = self.treeNodes.nodes.new("ShaderNodeBsdfGlossy")
    nodeshGloss.location = (ptX, ptY)
    nodeshGloss.inputs[0].default_value = tupColor if (tupColor) else (1, 1, 1, 1)
    nodeshGloss.inputs[1].default_value = flRoughness if (flRoughness) else 0
    nodeshGloss.label = "Glossy BSDF"
    return nodeshGloss

  def addshTrans(self, ptX, ptY, tupColor=None):
    nodeshTrans = self.treeNodes.nodes.new("ShaderNodeBsdfTransparent")
    nodeshTrans.location = (ptX, ptY)
    nodeshTrans.label = "TransMap"
    return nodeshTrans



  def makeSkin(self):
    # TexCoord -> Mapping ->
    shUVCo = self.addTexcoordMap(2, -1250, 350, "ClrMap")
    ImgFileName = self.ImgCol
    # -> Image Texture ->
    self.shImag = self.addImageTex(ImgFileName, -725, 350, "ClrTex")
    self.nodeLinks.new(shUVCo.outputs[0], self.shImag.inputs[0])
    # -> RGBMix -> principledShader
    self.shClrMix = self.addRGBMix(-75, 200, 0, .1, 'MIX')
    self.nodeLinks.new(self.shImag.outputs[0], self.shClrMix.inputs[1])
    self.nodeLinks.new(self.shClrMix.outputs[0], self.shPrin.inputs[0])

    # TexCoord -> Mapping -> Noise
    shNoUV = self.addTexcoordMap(0, -1250, 0, "TexMap")
    shNoise = self.addNoise(-725, 0, 15.000, 5.000, 0.00)
    self.nodeLinks.new(shNoUV.outputs[0], shNoise.inputs[0])
    # TexCoord -> Mapping -> Voronoi ->
    shVoron = self.addVoronoi(-725, -175, 1)
    self.nodeLinks.new(shNoUV.outputs[0], shVoron.inputs[0])
    # -> ColorRamps ->
    # colour settings (craClr=colorramp color, crPosn=colo position)
    craClr01 = (.18, .02, .01, 1)
    craClr02 = (.6, .25, .12, 1)
    craClr03 = (1.0, .47, .22, 1)
    crPosn01 = (0)
    crPosn02 = (.07)
    crPosn03 = (.5)
    self.shVCRamp = self.addColorRamp(-550, -175, craClr01, craClr02, craClr03, crPosn01, crPosn02, crPosn03)
    self.nodeLinks.new(shVoron.outputs[0], self.shVCRamp.inputs[0])
    craClr01 = (.51, .09, .04, 1)
    craClr02 = (.58, .18, .06, 1)
    craClr03 = (.6, .25, .12, 1)
    crPosn01 = (0)
    crPosn02 = (1)
    crPosn03 = (.5)
    shCrRamp = self.addColorRamp(-550, 50, craClr01, craClr02, 0, crPosn01, crPosn02, 0)
    self.nodeLinks.new(shNoise.outputs[0], shCrRamp.inputs[0])
    # mix ColorRamps
    self.rampMixr = self.addRGBMix(-250, 200, 0, .5, 'MIX')
    self.nodeLinks.new(shCrRamp.outputs[0], self.rampMixr.inputs[1])
    self.nodeLinks.new(self.shVCRamp.outputs[0], self.rampMixr.inputs[2])
    # RampMixes -> ColorMix -> Principled
    self.nodeLinks.new(self.rampMixr.outputs[0], self.shClrMix.inputs[2])

    # SubSurface Colour
    # Noise -> ColorRamp
    shNoise = self.addNoise(-550, 450, 20.000, 5.000, 0.00)
    craClr01 = (.59, .13, .19, 1)
    craClr02 = (1, .12, .09, 1)
    craClr03 = (.6, .25, .12, 1)
    crPosn01 = (0)
    crPosn02 = (1)
    crPosn03 = (.5)
    shCrRamp = self.addColorRamp(-250, 450, craClr01, craClr02, 0, crPosn01, crPosn02, 0)
    self.nodeLinks.new(shNoise.outputs[0], shCrRamp.inputs[0])
    self.nodeLinks.new(shCrRamp.outputs[0], self.shPrin.inputs[3])

    # Sheen
    shNoise = self.addNoise(-550, 275, 120.000, 25.000, 120.00)
    self.nodeLinks.new(shNoise.outputs[0], self.shPrin.inputs[10])

    # Bump
    shBump = self.addBump(-75, -225, .06, .01)
    self.nodeLinks.new(self.shVCRamp.outputs[0], shBump.inputs[2])
    self.nodeLinks.new(shBump.outputs[0], self.shPrin.inputs[17])

    # Roughness
    craClr01 = (1, 1, 1, 1)
    craClr02 = (0, 0, 0, 1)
    craClr03 = (0, 0, 0, 1)
    crPosn01 = (0)
    crPosn02 = (.45)
    crPosn03 = (.5)
    shCrRamp = self.addColorRamp(-250, 0, craClr01, craClr02, craClr03, crPosn01, crPosn02, crPosn03)
    self.nodeLinks.new(self.shVCRamp.outputs[0], shCrRamp.inputs[0])
    self.nodeLinks.new(shCrRamp.outputs[0], self.shPrin.inputs[6])


  def makeMouth(self):
    shUVCo = self.addTexcoordMap(2, -950, 350, "ClrMap")
    ImgFileName = self.ImgCol
    self.shImag = self.addImageTex(ImgFileName, -425, 350, "Color Map")
    self.nodeLinks.new(shUVCo.outputs[0], self.shImag.inputs[0])
    self.nodeLinks.new(self.shImag.outputs[0], self.shPrin.inputs[0])
    self.nodeLinks.new(self.shPrin.outputs[0], self.matOut.inputs[0])


  def makeEyes(self, surfType):
    if surfType[5:] == 'Trn':
      shTrn = self.addshTrans(-450, 350)
      shGlo = self.addshGloss(-450, 200, .002)
      shMix = self.addshMix(-200, 350, .93)
      self.nodeLinks.new(shGlo.outputs[0], shMix.inputs[1])
      self.nodeLinks.new(shTrn.outputs[0], shMix.inputs[2])
      self.nodeLinks.new(shMix.outputs[0], self.matOut.inputs[0])

    if surfType[5:] == 'Clr':
      self.shPrin = self.treeNodes.nodes.new("ShaderNodeBsdfPrincipled")
      self.shPrin.location = (100, 250)
      self.nodes["Principled"] = self.shPrin
      self.treeNodes.links.new(self.shPrin.outputs[0], self.matOut.inputs[0])
      # Specular
      self.shPrin.inputs[5].default_value = .6
      # roughness
      self.shPrin.inputs[7].default_value = .001
      #
      self.shPrin.inputs[11].default_value = .2
      self.shPrin.inputs[14].default_value = 1.33
      shUVCo = self.addTexcoordMap(2, -950, 350, "ClrMap")
      ImgFileName = self.ImgCol
      self.shImag = self.addImageTex(ImgFileName, -425, 350, "Color Map")
      self.nodeLinks.new(shUVCo.outputs[0], self.shImag.inputs[0])
      self.nodeLinks.new(self.shImag.outputs[0], self.shPrin.inputs[0])
      self.nodeLinks.new(self.shPrin.outputs[0], self.matOut.inputs[0])


    if surfType[5:] == 'Lash':
      shUVCo = self.addTexcoordMap(2, -1250, 350, "TransMap")
      ImgFileName = self.ImgCol
      # -> Image Texture ->
      self.shImag = self.addImageTex(ImgFileName, -725, 350, "TransMap")
      self.nodeLinks.new(shUVCo.outputs[0], self.shImag.inputs[0])
      shTrn = self.addshTrans(-450, 350)
      shDif = self.addshDiffuse(-450, 200)
      shMix = self.addshMix(-200, 350)
      self.nodeLinks.new(self.shImag.outputs[0], shDif.inputs[0])
      self.nodeLinks.new(self.shImag.outputs[1], shMix.inputs[0])
      self.nodeLinks.new(shDif.outputs[0], shMix.inputs[1])
      self.nodeLinks.new(shTrn.outputs[0], shMix.inputs[2])
      self.nodeLinks.new(shMix.outputs[0], self.matOut.inputs[0])


  def buildShaderset(self, image):
    if self.sSlctdSdr == "PrinSSS":
      """
      For skin, mouth, lashes or any node suffixed clr (colour) These are the
      Principled shader, texture coordinate, Mapping and Image Texture nodes.
      Also sets up the DiffuseBSDF node.
      """
      # Create a startup node tree : material output and principled shader
      self.matOut = self.treeNodes.nodes.new("ShaderNodeOutputMaterial")
      self.matOut.location = (100, 450)
      self.nodes["Output"] = self.matOut

      if (self.Region[0:4] == 'Skin' or self.Region == 'Mouth'):
        self.shPrin = self.treeNodes.nodes.new("ShaderNodeBsdfPrincipled")
        self.shPrin.location = (100, 250)
        self.nodes["Principled"] = self.shPrin
        self.treeNodes.links.new(self.shPrin.outputs[0], self.matOut.inputs[0])
        # SSS value - to be reviewed
        self.shPrin.inputs[1].default_value = self.shvsssval
        self.shPrin.inputs[2].default_value = [self.shvsssrad,self.shvsssrad,self.shvsssrad]
        # Specular values
        self.shPrin.inputs[5].default_value = self.shvspcamt
        self.shPrin.inputs[7].default_value = self.shvspcruf
        self.shPrin.inputs[11].default_value = self.shvsheenv
        self.shPrin.inputs[14].default_value = self.shviorval

    # Skin and Eyes mat slot names have _suffixes
    if self.Region[0:4] == 'Skin':
      self.makeSkin()

    if self.Region[0:4] == 'Eyes':
      self.makeEyes(self.Region)

    if self.Region == 'Mouth':
      self.makeMouth()


# --== End of Class buildShader() ==--
