from bpy.types import Context, Object, Operator
from bpy.props import BoolProperty
from .utils import Uninstancer


class OBJECT_OT_restore_collection_instances(Operator):
    bl_idname = 'object.restore_collection_instances'
    bl_label = 'Restore Collection Instances'
    bl_description = 'Replace instances with collections, using duplicate objects'
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(
        name='Duplicate',
        description='Duplicate instance collection, its children, and the objects inside',
        default=True,
    )

    linked: BoolProperty(
        name='Linked',
        description='Duplicate object but not object data, linking to the original data',
        default=True,
    )

    def draw(self, context: Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, 'duplicate')
        sub = layout.row()
        sub.enabled = self.duplicate
        sub.prop(self, 'linked')

    def execute(self, context: Context) -> set:
        uninstancer = Uninstancer(self.duplicate, self.linked)

        for object in context.selected_objects.copy():
            object: Object

            if object.type == 'EMPTY':
                if object.instance_type == 'COLLECTION':
                    if object.instance_collection:
                        uninstancer.uninstance(object)

        for window in context.window_manager.windows.values():
            for area in window.screen.areas.values():
                area.tag_redraw()

        return {'FINISHED'}
