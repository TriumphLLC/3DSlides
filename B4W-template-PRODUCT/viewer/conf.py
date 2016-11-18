#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bpy, bmesh
from math import cos, sin, radians
import math
import blend4web.logic_node_tree as logic
from bpy.props import BoolProperty, IntVectorProperty

from bpy.types import Operator
import mathutils
from mathutils import Vector
import os
import collections
import json
import blend4web.server as server
import blend4web.exporter as exporter
import codecs
from os.path import basename, exists, join, normpath, relpath, abspath, split, isabs
from bpy.props import (StringProperty,
					   BoolProperty,
					   EnumProperty,
					   IntProperty,
					   FloatProperty,
					   CollectionProperty,
					   )

from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy_extras.image_utils import load_image
from bpy_extras.view3d_utils import region_2d_to_location_3d,region_2d_to_vector_3d
from collections import namedtuple




import bpy
import bgl
import blf
import os


from bpy.types import AddonPreferences
from bpy.props import (BoolProperty, EnumProperty,
					   FloatProperty, FloatVectorProperty,
					   IntProperty, StringProperty)

from bpy_extras.io_utils import ImportHelper

from bpy.app.handlers import persistent

 


iconWidth = 100
iconHeight = 100
targetItemWidth = 410
targetItemHeight = 100

contentWidthArea = 700
correct = 50
delta = 0
rows = 1
tmp_mas = []
current_dir_content = []
current_item = {}
redrawFlag = False
export_url = ""
bl_info = {
	"name": "Blend4Web  Configurator" }

class Names(bpy.types.PropertyGroup):
	name = bpy.props.StringProperty(name="")
	
bpy.utils.register_class(Names)

bpy.types.Object.compatiblity_mas = \
	bpy.props.CollectionProperty(type=Names)  

bpy.types.Object.not_compatiblity_mas = \
	bpy.props.CollectionProperty(type=Names)  


bpy.types.Object.exception_materials = \
	bpy.props.CollectionProperty(type=Names)  

bpy.types.Object.material_name = \
	bpy.props.StringProperty(name="", default = "") 


bpy.types.Object.section = \
	bpy.props.StringProperty(name="", default = "") 

bpy.types.Object.user_image = \
	bpy.props.BoolProperty(name="", default = False) 		

bpy.types.Scene.Item = bpy.props.StringProperty(name="")  




bpy.types.Object.origin_position = bpy.props.FloatVectorProperty(
name="",
default=(0.0,)*3,
size=3
)
bpy.types.Object.select_all = bpy.props.BoolProperty(name="Select_all")

bpy.types.Object.title = bpy.props.StringProperty(name="", default = "object_name")

bpy.types.Object.section_type = bpy.props.StringProperty(name="", default = "")

bpy.types.Object.is_material = bpy.props.BoolProperty(
        name="is material",
        description="",
        default = False)

bpy.types.Object.order = bpy.props.IntProperty(name="", default = 0)

bpy.types.Object.compatiblity = \
	bpy.props.BoolProperty(default=False) 

paths = bpy.utils.script_paths("addons")

# libraryPath = 'assets'
# for path in paths:
#	 libraryPath = os.path.join(path, "add_mesh_asset_flinger")
#	 if os.path.exists(libraryPath):
#		 break

# if not os.path.exists(libraryPath):
#	 raise NameError('Did not find assets path from ' + libraryPath)

# libraryIconsPath = os.path.join(libraryPath, "icons")
# libraryDefaultModelsPath = os.path.join(libraryPath, "assets")

@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)

bpy.app.handlers.load_post.append(load_handler)


def get_objects_material_color(ob):
	color =""
	mat_name = ""
	if(len(ob.data.materials) > 0 ):
		mat = ob.data.materials[0]
		for n in mat.node_tree.nodes:
			if(n.type == "RGB"):
				color = (n.outputs[0].default_value[0],n.outputs[0].default_value[1],n.outputs[0].default_value[2])
				mat_name = mat.name
	return color,mat_name			

	

def dump3(ob,ind,s_type):
	global export_url

	color = ""
	material_name = ""
	names = []
	for s in ob.not_compatiblity_mas:
		names.append(s.name)

	materials = []
	for s in ob.exception_materials:
		materials.append(s.name)	
	imgpath = ""	
	if(export_url != ""):
		for img in bpy.data.images:
			if(img.name == ob.name+'_.jpg'):
				img.filepath_raw = export_url+ob.name+'.png'
				img.file_format = 'PNG'
				img.save()
				imgpath = ob.name+'.png'
	default = False
	
	if(s_type == "material"):
		color,_ = get_objects_material_color(ob)
	

	if ind == 0 and s_type != "material":
		default = True	

	title_text = ""	
	if(ob.title == "object_name"):
		title_text = ob.name
	else:
		title_text = ob.title				

	return  {'name': ob.name, 'user_image':ob.user_image, 'default': default, 'color':color, 'title':title_text, 'exceptions':{"objects":tuple(names),'materials':tuple(materials)}, 'img': imgpath}

def dump(ob):
	#['foo', {'bar': ('baz', None, 1.0, 2)}]
	#section_items = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == ob.name.split("_")[1] and len(c.name.split(".")) < 2) ]
	
	section_items = [c for c in bpy.data.objects if(c.section == ob.name and len(c.name.split('.')) < 2)  ]

	#section_items = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == s.name.split("_")[1] and c.name != bpy.context.scene.Item) ]


	print('section_items',section_items,tuple(section_items))
	s_type = ""
	
	material_name = ""
	if(ob.is_material):
		s_type = "material" 
		material_name = ob.material_name
		
	
	return  {'name': ob.name,'title':str(ob.title),'material_name':material_name,  'type':s_type, 'items': [dump3(s,ind,s_type) for ind,s in enumerate(section_items)]}

def SortSections(s):
	return s.order

def drawMenuItem(item, x, y, width, height):
	global iconWidth
	global iconHeight
	global delta

	

	y = y + delta

	iconMarginX = 4
	iconMarginY = 4
	textMarginX = 6

	textHeight = 16
	textWidth = 72

	bgl.glEnable(bgl.GL_BLEND)
	# if item['highlighted']:
	# 	bgl.glColor4f(0.555, 0.555, 0.555, 0.8)
	# else:
	if('empty' in item):
		bgl.glColor4f(0, 0, 0, 0.1)
	else:	
		if item['selected']:
			bgl.glColor4f(0.555, 0.555, 0.555, 0.8)
		else:	
			bgl.glColor4f(0.447, 0.447, 0.447, 0.8)

	bgl.glRectf(x, y, x + width, y + height)

	if('empty' in item):
		pass
	else:	
		texture = item['icon']
		texture.gl_load()
		bgl.glColor4f(0.0, 0.0, 1.0, 0.5)
		#bgl.glLineWidth(1.5)

		#------ TEXTURE ---------#
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
		bgl.glEnable(bgl.GL_TEXTURE_2D)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

		bgl.glColor4f(1,1,1,1)
		bgl.glBegin(bgl.GL_QUADS)
		bgl.glTexCoord2d(0,0)
		bgl.glVertex2d(x , y)
		bgl.glTexCoord2d(0,1)
		bgl.glVertex2d(x , y + iconHeight)
		bgl.glTexCoord2d(1,1)
		bgl.glVertex2d(x  + iconWidth, y + iconHeight)
		bgl.glTexCoord2d(1,0)
		bgl.glVertex2d(x  + iconWidth , y)
		bgl.glEnd()

		texture.gl_free()

	if('accept' in item):
		texture = item['accept']
		texture.gl_load()
		bgl.glColor4f(0.0, 0.0, 1.0, 0.5)
		#bgl.glLineWidth(1.5)

		#------ TEXTURE ---------#
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
		bgl.glEnable(bgl.GL_TEXTURE_2D)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

		bgl.glColor4f(1,1,1,1)
		bgl.glBegin(bgl.GL_QUADS)
		bgl.glTexCoord2d(0,0)
		bgl.glVertex2d(x  + width - 40, y + height - 35)
		bgl.glTexCoord2d(0,1)
		bgl.glVertex2d(x   + width - 40,y+ height - 5)
		bgl.glTexCoord2d(1,1)
		bgl.glVertex2d(x   + width - 10, y + height - 5)
		bgl.glTexCoord2d(1,0)
		bgl.glVertex2d(x   + width - 10 , y + height - 35)
		bgl.glEnd()

		texture.gl_free()	

	if('main' in item):
		texture = item['back']
		texture.gl_load()
		bgl.glColor4f(0.0, 0.0, 1.0, 0.5)
		#bgl.glLineWidth(1.5)

		#------ TEXTURE ---------#
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
		bgl.glEnable(bgl.GL_TEXTURE_2D)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

		bgl.glColor4f(1,1,1,1)
		bgl.glBegin(bgl.GL_QUADS)
		bgl.glTexCoord2d(0,0)
		bgl.glVertex2d(x  + width - 40, y + height - 35)
		bgl.glTexCoord2d(0,1)
		bgl.glVertex2d(x   + width - 40,y+ height - 5)
		bgl.glTexCoord2d(1,1)
		bgl.glVertex2d(x   + width - 10, y + height - 5)
		bgl.glTexCoord2d(1,0)
		bgl.glVertex2d(x   + width - 10 , y + height - 35)
		bgl.glEnd()

		texture.gl_free()		


	if(not item['isUPFolder'] and not item['Addbutton'] and not 'accept' in item and not 'back' in item):
		if(not 'empty' in item):
			texture = item['menu']
			texture.gl_load()
			bgl.glColor4f(0.0, 0.0, 1.0, 0.5)
			#bgl.glLineWidth(1.5)

			#------ TEXTURE ---------#
			bgl.glEnable(bgl.GL_BLEND)
			bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
			bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
			bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
			bgl.glEnable(bgl.GL_TEXTURE_2D)
			bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

			bgl.glColor4f(1,1,1,1)
			bgl.glBegin(bgl.GL_QUADS)
			bgl.glTexCoord2d(0,0)
			bgl.glVertex2d(x  + width - 40, y + height - 30)
			bgl.glTexCoord2d(0,1)
			bgl.glVertex2d(x   + width - 40,y+ height - 70)
			bgl.glTexCoord2d(1,1)
			bgl.glVertex2d(x   + width - 10, y + height - 70)
			bgl.glTexCoord2d(1,0)
			bgl.glVertex2d(x   + width - 10 , y + height - 30)
			bgl.glEnd()

			texture.gl_free()

	# draw some text
	font_id = 0
	if('title' in item):
		if(item['title'] == 'object_name'):
			length = len(item['text'])
			text = item['text']
		else:
			length = len(item['title'])
			text = item['title']
	else:
		length = 0


	if('empty' in item):
		bgl.glColor4f(1,1,1,1)
		blf.position(font_id, x + iconMarginX  + textMarginX, y + iconHeight * 0.5 - 0.25 * textHeight, 0)
		blf.size(font_id, textHeight, textWidth)
		if('title' in item):
			if(item['title'] == 'object_name'):
				blf.draw(font_id, item['text'])
			else:
				blf.draw(font_id, item['title'])
		else:
			blf.draw(font_id, item['text'])		
	else:				

		if(length > 11):
			split = text.split(' ')
			

			# for s in split:
			# 	if(len(s) > 11)
			if(len(split) > 1):
				str1 = split[0]
				str2 = split[1]

				
				blf.position(font_id, x + iconMarginX + iconWidth + textMarginX, y + iconHeight * 0.5 - 0.25 * textHeight, 0)
				blf.size(font_id, textHeight, textWidth)
				if('title' in item):
					if(item['title'] == 'object_name'):
						blf.draw(font_id, str1)
					else:
						blf.draw(font_id, str1)
				else:
					blf.draw(font_id, item['text'])	

				blf.position(font_id, x + iconMarginX + iconWidth + textMarginX, y + iconHeight * 0.5 - 0.25 * textHeight - textHeight, 0)
				blf.size(font_id, textHeight, textWidth)
				if('title' in item):
					if(item['title'] == 'object_name'):
						blf.draw(font_id, str2)
					else:
						blf.draw(font_id, str2)
				else:
					blf.draw(font_id, item['text'])					
			else:
				blf.position(font_id, x + iconMarginX + iconWidth + textMarginX, y + iconHeight * 0.5 - 0.25 * textHeight, 0)
				blf.size(font_id, textHeight, textWidth)
				if('title' in item):
					if(item['title'] == 'object_name'):
						blf.draw(font_id, item['text'])
					else:
						blf.draw(font_id, item['title'])
				else:
					blf.draw(font_id, item['text'])						
					
		else:	

			blf.position(font_id, x + iconMarginX + iconWidth + textMarginX, y + iconHeight * 0.5 - 0.25 * textHeight, 0)
			blf.size(font_id, textHeight, textWidth)
			if('title' in item):
				if(item['title'] == 'object_name'):
					blf.draw(font_id, item['text'])
				else:
					blf.draw(font_id, item['title'])
			else:
				blf.draw(font_id, item['text'])				

