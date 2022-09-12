bl_info = {
    'name': 'Restore Collection Instances',
    'author': 'bonjorno7',
    'description': 'Turn collection instances back into collections, with their original hierarchy',
    'blender': (3, 2, 0),
    'version': (2, 0, 1),
    'category': 'Object',
    'location': 'View3D > Object > Apply',
    'doc_url': 'https://keyboardrenderkit.readthedocs.io/en/stable/rci.html',
    'tracker_url': 'https://github.com/bonjorno7/restore-collection-instances',
}

from bpy.types import Context, Menu, VIEW3D_MT_object_apply
from bpy.utils import register_class, unregister_class
from .ops import OBJECT_OT_restore_collection_instances


def object_apply_menu(self: Menu, context: Context):
    self.layout.operator(OBJECT_OT_restore_collection_instances.bl_idname)


def register():
    register_class(OBJECT_OT_restore_collection_instances)
    VIEW3D_MT_object_apply.append(object_apply_menu)


def unregister():
    VIEW3D_MT_object_apply.remove(object_apply_menu)
    unregister_class(OBJECT_OT_restore_collection_instances)
