import bpy

for obj in bpy.data.objects:
    obj.compatiblity_mas.clear()
    obj.not_compatiblity_mas.clear()