def drawCallbackMenu(self, context):

	global targetItemWidth
	global targetItemHeight
	global delta
	global correct
	global redrawFlag
	global current_dir_content
	global contentWidthArea,rows

	# if(redrawFlag):
	# 	redrawFlag = False
	# 	self.redraw()
		

	# else:	

	marginX = 20
	marginY = 5
	paddingX = 5
	Ho = len(current_dir_content) * (targetItemHeight + marginY) / rows + 50
	contentHeight = context.area.regions[4].height - 5 * 2

	#X0 = contentWidthArea/2
	X0 = 0
	Y0 = 0

	bgl.glEnable(bgl.GL_BLEND)
	bgl.glColor4f(0.0, 0.0, 0.0, 0.6)
	bgl.glRectf(X0,Y0,(contentWidthArea+ marginX * 3 - correct)/2,context.area.regions[4].height)

	contentWidth = (contentWidthArea - marginX * 2  - correct)/2
	contentHeight = context.area.regions[4].height - marginY * 2

	contentX =  marginX
	contentY = context.area.height - marginY - targetItemHeight - 50

	colCount = int(contentWidth / targetItemWidth)

	itemWidth = (contentWidth - (colCount * paddingX)) / (colCount + 1)
	itemHeight = targetItemHeight



	#------ TEXTURE SCROL---------#
	if(Ho > contentHeight):
		texture = bpy.data.images["scroll.png"]
		texture.gl_load() 
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
		bgl.glEnable(bgl.GL_TEXTURE_2D)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

		bgl.glColor4f(1,1,1,1)
		bgl.glBegin(bgl.GL_QUADS)
		bgl.glTexCoord2d(0,0)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2, Y0 + 10)
		bgl.glTexCoord2d(0,1)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2, Y0 + contentHeight )
		bgl.glTexCoord2d(1,1)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2 + 50, Y0 + contentHeight )
		bgl.glTexCoord2d(1,0)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2 + 50 , Y0 + 10)
		bgl.glEnd()

		texture.gl_free()

		#------ TEXTURE SCROL TOOL---------#


		scrollPercent = 1 - delta / (Ho - contentHeight)
		texture = bpy.data.images["scroll_tool.png"]
		texture.gl_load() 
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
		bgl.glEnable(bgl.GL_TEXTURE_2D)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

		bgl.glColor4f(1,1,1,1)
		bgl.glBegin(bgl.GL_QUADS)
		bgl.glTexCoord2d(0,0)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2, Y0 -35 + scrollPercent * (contentHeight - 80) + 45 )
		bgl.glTexCoord2d(0,1)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2, Y0 +35 + scrollPercent * (contentHeight - 80) + 45)
		bgl.glTexCoord2d(1,1)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2 + 50, Y0  +35 + scrollPercent * (contentHeight - 80) + 45 )
		bgl.glTexCoord2d(1,0)
		bgl.glVertex2d(X0 + contentWidth+ marginX/2 + 50 , Y0 -35 + scrollPercent * (contentHeight - 80) + 45 )
		bgl.glEnd()

		texture.gl_free()

	 #------ TEXTURE ---------#

	
	#------ TEXTURE SCROL TOOL---------#


	texture = bpy.data.images["resize.png"]
	texture.gl_load() 
	bgl.glEnable(bgl.GL_BLEND)
	bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode[0])
	bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
	bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images
	bgl.glEnable(bgl.GL_TEXTURE_2D)
	bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

	bgl.glColor4f(1,1,1,1)
	bgl.glBegin(bgl.GL_QUADS)
	bgl.glTexCoord2d(0,0)
	bgl.glVertex2d(X0 + contentWidth + marginX + 20, Y0 +contentHeight/2 )
	bgl.glTexCoord2d(0,1)
	bgl.glVertex2d(X0 + contentWidth+ marginX + 20, Y0 +contentHeight/2 + 20)
	bgl.glTexCoord2d(1,1)
	bgl.glVertex2d(X0 + contentWidth+ marginX + 30,Y0 +contentHeight/2 + 20 )
	bgl.glTexCoord2d(1,0)
	bgl.glVertex2d(X0 + contentWidth+ marginX + 30 ,  Y0 +contentHeight/2)
	bgl.glEnd()

	texture.gl_free() 

	col = 0
	row = 0
	x = contentX
	y = contentY


	if len(current_dir_content ) == 0:
		font_id = 0
		text = "Folder doesn't contain any assets!"
		bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
		blf.size(font_id, 20, 72)
		textWidth, textHeight = blf.dimensions(font_id, text)
		blf.position(font_id, contentX + contentWidth * 0.5 - textWidth * 0.5, contentY - contentHeight * 0.5 + textHeight * 0.5, 0)
		blf.draw(font_id, text)
	else:
		for item in current_dir_content:
			if self.mouseX > x and self.mouseX < x + itemWidth and self.mouseY -delta > y and self.mouseY- delta < y + itemHeight:
				item['highlighted'] = True
			else:
				item['highlighted'] = False

			drawMenuItem(item, x, y, itemWidth, itemHeight)
			x = x + itemWidth + paddingX
			col += 1

			if col > colCount:
				col = 0
				x = contentX
				y = y - itemHeight - marginY
				row += 1

	bgl.glDisable(bgl.GL_BLEND)
	bgl.glDisable(bgl.GL_TEXTURE_2D)
	#bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

def getClicked(self, context):


	global targetItemWidth
	global targetItemHeight
	global correct
	global current_dir_content
	global contentWidthArea

	marginX = 20
	marginY = 5
	paddingX = 5


	contentWidth = (contentWidthArea - marginX * 2 - correct)/2
	contentHeight = context.area.regions[4].height - marginY * 2

	contentX = marginX
	contentY = context.area.height - marginY - targetItemHeight - 50

	colCount = int(contentWidth / targetItemWidth)

	itemWidth = (contentWidth - (colCount * paddingX)) / (colCount + 1)
	itemHeight = targetItemHeight

	col = 0
	row = 0
	x = contentX
	y = contentY
	X0 = 0 
	Y0 = 0

	for item in current_dir_content:
		if self.mouseX > X0 + contentWidth+ marginX/2 and self.mouseX < X0 + contentWidth+ marginX/2 + 50 and self.mouseY > Y0 + 10 and self.mouseY < Y0 + contentHeight:
			return (item,'scroll')

		if self.mouseX > x + itemWidth - 40 and self.mouseX < x + itemWidth -10 and self.mouseY -delta > y + itemHeight - 70 and self.mouseY -delta < y + itemHeight - 30:
			return (item,'menu')

		if self.mouseX > x + itemWidth - 40 and self.mouseX < x + itemWidth -10 and self.mouseY -delta > y + itemHeight - 35 and self.mouseY -delta < y + itemHeight - 5:
			return (item,'accept')	

		if self.mouseX > x  and self.mouseX < x + iconWidth  and self.mouseY -delta > y  and self.mouseY -delta < y + iconHeight:
			return (item,'icon')		

			

		if self.mouseX > x and self.mouseX < x + itemWidth and self.mouseY -delta > y and self.mouseY -delta < y + itemHeight:
			return (item,'item')

		x = x + itemWidth + paddingX
		col += 1
		if col > colCount:
			col = 0
			x = contentX
			y = y - itemHeight - marginY
			row += 1
	return (None,None)


