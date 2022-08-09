import bpy
from . import utils


class OBJECT_OT_restore_collection_instances(bpy.types.Operator):
    bl_idname = 'object.restore_collection_instances'
    bl_label = 'Restore Collection Instances'
    bl_description = 'Replace selected instances with their collections, using new objects but linked data'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> set:
        objects: list[bpy.types.Object] = context.selected_objects[:]
        bpy.ops.object.select_all(action='DESELECT')

        for object in objects:
            if object.type != 'EMPTY':
                continue
            if object.instance_type != 'COLLECTION':
                continue
            if not object.instance_collection:
                continue
            utils.realize_instance(context, object)

        utils.tag_redraw(context)
        return {'FINISHED'}
