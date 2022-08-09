import bpy


def realize_instance(context: bpy.types.Context, instance: bpy.types.Object, linked: bool):
    old_collection = instance.instance_collection
    new_collection = duplicate_collection(old_collection)

    for collection in instance.users_collection:
        collection: bpy.types.Collection
        collection.children.link(new_collection)

    collection_data = show_collection(new_collection)
    old_objects: list[bpy.types.Object] = new_collection.all_objects[:]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.duplicate({'selected_objects': old_objects}, linked=linked)
    new_objects: list[bpy.types.Object] = context.selected_objects[:]
    hide_collection(new_collection, collection_data)

    unlink_objects(old_collection, new_objects)
    unlink_objects(new_collection, old_objects)

    origin = bpy.data.objects.new(new_collection.name, None)
    new_collection.objects.link(origin)
    origin.matrix_world = instance.matrix_world
    context.view_layer.objects.active = origin
    origin.select_set(True)

    for object in new_objects:
        if not object.parent:
            object.parent = origin

    bpy.data.objects.remove(instance)


def duplicate_collection(old_collection: bpy.types.Collection) -> bpy.types.Collection:
    new_collection: bpy.types.Collection = old_collection.copy()

    for child in new_collection.children.values():
        new_collection.children.link(duplicate_collection(child))
        new_collection.children.unlink(child)

    return new_collection


def show_collection(collection: bpy.types.Collection) -> dict:
    data = {}

    data['hide_viewport'] = collection.hide_viewport
    collection.hide_viewport = False

    data['hide_select'] = collection.hide_select
    collection.hide_select = False

    data['children'] = []
    for child in collection.children.values():
        data['children'].append(show_collection(child))

    return data


def hide_collection(collection: bpy.types.Collection, data: dict):
    for child, child_data in zip(collection.children.values(), data['children']):
        hide_collection(child, child_data)

    collection.hide_viewport = data['hide_viewport']
    collection.hide_select = data['hide_select']


def unlink_objects(collection: bpy.types.Collection, objects: list[bpy.types.Object]):
    for child in collection.children:
        unlink_objects(child, objects)

    for object in collection.objects[:]:
        if object in objects:
            collection.objects.unlink(object)


def tag_redraw(context: bpy.types.Context):
    for window in context.window_manager.windows.values():
        for area in window.screen.areas.values():
            area.tag_redraw()