def getMoved(self, context):


	global targetItemWidth
	global targetItemHeight
	global correct
	global current_dir_content
	global contentWidthArea

	marginX = 20
	marginY = 5
	paddingX = 5

	X0 = 0 
	Y0 = 0

	# X0 + contentWidth+ marginX/2, Y0 + contentHeight 
	# X0 + contentWidth+ marginX/2, Y0 + 10 
	# X0 + contentWidth+ marginX/2 + 50, Y0 + 10
	# X0 + contentWidth+ marginX/2 + 50 , Y0 + contentHeight

	contentWidth = (contentWidthArea - marginX * 2 - correct)/2
	contentHeight = context.area.regions[4].height - marginY * 2

	contentX = marginX
	contentY = context.area.height - marginY - targetItemHeight - 50

	colCount = int(contentWidth / targetItemWidth)

	itemWidth = (contentWidth - (colCount * paddingX)) / (colCount + 1)
	itemHeight = targetItemHeight

	col = 0
	row = 0
	x = contentX
	y = contentY

	for item in current_dir_content:
		if self.mouseX > X0 + contentWidth+ marginX/2 and self.mouseX < X0 + contentWidth+ marginX/2 + 50 and self.mouseY > Y0 + 10 and self.mouseY < Y0 + contentHeight:
			return (item,'scroll')

		if self.mouseX > x and self.mouseX < x + itemWidth and self.mouseY > y and self.mouseY < y + itemHeight:
			return (item,'item')

		x = x + itemWidth + paddingX
		col += 1
		if col > colCount:
			col = 0
			x = contentX
			y = y - itemHeight - marginY
			row += 1
	return (None,None)	


class ScreenShotClass(bpy.types.Operator):
	bl_idname = "object.screen_shot"
	bl_label = "ScreenShotClass"
	def make_screen(self,ob,section):
		bpy.context.scene.objects.active = ob
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]

		trafaret = bpy.data.objects['trafaret']

		for s in sections:
			section_items = [c for c in bpy.data.objects if(c.section == s.name)  ]
			for si in section_items:
				si.hide_render = True
		ob.select = True
		ob.hide = False
		print('duplicate',ob)
		bpy.ops.object.duplicate()
		obj_copy = bpy.context.selected_objects[0]
		bpy.context.scene.objects.active = obj_copy
	
		obj_copy.hide = False
		obj_copy.hide_render = False
		ob.hide = True
		# Scale uniformly
		obj_copy.select = True

		camera = bpy.data.objects['Camera']
		camera_empty = bpy.data.objects['camera_empty']
		camera_empty_material = bpy.data.objects['camera_empty_material']


	
		camera.rotation_euler = (math.radians(90),math.radians(0),math.radians(90)) 


		#base settings
		base = ""

		for o in bpy.data.objects:
			if(o.name == 'base'):
				base = bpy.data.objects['base']
				base.hide_render = False	

		# base = bpy.data.objects['base']

		print('section.is_material',section.is_material)
		print("base.hide_render",base.hide_render)
		if(section.is_material):
			obj_copy.location = (0,0,2.5)
			camera.location = camera_empty_material.location
			if(base != ""):
				base.hide_render = True
		else:	
			camera.location = camera_empty.location

		if(base != ""):	
			olc = base.data.materials[0].diffuse_intensity
			base.data.materials[0].diffuse_intensity = 0

		#obj_copy settings
		obj_copy.data.materials[0].diffuse_color = (1,1,1)


		folder = bpy.path.abspath("//")


		# if filename:
		bpy.context.scene.render.filepath = os.path.join(folder,ob.name + "_")



		bpy.ops.render.render(write_still = True)	

		iconFile = bpy.context.scene.render.filepath + ".jpg"

		for img in bpy.data.images:
			if(img.name == ob.name + "_"+ ".jpg"):
				img.user_clear()
				if(img.users == 0):
					bpy.data.images.remove(img)

		bpy.data.images.load(filepath = iconFile)
		bpy.data.images[ob.name + "_"+ ".jpg"].use_fake_user = True
		if(base != ""):	
			base.data.materials[0].diffuse_intensity = olc
			base.hide_render = False
		obj_copy.select = True
		bpy.ops.object.delete()

	def execute(self, context):
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section" and not c.is_material)]
		for s in sections:
			section_items = [c for c in bpy.data.objects if(c.section == s.name and len(c.name.split('.')) < 2)  ]	
			for si in section_items:
				self.make_screen(si,s)	


		return {'FINISHED'}   

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir
from os.path import join as pjoin

class PreviewClass(bpy.types.Operator):
	bl_idname = "object.preview_json"
	bl_label = "PreviewClass"
	def execute(self, context):
		
		
		global export_url

		

		folder = bpy.path.abspath("//")
		ADDRESS = 'localhost'
		#port = 6687
		port = bpy.context.user_preferences.addons['blend4web'].preferences.b4w_port_number
		path = bpy.context.user_preferences.addons['blend4web'].preferences.b4w_src_path
		if not exists(path+"/tmp"):
			os.mkdir( path+"/tmp");

		if not exists(path+"/tmp/configurator"):
			os.mkdir( path+"/tmp/configurator");

		export_url = path+"/tmp/configurator/"

		ExportClassGibrid.execute(ExportClassGibrid,context)
		
		bpy.ops.export_scene.b4w_json(filepath=path+"/tmp/configurator/preview.json")
		for tx in bpy.data.texts:
			#if(tx.name == "index.html"):
			string = tx.as_string()

			text_file = codecs.open(path+"/tmp/configurator/"+tx.name, mode="w", encoding="utf-8")
			#text_file = open(path+"/tmp/configurator/"+tx.name, mode ="w", encoding = "utf-8")

			string.encode('UTF-8')
			text_file.write(string)
			text_file.close()

		

		server.B4WLocalServer.open_url("http://" + ADDRESS + ":" + str(port) + "/tmp/configurator/?load=preview.json")
		#bpy.ops.b4w.open_sdk()
		return {'FINISHED'}   

class ExportClassGibrid(bpy.types.Operator):
	bl_idname = "object.export_gibrid_json"
	bl_label = "ExportClassGibrid"
	def execute(self, context):
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]

		#['foo', {'bar': ('baz', None, 1.0, 2)}]

		for o in bpy.data.objects:
			o.select = False


		materials = []
		objects = []
		for s in sections:
			if(s.is_material):
				materials.append(s)
			else:
				objects.append(s)
		section_items_objects_tmp = []	

	

		for o in objects:
			for co in bpy.data.objects:
				#if(co.name.split('_')[0].split('-')[0] == "S" and len(co.name.split('_')[0].split('-')) > 1 and co.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(co.name.split(".")) >= 2):
				if(co.section == o.name and len(co.name.split(".")) > 2):
					section_items_objects_tmp.append(co)
		#section_items_objects_tmp = [co for co in bpy.data.objects if(co.name.split('_')[0].split('-')[0] == "S" and len(co.name.split('_')[0].split('-')) > 1 and co.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(co.name.split(".")) >= 2) ]
			
		


		for so in section_items_objects_tmp:
			
			so.hide = False
			so.select = True
			if(len(so.data.materials) > 0):
				del_mat = so.data.materials[0]
				for m in bpy.data.materials:
					if(m.name == del_mat.name):
						m.user_clear();
						bpy.data.materials.remove(m);	

			bpy.context.scene.objects.active = so
			bpy.ops.object.delete()	
				


		for o in objects:
			#section_items_objects = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(c.name.split(".")) < 2) ]
			section_items_objects = [c for c in bpy.data.objects if(c.section == o.name and len(c.name.split(".")) < 2)  ]	

			print('section_items_objects',section_items_objects)
			for so in section_items_objects:	
				if(len(so.name.split('product_')) > 1):		
					so.name = so.name.split('product_')[1]		
				for m in materials:
					section_items_materials = [c for c in bpy.data.objects if(c.section == m.name and len(m.name.split(".")) < 2)  ]	
					#section_items_materials = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == m.name.split("_")[1] and len(c.name.split(".")) < 2) ]
					ob_mat = section_items_materials[0]
					
					so.hide = False		
					so.select = True		
					

					mat_source = ob_mat.data.materials[0]

				

					# for o in bpy.data.objects:
					# 	if(o.name == so.name+'.'+mat_source.name):
					# 		for obj in bpy.data.objects:
					# 			obj.select = False
					# 		o.select = True
					# 		bpy.ops.object.delete()


					
					
					bpy.context.scene.objects.active = so
					bpy.ops.object.duplicate()
					
					obj_copy = bpy.context.selected_objects[0]
					
					obj_copy.name = so.name+'.'+mat_source.name
					obj_copy.data.materials[0] = mat_source.copy()
					obj_copy.data.materials[0].name = so.name+'.'+mat_source.name
					obj_copy.hide = True
					m.material_name = mat_source.name
			
			
		json_string = json.dumps({"export_wantenger":"false","items":[dump(s) for s in sections]}, indent=2, ensure_ascii=False)
		
		for tx in bpy.data.texts:
			if(tx.name == "conf.json"):
				tx.user_clear()
				bpy.data.texts.remove(tx)

		bpy.ops.text.new()
		text = bpy.data.texts[-1]
		text.name = 'conf.json'


		text.write(json_string)

		for area in bpy.context.screen.areas:
			if area.type == 'TEXT_EDITOR':
				area.spaces[0].text = text	


		# if(ob.hide == True):
		# 	ob.hide = False
		# 	ob.select = True
		# 	bpy.context.scene.objects.active = ob
		# 	bpy.ops.object.duplicate()
		# 	ob.hide == True
		# 	obj_copy = bpy.context.selected_objects[0]

		# 	obj_copy.name = ob.name+'.'+mat_source.name
		# 	obj_copy.data.materials[0] = mat_source.copy()
		# 	obj_copy.data.materials[0].name = ob.name+'.'+mat_source.name
		# 	obj_copy.hide = True		

		return {'FINISHED'} 



