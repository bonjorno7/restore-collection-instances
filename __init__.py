bl_info = {
    'name': 'Restore Collection Instances',
    'author': 'bonjorno7',
    'description': 'Turn collection instances back into collections, with their original hierarchy',
    'blender': (3, 2, 0),
    'version': (1, 1, 1),
    'category': 'Object',
    'location': 'View3D > Object > Apply',
}

import bpy
from . import ops


def object_apply_menu(self: bpy.types.Menu, context: bpy.types.Context):
    self.layout.operator(ops.OBJECT_OT_restore_collection_instances.bl_idname)


def register():
    bpy.utils.register_class(ops.OBJECT_OT_restore_collection_instances)
    bpy.types.VIEW3D_MT_object_apply.append(object_apply_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_apply.remove(object_apply_menu)
    bpy.utils.unregister_class(ops.OBJECT_OT_restore_collection_instances)