class ExportClassGibridWantenger(bpy.types.Operator):
	bl_idname = "object.export_gibrid_json_wantenger"
	bl_label = "ExportClassGibridWantenger"
	def execute(self, context):
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]

		#['foo', {'bar': ('baz', None, 1.0, 2)}]

		for o in bpy.data.objects:

			o.select = False


		materials = []
		objects = []
		for s in sections:
			if(s.is_material):
				materials.append(s)
			else:
				objects.append(s)
		section_items_objects_tmp = []	

	

		for o in objects:
			for co in bpy.data.objects:
				#if(co.name.split('_')[0].split('-')[0] == "S" and len(co.name.split('_')[0].split('-')) > 1 and co.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(co.name.split(".")) >= 2):
				if(co.section == o.name and len(co.name.split(".")) > 2):
					section_items_objects_tmp.append(co)
		#section_items_objects_tmp = [co for co in bpy.data.objects if(co.name.split('_')[0].split('-')[0] == "S" and len(co.name.split('_')[0].split('-')) > 1 and co.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(co.name.split(".")) >= 2) ]
			
		


		for so in section_items_objects_tmp:
				
			so.hide = False
			so.select = True
			if(len(so.data.materials) > 0):
				del_mat = so.data.materials[0]
				for m in bpy.data.materials:
					if(m.name == del_mat.name):
						m.user_clear();
						bpy.data.materials.remove(m);	

			bpy.context.scene.objects.active = so
			bpy.ops.object.delete()	
				


		for o in objects:
			#section_items_objects = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(c.name.split(".")) < 2) ]
			section_items_objects = [c for c in bpy.data.objects if(c.section == o.name and len(c.name.split(".")) < 2)  ]	

			
			for so in section_items_objects:
				if(len(so.name.split('product_')) > 1):		
					so.name = so.name.split('product_')[1]	
				so.name = 'product_'+so.name		
				for m in materials:
					section_items_materials = [c for c in bpy.data.objects if(c.section == m.name and len(m.name.split(".")) < 2)  ]	
					#section_items_materials = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == m.name.split("_")[1] and len(c.name.split(".")) < 2) ]
					ob_mat = section_items_materials[0]
					
					so.hide = False		
					so.select = True		
					

					mat_source = ob_mat.data.materials[0]

				

					# for o in bpy.data.objects:
					# 	if(o.name == so.name+'.'+mat_source.name):
					# 		for obj in bpy.data.objects:
					# 			obj.select = False
					# 		o.select = True
					# 		bpy.ops.object.delete()


					
					
					bpy.context.scene.objects.active = so
					bpy.ops.object.duplicate()
					
					obj_copy = bpy.context.selected_objects[0]
					# print('obj_copy.name',obj_copy.name)
					# print('obj_copy.name',len(obj_copy.name.split('product_')[1]))
					
					# if(len(obj_copy.name.split('product_')) > 1):		
					# 	obj_copy.name = obj_copy.name.split('product_')[1]
					obj_copy.name = so.name+'.'+mat_source.name
					obj_copy.data.materials[0] = mat_source.copy()
					obj_copy.data.materials[0].name = so.name+'.'+mat_source.name
					obj_copy.hide = True
					m.material_name = mat_source.name
				
				
			
		json_string = json.dumps({"export_wantenger":"true","items":[dump(s) for s in sections]}, indent=2, ensure_ascii=False)
		
		for tx in bpy.data.texts:
			if(tx.name == "conf.json"):
				tx.user_clear()
				bpy.data.texts.remove(tx)

		bpy.ops.text.new()
		text = bpy.data.texts[-1]
		text.name = 'conf.json'


		text.write(json_string)

		for area in bpy.context.screen.areas:
			if area.type == 'TEXT_EDITOR':
				area.spaces[0].text = text	

		bpy.ops.export_scene.b4w_json('INVOKE_DEFAULT')		
		print('export_filepath',dir(exporter))

		print('export_filepath',exporter._export_filepath)


		for tx in bpy.data.texts:
			#if(tx.name == "index.html"):
			if(tx.name == "conf.json"):
				string = tx.as_string()
				if(len(exporter._export_filepath.split('/')) > 1):
					path = exporter._export_filepath.rsplit('/',1)[0]
					print('path',path)
					text_file = codecs.open(path+'/'+tx.name, mode="w", encoding="utf-8")
					#text_file = open(path+"/tmp/configurator/"+tx.name, mode ="w", encoding = "utf-8")

					string.encode('UTF-8')
					text_file.write(string)
					text_file.close()



		# if(ob.hide == True):
		# 	ob.hide = False
		# 	ob.select = True
		# 	bpy.context.scene.objects.active = ob
		# 	bpy.ops.object.duplicate()
		# 	ob.hide == True
		# 	obj_copy = bpy.context.selected_objects[0]

		# 	obj_copy.name = ob.name+'.'+mat_source.name
		# 	obj_copy.data.materials[0] = mat_source.copy()
		# 	obj_copy.data.materials[0].name = ob.name+'.'+mat_source.name
		# 	obj_copy.hide = True		

		return {'FINISHED'} 		

class NewSection(bpy.types.Operator):
	bl_idname = "object.new_section"
	bl_label = "NewSection"
	def execute(self, context):
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		l = len(sections)
		bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.1, view_align=False, location=(0,0,0))
		new_obj = bpy.context.scene.objects.active 
		
		new_obj.name = "Section_"+str(l+1)
		return {'FINISHED'} 

class RenameSection(bpy.types.Operator):
	bl_idname = "object.rename_section"
	bl_label = "RenameSection"

	def execute(self, context):
		for c in bpy.data.objects:
			c.select  = False

		for c in bpy.data.objects:
			if(c.name == bpy.context.scene.Item):
				c.select = True

		bpy.ops.object.title_settings('INVOKE_DEFAULT')

		return {'FINISHED'} 

class DelSection(bpy.types.Operator):
	bl_idname = "object.del_section"
	bl_label = "DelSection"
	
	def execute(self, context):
		global current_dir_content,delta
		for c in bpy.data.objects:
			c.select  = False

		for c in bpy.data.objects:
			if(c.name == bpy.context.scene.Item):
				del_section = c
				del_section.select = True
				bpy.ops.object.delete()

		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		
		newS = [s for s in current_dir_content if(s['text'] != del_section.name)]

		print('JsonManagerMenu.current_dir_content',current_dir_content)
		current_dir_content = newS

		delta = 0

		#JsonManagerMenu.del_section(JsonManagerMenu)
	
		return {'FINISHED'} 

class UploadImage(bpy.types.Operator):
	bl_idname = "object.upload_image"
	bl_label = "UploadImage"
	def execute(self, context):
		#bpy.types.SpaceView3D.draw_handler_remove(JsonManagerMenu._handle, 'WINDOW')					
		bpy.ops.import_image.data('INVOKE_DEFAULT')	

		return {'FINISHED'} 		

class OpenObjectSettings(bpy.types.Operator):
	bl_idname = "object.open_settings"
	bl_label = "OpenObjectSettings"
	
	def execute(self, context):
		global current_dir_content,delta, current_item


		current_dir_content = []
		current_item['main'] = True
		current_item['back'] = bpy.data.images["back.png"]
		
		current_dir_content.append(current_item)

		text_string = {}
		text_string['text'] = "Select compatible elements"
		text_string['title'] = "Select compatible elements"
		text_string['isFolder'] = False
		text_string['isUPFolder'] = False
		text_string['is_material'] = False
		text_string['Addbutton'] = False
		text_string['selected'] = False
		text_string['settings'] = False
		text_string['empty'] = True

		current_dir_content.append(text_string) 
		print('text_string',text_string)	

		sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
		#objs = [ o for o in bpy.data.objects if (o.name.split('-')[0] == 'S')]

		print('sections',sections)
		sections.sort(key=SortSections)

		for num,o in enumerate(sections):
			item = {}
			item['text'] = o.name
			item['title'] = o.title
			item['isFolder'] = True
			item['isUPFolder'] = False
			item['is_material'] = o.is_material == True
			item['Addbutton'] = False
			item['selected'] = False
			item['settings'] = True
			item['settings_item'] = current_item
			o.order = num
			 
			# iconFile = os.path.join(libraryIconsPath, "folder.png")
			# item['icon'] = bpy.data.images.load(filepath = iconFile)
			item['icon'] = bpy.data.images["folder.png"]
			item['menu'] = bpy.data.images["m.png"]
			current_dir_content.append(item) 		

		current_item = {}
		# for c in bpy.data.objects: object_settings
		# 	c.select  = False

		# for c in bpy.data.objects:
		# 	if(c.name == bpy.context.scene.Item):
		# 		del_section = c
		# 		del_section.select = True
		# 		bpy.ops.object.delete()

		# sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		
		# newS = [s for s in current_dir_content if(s['text'] != del_section.name)]

		# print('JsonManagerMenu.current_dir_content',current_dir_content)
		# current_dir_content = newS

		# delta = 0

		# #JsonManagerMenu.del_section(JsonManagerMenu)
	
		return {'FINISHED'} 		




class OpenObject(bpy.types.Operator):
	bl_idname = "object.open_object"
	bl_label = "OpenObject"
	def execute(self, context):
		pass
		return {'FINISHED'} 

class ClearScene(bpy.types.Operator):
	bl_idname = "object.clear_scene"
	bl_label = "ClearScene"
	def execute(self, context):
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		for s in sections:
			#section_items = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == s.name.split("_")[1]) ]
			
			section_items = [c for c in bpy.data.objects if(c.section == s.name)  ]
			for si in section_items:
				si.hide = True
		return {'FINISHED'} 

class PriceList(bpy.types.Operator):
	bl_idname = "object.prices_make"
	bl_label = "PriceList"
	def execute(self, context):
		materials = []
		objects = []
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]

		for s in sections:
			if(s.is_material):
				materials.append(s)
			else:
				objects.append(s)

		prices = []		
				
		for o in objects:
			#section_items_objects = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == o.name.split("_")[1] and len(c.name.split(".")) < 2) ]
			section_items_objects = [c for c in bpy.data.objects if(c.section == o.name and len(c.name.split(".")) < 2)  ]	
			for so in section_items_objects:	
				for m in materials:
					section_items = [c for c in bpy.data.objects if(c.section == m.name and len(c.name.split(".")) < 2)  ]
					for si in section_items:
						o = {}
						o['name'] = so.name
						o['material'] = si.data.materials[0].name
						o['price'] = 0.0	
						prices.append(o)


		# for m in materials:
		# 	for ob in objects:
		# 		o = {}
		# 		o['name'] = ob.name
		# 		o['material'] = m.name
		# 		o['price'] = ""

		# 		prices.append(o)

		json_string = json.dumps({ 'currency':'', 'items': [p for p in prices] }, indent=2, ensure_ascii=False)
		
		for tx in bpy.data.texts:
			if(tx.name == "prices.json"):
				tx.user_clear()
				bpy.data.texts.remove(tx)

		bpy.ops.text.new()
		text = bpy.data.texts[-1]
		text.name = 'prices.json'


		text.write(json_string)

		for area in bpy.context.screen.areas:
			if area.type == 'TEXT_EDITOR':
				area.spaces[0].text = text	
				


		return {'FINISHED'}


class MoveSection(bpy.types.Operator):
	bl_idname = "object.move_section"
	bl_label = "MoveSection"
	move_type = bpy.props.StringProperty()
	def execute(self, context):
		global current_dir_content
		if(self.move_type == "UP"):
			sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
			sections.sort(key=SortSections)
			for num,s in enumerate(sections):
				if(s.name == bpy.context.scene.Item):
					#s.order-=1
					number = num
					#s.order -= 1
				#else:
					#s.order	+= 1
			
			#tmp = sections[number -1 ].order.copy()
			sections[number -1 ].order,sections[number].order = sections[number].order,sections[number -1 ].order
			#sections[number].order = tmp

			#sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		
			sections.sort(key=SortSections)

			print('sections',[ s.order for s in  sections])
			add = current_dir_content[-1]
			current_dir_content = []
			for s in sections:
				item = {}
				item['text'] = s.name
				item['title'] = s.title
				item['isFolder'] = True 
				item['isUPFolder'] = False
				item['is_material'] = s.is_material == True
				item['Addbutton'] = False
				item['selected'] = False
				if(s.is_material):
					item['icon'] = bpy.data.images["folder_material.png"]	
				else:	
					item['icon'] = bpy.data.images["folder.png"]

				item['menu'] = bpy.data.images["m.png"]
				current_dir_content.append(item)
			
			current_dir_content.append(add)
		elif(self.move_type == "TOP"):
			sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
			for num,s in enumerate(sections):
				if(s.name == bpy.context.scene.Item):
					#s.order-=1
					number = num
					sections[number].order = 0
				else:
					s.order += 1 	
			sections.sort(key=SortSections)

			print('sections',[ s.order for s in  sections])
			add = current_dir_content[-1]
			current_dir_content = []
			for s in sections:
				item = {}
				item['text'] = s.name
				item['title'] = s.title
				item['isFolder'] = True 
				item['isUPFolder'] = False
				item['is_material'] = s.is_material == True
				item['Addbutton'] = False
				item['selected'] = False
				if(s.is_material):
					item['icon'] = bpy.data.images["folder_material.png"]	
				else:	
					item['icon'] = bpy.data.images["folder.png"]
				item['menu'] = bpy.data.images["m.png"]
				current_dir_content.append(item)
			
			current_dir_content.append(add)	
								
		elif(self.move_type == "BOTTOM"):
			sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
			for num,s in enumerate(sections):
				if(s.name == bpy.context.scene.Item):
					#s.order-=1
					number = num
					sections[number].order = len(sections)
				else:
					s.order -= 1 		
			sections.sort(key=SortSections)

			print('sections',[ s.order for s in  sections])
			add = current_dir_content[-1]
			current_dir_content = []
			for s in sections:
				item = {}
				item['text'] = s.name
				item['title'] = s.title
				item['isFolder'] = True 
				item['isUPFolder'] = False
				item['is_material'] = s.is_material == True
				item['Addbutton'] = False
				item['selected'] = False
				if(s.is_material):
					item['icon'] = bpy.data.images["folder_material.png"]	
				else:	
					item['icon'] = bpy.data.images["folder.png"]	
				
				item['menu'] = bpy.data.images["m.png"]
				current_dir_content.append(item)
			
			current_dir_content.append(add)		
				
		else:
			sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
			sections.sort(key=SortSections)
			for num,s in enumerate(sections):
				if(s.name == bpy.context.scene.Item):
					#s.order-=1
					number = num
					#s.order -= 1
				#else:
					#s.order	+= 1
	
			# print('sections',[ s.title for s in  sections])		
			# print('number',number)
			# print('sections',sections[number].title,sections[number].order)
			# print('sections',sections[number+1].title,sections[number].order)
			sections[number +1 ].order,sections[number].order = sections[number].order,sections[number +1 ].order
			#sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		
			sections.sort(key=SortSections)

			print('sections',[ str(s.order)+" _"+s.title for s in  sections])
			add = current_dir_content[-1]
			current_dir_content = []
			for s in sections:
				item = {}
				item['text'] = s.name
				item['title'] = s.title
				item['isFolder'] = True 
				item['isUPFolder'] = False
				item['is_material'] = s.is_material == True
				item['Addbutton'] = False
				item['selected'] = False
				if(s.is_material):
					item['icon'] = bpy.data.images["folder_material.png"]	
				else:	
					item['icon'] = bpy.data.images["folder.png"]	
				item['menu'] = bpy.data.images["m.png"]
				current_dir_content.append(item)
			
			current_dir_content.append(add)		
		#print('JsonManagerMenu.current_dir_content',current_dir_content)
			#current_dir_content = newS
			#current_dir_content.sort(key=SortSections)
		return {'FINISHED'} 

class SectionsButton(bpy.types.Panel):
	bl_label = "Json Editor"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Template Product"


	# bpy.types.Scene.section_name = bpy.props.StringProperty \
 #	(
 #	name = "",
 #	description = "My description",
 #	default = 'name',
 #	update = update_section_name
 #	)
	def draw(self, context):
		col = self.layout.column(align = True)
		if(len(bpy.context.selected_objects)== 1):
			#bpy.context.scene.section_name = '1111'
			# print('bpy.context.scene.section_name',bpy.context.selected_objects[0].name)
			col.prop(bpy.context.selected_objects[0], "title")
			# col.prop(bpy.context.selected_objects[0], "section_type")

			
		#col.operator(NewSection.bl_idname,icon = "ZOOMIN",  text = "New")
		#col.operator(LoadZip.bl_idname,icon = "IMAGE_COL",  text = "Load elements pictures")	

		col.operator(LoadObject.bl_idname,icon = "APPEND_BLEND",  text = "Append new element")		
		col.operator(ClearScene.bl_idname,icon = "VISIBLE_IPO_ON",  text = "Hide all elements")
		col.operator(PriceList.bl_idname,icon = "LINENUMBERS_ON",  text = "PriceList")

		col.operator(JsonManagerMenu.bl_idname,icon = "SCRIPTPLUGINS",  text = "Elements")
		col.operator(ScreenShotClass.bl_idname,icon = "RESTRICT_RENDER_OFF",  text = "ScreenShot All")	
		#col.operator(ExportClassGibrid.bl_idname, icon="EXPORT", text = "Save Data")	

		col.operator(ExportClassGibridWantenger.bl_idname, icon="EXPORT", text = "Export to Wantenger")	
		col.operator(PreviewClass.bl_idname, icon="ZOOM_ALL",  text = "Preview")	


class LoadZip(bpy.types.Operator):
	bl_idname = "object.load_zip"
	bl_label = "LoadZip"
	def execute(self, context):
		print('LoadZip')
		pass
		return {'FINISHED'}

class SectionSettings(bpy.types.Operator):
	bl_idname = "object.section_operator"
	bl_label = "Section Settings"


	tmp_mas = []
	def execute(self, context):

		pass
		
	def draw(self, context):
		col = self.layout.column(align = True)	

		# row = layout.row(align=False)
		# row.alignment = 'LEFT'
		# self.layout.alignment = "LEFT"	
		col.operator(DelSection.bl_idname,icon = "X",  text = "Delete")
		col.operator(MoveSection.bl_idname,icon = "TRIA_UP",  text = "Move Top").move_type = "TOP"
		col.operator(MoveSection.bl_idname,icon = "TRIA_UP",  text = "Move Up").move_type = "UP"
		col.operator(MoveSection.bl_idname,icon = "TRIA_DOWN",  text = "Move Down").move_type = "DOWN"
		col.operator(MoveSection.bl_idname,icon = "TRIA_DOWN",  text = "Move Bottom").move_type = "BOTTOM"
		col.operator(RenameSection.bl_idname,icon = "GREASEPENCIL",  text = "Rename")
		#col.operator(OpenObject.bl_idname,icon = "SCRIPTPLUGINS",  text = "Open")		


		for o in bpy.data.objects:
			if(o.name == bpy.context.scene.Item):
				ob = o
				col.prop(ob,'is_material')


	def invoke(self, context, event):

		wm = context.window_manager
		return wm.invoke_popup(self, width=100, height=150)
		#pass

		#return context.window_manager.invoke_props_dialog(self)

class ObjectSettings(bpy.types.Operator):
	bl_idname = "object.object_operator"
	bl_label = "Object Settings"


	tmp_mas = []
	def execute(self, context):

		pass
		
	def draw(self, context):
		col = self.layout.column(align = True)	

		# row = layout.row(align=False)
		# row.alignment = 'LEFT'
		# self.layout.alignment = "LEFT"	
		col.operator(OpenObjectSettings.bl_idname,icon = "SCRIPTPLUGINS",  text = "Settings")
		col.operator(UploadImage.bl_idname,icon = "IMAGE_COL",  text = "Upload Image")
		# col.operator(MoveSection.bl_idname,icon = "TRIA_UP",  text = "Move Up").move_type = "UP"
		# col.operator(MoveSection.bl_idname,icon = "TRIA_DOWN",  text = "Move Down").move_type = "DOWN"
		# col.operator(RenameSection.bl_idname,icon = "GREASEPENCIL",  text = "Rename")
		#col.operator(OpenObject.bl_idname,icon = "SCRIPTPLUGINS",  text = "Open")		

		


		# for o in bpy.data.objects:
		# 	if(o.name == bpy.context.scene.Item):
		# 		ob = o
		# 		col.prop(ob,'is_material')


	def invoke(self, context, event):

		wm = context.window_manager
		return wm.invoke_popup(self, width=100, height=150)
		#pass

		#return context.window_manager.invoke_props_dialog(self)		


class SelectSectrionIn(bpy.types.Operator):
	bl_idname = "object.select_in_operator"
	bl_label = "Section Settings"
	section_name = bpy.props.StringProperty()
	def execute(self, context):

		if(len(bpy.context.selected_objects) == 1):
			ob = bpy.context.selected_objects[0]

			#section_items = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == self.section_name.split("_")[1] and len(c.name.split(".")) < 2) ]
			#i = len(section_items) + 1
			#ob.name = "S-"+self.section_name.split('_')[1] + "_section-"+str(i)

			ob.section = self.section_name
		print('section_name',self.section_name)
		pass
		return {'FINISHED'}


class ClearSection(bpy.types.Operator):
	bl_idname = "object.clear_section"
	bl_label = "Clear Section"
	
	def execute(self, context):

		if(len(bpy.context.selected_objects) == 1):
			ob = bpy.context.selected_objects[0]

			#section_items = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == self.section_name.split("_")[1] and len(c.name.split(".")) < 2) ]
			#i = len(section_items) + 1
			#ob.name = "S-"+self.section_name.split('_')[1] + "_section-"+str(i)

			ob.section = ""
		
		return {'FINISHED'}

class SectionInSettings(bpy.types.Operator):
	bl_idname = "object.section_in_operator"
	bl_label = "Section Settings"

	
	tmp_mas = []
	def execute(self, context):
		
		pass
		return {'FINISHED'}
	def draw(self, context):
		col = self.layout.column(align = True)	

		
		sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]


		

		for s in sections:
			name = s.name
			if(s.title != "object_name"):
				name = s.title
			col.operator(SelectSectrionIn.bl_idname,  text = name).section_name = s.name
		col.operator(ClearSection.bl_idname,  text = "Clear Section")
		

		# col.operator(DelSection.bl_idname,icon = "X",  text = "Delete")
		# col.operator(MoveSection.bl_idname,icon = "TRIA_UP",  text = "Move Up").move_type = "UP"
		# col.operator(MoveSection.bl_idname,icon = "TRIA_DOWN",  text = "Move Down").move_type = "DOWN"
		# col.operator(RenameSection.bl_idname,icon = "GREASEPENCIL",  text = "Rename")
				


		


	def invoke(self, context, event):

		wm = context.window_manager
		return wm.invoke_popup(self, width=100, height=150)
		#pass




class TitleSettings(bpy.types.Operator):
	bl_idname = "object.title_settings"
	bl_label = "TitleSettings"


	tmp_mas = []
	def execute(self, context):
		pass
	def draw(self, context):
		col = self.layout.column(align = True)	
		col.prop(bpy.context.selected_objects[0], "title")	
		
		#col.operator(OpenObject.bl_idname,icon = "SCRIPTPLUGINS",  text = "Open")		

	def invoke(self, context, event):

		wm = context.window_manager
		return wm.invoke_popup(self, width=100, height=150)
		#pass

		#return context.window_manager.invoke_props_dialog(self)		
	
class DialogOperator(bpy.types.Operator):
	bl_idname = "object.dialog_operator"
	bl_label = "Compatiblity Settings"


	tmp_mas = []
	def execute(self, context):
	
		for c in bpy.data.objects:
			if(c.name == bpy.context.scene.Item):
				obj = c
				obj.compatiblity_mas.clear()
				obj.not_compatiblity_mas.clear()
				for o in tmp_mas:
					if(o.compatiblity):
						dp = obj.compatiblity_mas.add()
						dp.name = o.name
					else:
						dp = obj.not_compatiblity_mas.add()
						dp.name = o.name	
				del tmp_mas[:]		
		
		print('obj.compatiblity_mas',[c.name for c in obj.compatiblity_mas])
		print('obj.not_compatiblity_mas',[c.name for c in obj.not_compatiblity_mas])
						
		print('CLOSE')
		return {'FINISHED'}

	def draw(self, context):

		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		sections.sort(key=SortSections)
		layout = self.layout
		col = layout.column(align=True)
		# for c in bpy.data.objects:
		# 	if(c.name == bpy.context.scene.Items):
		col.label("Object "+bpy.context.scene.Item)
		col.label("compatible width:")
		
		for s in sections:
			col = layout.column(align=True)
			row = layout.row(align = True) 
			row.prop(s,'select_all',s.name)
			#section_items = [c for c in bpy.data.objects if(c.name.split('_')[0].split('-')[0] == "S" and len(c.name.split('_')[0].split('-')) > 1 and c.name.split('_')[0].split('-')[1] == s.name.split("_")[1] and c.name != bpy.context.scene.Item) ]
			
			section_items = [c for c in bpy.data.objects if(c.section == s.name and c.name != bpy.context.scene.Item) ]
			
			row = layout.row(align = True) 		
			for si in section_items:
				tmp_mas.append(si)
				row.prop(si,'compatiblity',si.name)
			layout.separator()		
	
			
			layout.separator()	
		
	def invoke(self, context, event):

		pass

		return context.window_manager.invoke_props_dialog(self)



class JsonManagerMenu(bpy.types.Operator):

	bl_idname = "view3d.json_manager"
	bl_label = "json_manager"
	tree_index = ''
	global current_dir_content

	def clearImages(self):
		# Cleaner for Images
		# print ("here")
		for image in bpy.data.images:
			if image.filepath_raw in self.imageList:
				# print (image.filepath_raw)
				image.user_clear()
				bpy.data.images.remove(image)

			# print ("images " + str(len(bpy.data.images)))

			self.imageList.clear()

	
	def object_settings(self,selected):
		global current_dir_content
		current_dir_content = []
		selected['main'] = True
		selected['back'] = bpy.data.images["back.png"]
		
		current_dir_content.append(selected)

		sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
		#objs = [ o for o in bpy.data.objects if (o.name.split('-')[0] == 'S')]

		print('sections',sections)
		sections.sort(key=SortSections)

		for num,o in enumerate(sections):
			item = {}
			item['text'] = o.name
			item['title'] = o.title
			item['isFolder'] = True
			item['isUPFolder'] = False
			item['is_material'] = o.is_material == True
			item['Addbutton'] = False
			item['selected'] = False
			item['settings'] = True
			item['settings_item'] = selected
			o.order = num
			 
			# iconFile = os.path.join(libraryIconsPath, "folder.png")
			# item['icon'] = bpy.data.images.load(filepath = iconFile)
			item['icon'] = bpy.data.images["folder.png"]
			item['menu'] = bpy.data.images["m.png"]
			current_dir_content.append(item) 		

	def modal(self, context, event):
		global delta
		global targetItemHeight
		global current_dir_content
		global contentWidthArea,rows
		global scrollOn
		global current_item
		wheelSpeed = 0.05
		contentHeight = context.area.regions[4].height - 2*5
		context.area.tag_redraw()

		panelHeight = len(current_dir_content) * (targetItemHeight + 5) / rows + 50

		# Scroll
		if(panelHeight > contentHeight):
			scrollPercent = 1 - delta / (panelHeight - contentHeight)

			if event.type == 'MOUSEMOVE':
				
				(selected,Type) = getMoved(self, context)

				if( event.value == 'PRESS' and scrollOn):
					if(event.mouse_region_y > contentHeight- 45):
						scrollPercent = 1
					elif(event.mouse_region_y < 45):
						scrollPercent = 0
					else:	
						scrollPercent = (event.mouse_region_y - 45) / (contentHeight - 80)

						
						#print('event.mouse_region_y',event.mouse_region_y,contentHeight)
						self.mouseX = event.mouse_region_x
						self.mouseY = event.mouse_region_y

					
				else:
					#delta = 0
					pass

			elif  event.type == 'WHEELDOWNMOUSE':
				scrollPercent -= wheelSpeed
				if scrollPercent < 0 :
					scrollPercent = 0
			elif event.type == 'WHEELUPMOUSE' :	
				scrollPercent += wheelSpeed
				if scrollPercent > 1 :
					scrollPercent = 1
						
			elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
				self.first = event.mouse_region_x

			elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
				self.last = event.mouse_region_x
				scrollOn = 'false'				
				dlt = self.last - self.first
				print('dltdltdltdltdltdlt',dlt)
				(selected,Type) = getClicked(self, context)

				print('selected',selected)
				print('Type',Type)
				
				if(Type == 'scroll'):	
					print('111111111111111')
					print('BBB',delta)	
			# 		pass
			# if(dlt < 100 and dlt > -10):

					print('self.first',self.first)
					print('self.last',self.last)

					if(event.mouse_region_y > contentHeight- 45):
						scrollPercent = 1

					elif(event.mouse_region_y < 45):
						scrollPercent = 0
					else:	
						scrollPercent = (event.mouse_region_y - 45) / (contentHeight - 80)
						self.mouseX = event.mouse_region_x
						self.mouseY = event.mouse_region_y







			delta = (panelHeight - contentHeight) * (1 - scrollPercent)

		# Mouse click
		if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
			self.first = event.mouse_region_x
					
		elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
			self.last = event.mouse_region_x

			dlt = self.last - self.first
			if(dlt < 100 and dlt > -10):
				self.mouseX = event.mouse_region_x
				self.mouseY = event.mouse_region_y

				(selected,Type) = getClicked(self, context)
				print('selected',selected)
				print('Type',Type)
				
				if selected == None:
					bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
					return {'FINISHED'}

				bpy.context.scene.Item = selected['text']
				current_item = selected

				if(Type == 'menu'):
					if not selected['isFolder']:
						if not 'accept' in selected:
							
							bpy.ops.object.object_operator('INVOKE_DEFAULT')
							#self.object_settings(selected)
						#bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
						# self.redraw()
					else:
						if not selected['isUPFolder']:
							bpy.ops.object.section_operator('INVOKE_DEFAULT')
						# self.redraw()	
				elif(Type == 'scroll'):	
					print('111111111111111')
					print('BBB',delta)	
					pass
				
							
				elif(Type == 'accept'):	
					if('back' in selected):
						selected.pop('main',None)
						selected.pop('back', None)
						selected.pop('settings', None)
						selected.pop('settings_item', None)
						self.BrowseContent(None)
					else:	
						if not selected['isFolder']:
							self.toggle_accept(selected)
					
					pass	
				else:		
					print('2222222222222222')
					if selected['isFolder'] == True:
						if selected['Addbutton'] == True:
							self.add_section()
						else:	
							delta = 0
							self.mouseY = 0 + context.area.regions[4].height #- 35
							# self.tree_index = os.path.normpath(os.path.join(self.tree_index, selected['text']))
							self.browse_assets(selected)

					else:
						
						if selected['Addbutton'] == True:
							self.add_item(selected)
						#elif(Type == 'icon'):
							#
						#	bpy.ops.import_image.data('INVOKE_DEFAULT')		
						else:		
							delta = 0
							self.mouseY = 0 + context.area.regions[4].height #- 35
							self.choose_object(selected)
							#bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
							
							# bpy.ops.import_scene.obj(filepath=selected['filename'])
							# bpy.ops.view3d.snap_selected_to_cursor()
							# bpy.context.scene.objects.active = bpy.context.selected_objects[0]

						return {'RUNNING_MODAL'}
			elif(dlt > 101):
				if(contentWidthArea == 700):
					rows = 2
					contentWidthArea = 1400
			else:
				if(contentWidthArea > 700):
					rows = 1
					contentWidthArea = 700			
			# print('MOVE',dlt)
			# contentWidthArea *= 2			

		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

			return {'CANCELLED'}
			# Column count changing

		return {'RUNNING_MODAL'}



	def choose_object(self,item):

		if(item['selected']):
			item['selected'] = False
			for o in bpy.data.objects:
				o.select = False
				if(o.name == bpy.context.scene.Item):
					ob = o
					ob.hide = True
					ob.select = False

		else:	
			item['selected'] = True
			for o in bpy.data.objects:
				o.select = False
				if(o.name == bpy.context.scene.Item):
					ob = o
					ob.hide = False
					ob.select = True

	def redraw(self):
		global current_dir_content
	
		# add  = current_dir_content[-1]
		# current_dir_content = []
		ob = bpy.context.scene.Item
		if(ob.split('_')[0] == "Section"):
			self.BrowseContent()
			# sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
			# for s in sections:
			# 	item = {}
			# 	item['text'] = new_obj.name
			# 	item['isFolder'] = True 
			# 	item['isUPFolder'] = False
			# 	item['Addbutton'] = False
			# 	item['icon'] = bpy.data.images["folder.png"]
			# 	item['menu'] = bpy.data.images["m.png"]
			# 	current_dir_content.append(item)

			# current_dir_content.append(add)
		else:
			for i in current_dir_content:
				if(i['text'] == bpy.context.scene.Item):
					item = i 
					self.browse_assets(item)			

	def add_item(self,item):
		global current_dir_content
		print('add item',item)
		name = item['Folder']
		objs = [ o for o in bpy.data.objects if (o.name.split('-')[0] == 'S' and o.name.split('_')[0].split('-')[1] == name.split('_')[1] and len(name.split('.')) < 2)]
		
		l = len(objs)


		bpy.ops.mesh.primitive_cube_add( radius =0.5 ,location=(0,0,0))
		new_obj = bpy.context.scene.objects.active 
		
		if(l == 0):
			
					
			new_obj.name = "S-"+name.split('_')[-1]+"_section-1"
			new_obj.section = 	name		
		else:
		
			name_obj = objs[-1].name
			new_obj.name = name_obj.split("_")[0] + "_" + name_obj.split("_")[1] + "-" + str(l+1) 	
			new_obj.section = name

		new_obj.b4w_do_not_batch = True
		new_obj.b4w_dynamic_geometry = True
		Upitem = [c for c in current_dir_content if(c['text'] == name)][0]	

		print('Upitem',Upitem)
		Upitem['isUPFolder'] = False
		#Upitem['is_material'] = item.is_material == True
		self.browse_assets(Upitem)	

	def add_section(self):
		global current_dir_content
		sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		l = len(sections)
		bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.1, view_align=False, location=(0,0,0))
		new_obj = bpy.context.scene.objects.active 
		
		new_obj.name = "Section_"+str(l+1)

		print('self1',self)

		item = {}
		item['text'] = new_obj.name
		item['title'] = new_obj.title
		item['isFolder'] = True 
		item['isUPFolder'] = False
		item['is_material'] = False
		item['Addbutton'] = False
		item['selected'] = False
		# iconFile = os.path.join(libraryIconsPath, "nothumbnail.png")
		# item['icon'] = bpy.data.images.load(filepath = iconFile)
		item['icon'] = bpy.data.images["folder.png"]

		# iconMenu = os.path.join(libraryIconsPath, "m.png")
		# item['menu'] = bpy.data.images.load(filepath = iconMenu)
		item['menu'] = bpy.data.images["m.png"]

		add  = current_dir_content[-1]
		current_dir_content[-1] = item
		current_dir_content.append(add)	 	 
					
	def del_section(self):	
		global delta,redrawFlag
		for c in bpy.data.objects:
			c.select  = False

		for c in bpy.data.objects:
			if(c.name == bpy.context.scene.Item):
				del_section = c
				del_section.select = True
				bpy.ops.object.delete()
		# JsonManagerMenu.redraw(JsonManagerMenu)		
		redrawFlag = True
			

		# bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
				
		


		# sections = [c for c in bpy.data.objects if(c.name.split('_')[0] == "Section")]
		
		# newS = [s for s in current_dir_content if(s['text'] != del_section.name)]

		# print('current_dir_content',current_dir_content)
		# current_dir_content = newS
		
	def find_obj_image(self,item):
		image = bpy.data.images["nothumbnail.png"]
		for i in bpy.data.images:
			if(i.name == item['text']+'_.jpg'):
				image = i
		return image	

	def check_accept(self,obj,name):
		res = bpy.data.images["folder.png"]
		print('check_accept',obj,name)
		for o in bpy.data.objects:
			if(o.name == name):
				if(hasattr(o,'not_compatiblity_mas')):
					if(obj.name in o.not_compatiblity_mas):
						res = bpy.data.images["disAccept.png"]
					else:
						res = bpy.data.images["Accept.png"]
		return res

	def check_accept_folder(self,folder_name,name):
		
		res = True
		list_check = []
		print('CHECKsections',name,folder_name)
		for o in bpy.data.objects:
			if(o.name == name):
				sections = [ sec for sec in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
				for s in sections:
					print('CHECKsections',s,folder_name)
					if(s.name == folder_name):
						objs = [ o for o in bpy.data.objects if (o.name.split('-')[0] == 'S' and o.name.split('_')[0].split('-')[1] == folder_name.split('_')[1] and len(o.name.split('.')) < 2)]
						print('CHECK',objs)
						for obj in objs:
							if(obj.name in o.not_compatiblity_mas):
								res = list_check.append(True)
							else:
								res = list_check.append(False)
						list1 = res
						list2 = []    
						[list2.append(i) for i in list1 if not i in list2]    		
						print('list2',list2)			
				# if(hasattr(o,'not_compatiblity_mas')):
				# 	if(obj.name in o.not_compatiblity_mas):
				# 		res = bpy.data.images["disAccept.png"]
				# 	else:
				# 		res = bpy.data.images["Accept.png"]
		return bpy.data.images["Accept.png"]
			
	def check_item(self,item):
		name = 	item['text']
		sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
		for s in sections:
			if(len(name.split("_")) > 1 and len(name.split("_")[0].split("-")) > 1 and s.name.split('_')[1] == name.split('_')[0].split("-")[1]):
				if(s.is_material):	
					for o in bpy.data.objects:
						if(o.name == name):
							mat_source = o.data.materials[0]
							print('mat_source',mat_source)
							# for o in bpy.data.objects:
							# 	o.select = False
							# 	if(o.name == item["settings_item"]["text"]+'.'+mat_source.name):
							# 		if(o.hide == True):
							# 			o.hide = False
							# 		o.select = True
							# 		bpy.ops.object.delete()
							for ob in bpy.data.objects:	
								if(ob.name == item["settings_item"]["text"]):
									if(item['accept'] == bpy.data.images["disAccept.png"]):
										for ind,c in enumerate(o.exception_materials):
											if(c.name == name):
												c.exception_materials.remove(ind)
										dp = ob.exception_materials.add()
										dp.name = name
									else:
										for ind,c in enumerate(o.exception_materials):
											if(c.name == name):
												c.exception_materials.remove(ind)

									print('ERROR',ob)
									



	def toggle_accept(self,item):

		print('TOGGLE',item)

		

		if('accept' in item):
			if(item['accept'] == bpy.data.images["disAccept.png"]):
				item['accept'] = bpy.data.images["Accept.png"]
				for o in bpy.data.objects:
					if(o.name == item["settings_item"]['text']):
						print('TOGGLEo.not_compatiblity_mas', [ o.name for o in o.not_compatiblity_mas], item["settings_item"]['text'],item['text'] )
						if(hasattr(o,'not_compatiblity_mas')):
							for ind,c in enumerate(o.not_compatiblity_mas):
								if(c.name == item['text']):
									o.not_compatiblity_mas.remove(ind)
							#o.compatiblity_mas = [c for c in o.compatiblity_mas if(c.name != item["settings_item"]['text'])]
			else:
				item['accept'] = bpy.data.images["disAccept.png"]		
				for o in bpy.data.objects:
					if(o.name == item["settings_item"]['text']):
						if(hasattr(o,'not_compatiblity_mas')):
							for ind,c in enumerate(o.not_compatiblity_mas):
								if(c.name == item['text']):
									o.not_compatiblity_mas.remove(ind)
							dp = o.not_compatiblity_mas.add()
							dp.name = item['text']

		self.check_item(item)					

	def browse_assets(self, selected):
		global current_dir_content

		name = selected['text']

		title = selected['title']
		current_dir_content = []
		

		if(selected['isUPFolder']):
			self.BrowseContent(selected)
		else:	


			#objs = [ o for o in bpy.data.objects if (o.name.split('-')[0] == 'S' and o.name.split('_')[0].split('-')[1] == name.split('_')[1] and len(o.name.split('.')) < 2)]
			objs = [c for c in bpy.data.objects if(c.section == name and len(c.name.split('.')) < 2)  ]	
			if('settings' in selected):
				objs = [o for o in objs if(o.name != selected['settings_item']['text'])]

			
			up_folder = {}
			#iconFile = os.path.join(libraryIconsPath, "folder.png")
			#up_folder['icon'] = bpy.data.images.load(filepath = iconFile)
			up_folder['icon'] = bpy.data.images["Up.png"]
			
			up_folder['text'] = name
			up_folder['title'] = title
			up_folder['isFolder'] = True
			up_folder['isUPFolder'] = True
			if('is_material' in selected):
					if(selected['is_material']):
						up_folder['is_material'] = True
					else:
						up_folder['is_material'] = False
			else:
				up_folder['is_material'] = False					
			
			up_folder['Addbutton'] = False
			up_folder['selected'] = False
			up_folder['subItems'] = []

			if('settings' in selected):
				#up_folder['accept'] = self.check_accept_folder(selected['text'],selected['settings_item']['text'])
				up_folder['settings_item'] = selected['settings_item']
				up_folder['settings'] = True
				current_dir_content.append(selected['settings_item'])   

			#up_folder['index'] = self.tree_index
			current_dir_content.append(up_folder)	 	 

			# print('item',item)
			for o in objs:
				item = {}
				item['text'] = o.name
				item['title'] = o.title
				item['user_image'] = o.user_image
				item['isFolder'] = False 
				item['isUPFolder'] = False
				item['Addbutton'] = False
				item['selected'] = o.hide != True
				# iconFile = os.path.join(libraryIconsPath, "nothumbnail.png")
				# item['icon'] = bpy.data.images.load(filepath = iconFile)
				if('is_material' in selected):
					if(selected['is_material']):
						if(item['user_image']):
							item['icon'] = self.find_obj_image(item)
						else:		
							item['icon'] = bpy.data.images["nothumbnail.png"]
					else:
						item['icon'] = self.find_obj_image(item)			
				else:	
					item['icon'] = self.find_obj_image(item)

				# iconMenu = os.path.join(libraryIconsPath, "m.png")
				# item['menu'] = bpy.data.images.load(filepath = iconMenu)
				item['menu'] = bpy.data.images["m.png"]

				if('settings' in selected):
					item['accept'] = self.check_accept(o,selected['settings_item']['text'])
					item['settings_item'] = selected['settings_item']

				
				#self.imageList.append(item['menu'].filepath_raw)
				current_dir_content.append(item)   


			add = {}
		
			add['isFolder'] = False
			add['isUPFolder'] = False	
			add['Addbutton'] = True
			add['selected'] = False
			add['is_material'] = False
			add['icon'] = bpy.data.images["add.png"]
			add['menu'] = bpy.data.images["m.png"]
			add['Folder'] = name
			add['text'] = "Add"
			
			if('settings' in selected):
				pass	
			else:	
				current_dir_content.append(add)	

	def BrowseContent(self,selected):
		global current_dir_content
		current_dir_content = []
		
		sections = [ o for o in bpy.data.objects if (o.name.split('_')[0] == 'Section')]
		#objs = [ o for o in bpy.data.objects if (o.name.split('-')[0] == 'S')]

		print('sections',sections)
		sections.sort(key=SortSections)

		if(selected):
			if('settings' in selected):
					current_dir_content.append(selected['settings_item'])   

		for num,o in enumerate(sections):
			item = {}
			item['text'] = o.name
			item['title'] = o.title
			item['isFolder'] = True
			item['isUPFolder'] = False
			item['Addbutton'] = False
			item['selected'] = False
			item['is_material'] = o.is_material == True
			o.order = num
			 
			# iconFile = os.path.join(libraryIconsPath, "folder.png")
			# item['icon'] = bpy.data.images.load(filepath = iconFile)
			
			if(o.is_material):
				item['icon'] = bpy.data.images["folder_material.png"]	
			else:	
				item['icon'] = bpy.data.images["folder.png"]
			item['menu'] = bpy.data.images["m.png"]
			if(selected):
				if('settings' in selected):
					item['settings'] = True
					item['settings_item'] = selected['settings_item']
					
			current_dir_content.append(item) 

		add = {}
		
		add['isFolder'] = True
		add['isUPFolder'] = False	
		add['Addbutton'] = True
		add['selected'] = False
		add['icon'] = bpy.data.images["add.png"]
		add['menu'] = bpy.data.images["m.png"]
		add['text'] = "Add"
		add['title'] = "object_name"
		current_dir_content.append(add)

	def __del__(self):
		# print("End")
		pass
		#self.clearImages()

	def invoke(self, context, event):
		global current_dir_content
		global delta
		global scrollOn
		if context.area.type == 'VIEW_3D':


			self.mouseX = event.mouse_region_x
			self.mouseY = 0 + context.area.regions[4].height #- 40
			scrollOn = 'false'
			delta = 0
			self.mainItem = {}
			current_dir_content = []
			self.imageList = []

			print('INIT MAGIC')
			# self.buildAssetTree(self.mainItem, libraryDefaultModelsPath)
			# self.browse_assets(libraryDefaultModelsPath)
			self.BrowseContent(None)
			self.activeItem = self.mainItem

			# the arguments we pass the the callback
			args = (self, context)
			# Add the region OpenGL drawing callback
			# draw in view space with 'POST_VIEW' and 'PRE_VIEW'
			self._handle = bpy.types.SpaceView3D.draw_handler_add(drawCallbackMenu, args, 'WINDOW', 'POST_PIXEL')

			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "View3D not found")
			return {'CANCELLED'}   





class LoadObject(bpy.types.Operator):
	bl_idname = "object.load_object"
	bl_label = "LoadObject"
	def execute(self, context):
		bpy.ops.wm.append('INVOKE_DEFAULT')
		return {'FINISHED'}




def replace_shortkey( old_op_name, new_op_name) :

        wm = bpy.context.window_manager
        keyconfig = wm.keyconfigs.active
        keymap = keyconfig.keymaps['3D View']
        items = keymap.keymap_items

        item = items.get(old_op_name, None)
        while item :

                props = item.properties
                print('props',props)

                # extend    = props.extend.real
                # deselect  = props.deselect.real
                # toggle    = props.toggle.real
                # center    = props.center.real
                # enumerate = props.enumerate.real
                # object    = props.object.real

                item.idname = new_op_name

                # props.extend    = extend 
                # props.deselect  = deselect
                # props.toggle    = toggle
                # props.center    = center
                # props.enumerate = enumerate
                # props.object    = object

                item = items.get( old_op_name, None)



class SelectionOperatorGibrid(bpy.types.Operator):
	""" Costum selection
	"""
	bl_idname = "view3d.select_costum_gibrid" 
	bl_label = "costum selection"

	
	location = IntVectorProperty(default = (0,0),subtype ='XYZ', size = 2)

	def execute(self, context):

		coord = self.location[0],self.location[1]
		region = bpy.context.region
		rv3d = bpy.context.space_data.region_3d
		vec = region_2d_to_vector_3d(region, rv3d, coord)
		loc = region_2d_to_location_3d(region, rv3d, coord, vec)
		# loc = region_2d_to_location_3d(region,rv3d ,coord,(0,0,0))

		bpy.context.scene.cursor_location = loc


		#select the object
		bpy.ops.object.section_in_operator('INVOKE_DEFAULT')
		bpy.ops.view3d.select( location=(self.location[0] , self.location[1] ))
		#change the property
		#print('select 111',bpy.context.selected_objects[0].name,bpy.context.selected_objects[0].name.split("_"),bpy.context.selected_objects[0].name.split("_")[1])



		return {'FINISHED'}

	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			self.location[0] = event.mouse_region_x
			self.location[1]  = event.mouse_region_y
			return self.execute(context)
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

# store keymaps here to access after registration
addon_keymaps = []

def write_image(context, filepath):
	print("running read_some_data...",bpy.context.scene.Item)
	filename = filepath.split('/')[-1]
	newimg = bpy.data.images.load(filepath)

	for img in bpy.data.images:
			if(img.name == bpy.context.scene.Item + "_"+ ".jpg"):
				img.user_clear()
				if(img.users == 0):
					bpy.data.images.remove(img)


	newimg.name = bpy.context.scene.Item+ "_"+ ".jpg"

	for o in bpy.data.objects:
		if(o.name == bpy.context.scene.Item):
			obj = o
			obj.user_image = True

	print('obj.user_image',obj.user_image)
	return {'FINISHED'}

class ImportImage(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_image.data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "ImportImage"

    
    

    def execute(self, context):
        return write_image(context, self.filepath)


def register():
	bpy.utils.register_class(JsonManagerMenu)
	bpy.utils.register_class(DialogOperator)
	bpy.utils.register_class(SectionsButton)
	bpy.utils.register_class(ScreenShotClass)
	bpy.utils.register_class(ExportClassGibrid)
	bpy.utils.register_class(ExportClassGibridWantenger)
	bpy.utils.register_class(NewSection)
	bpy.utils.register_class(OpenObject)

	bpy.utils.register_class(ClearScene)
	bpy.utils.register_class(SectionSettings)
	bpy.utils.register_class(ObjectSettings)
	bpy.utils.register_class(DelSection)
	bpy.utils.register_class(MoveSection)
	
	#bpy.utils.register_class(StoreHandler)
	
	bpy.utils.register_class(PreviewClass)
	

	bpy.utils.register_class(LoadObject)
	bpy.utils.register_class(TitleSettings)
	bpy.utils.register_class(RenameSection)
	
	bpy.utils.register_class(SelectionOperatorGibrid) 
	bpy.utils.register_class(SectionInSettings) 
	bpy.utils.register_class(SelectSectrionIn) 
	bpy.utils.register_class(ClearSection) 
	bpy.utils.register_class(PriceList) 
	bpy.utils.register_class(ImportImage) 	
	bpy.utils.register_class(OpenObjectSettings) 	
	bpy.utils.register_class(LoadZip) 
	bpy.utils.register_class(UploadImage) 	
	  	
	
	# handle the keymap
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	if kc:
		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('view3d.json_manager', 'Q', 'PRESS', ctrl=True, shift=True, alt=True)

		# kmi.properties.use_selection = True
		# kmi.properties.use_mesh_modifiers = False		 
	addon_keymaps.append((km, kmi))
	replace_shortkey( 'view3d.cursor3d', SelectionOperatorGibrid.bl_idname ) 



def unregister():
	bpy.utils.unregister_class(JsonManagerMenu)
	bpy.utils.unregister_class(DialogOperator)
	bpy.utils.unregister_class(SectionsButton)
	bpy.utils.unregister_class(ScreenShotClass)
	bpy.utils.unregister_class(ExportClassGibrid)
	bpy.utils.unregister_class(ExportClassGibridWantenger)
	
	bpy.utils.unregister_class(NewSection)
	bpy.utils.unregister_class(OpenObject)

	bpy.utils.unregister_class(ClearScene)
	bpy.utils.unregister_class(SectionSettings)
	bpy.utils.unregister_class(ObjectSettings)
	bpy.utils.unregister_class(DelSection)
	bpy.utils.unregister_class(MoveSection)
	#bpy.utils.unregister_class(StoreHandler)
	bpy.utils.unregister_class(PreviewClass)
	bpy.utils.unregister_class(RenameSection)

	

	bpy.utils.unregister_class(LoadObject)
	bpy.utils.unregister_class(TitleSettings)
	bpy.utils.unregister_class(SelectionOperatorGibrid) 
	bpy.utils.unregister_class(SectionInSettings) 
	bpy.utils.unregister_class(SelectSectrionIn) 
	bpy.utils.unregister_class(ClearSection) 
	bpy.utils.unregister_class(PriceList) 
	bpy.utils.unregister_class(ImportImage) 
	bpy.utils.unregister_class(OpenObjectSettings) 		
	bpy.utils.unregister_class(LoadZip) 	
	bpy.utils.unregister_class(UploadImage) 	

	# handle the keymap
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
	replace_shortkey(SelectionOperatorGibrid.bl_idname, 'view3d.cursor3d')
	
if __name__ == "__main__":
	register() 	