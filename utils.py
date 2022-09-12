from typing import Any, Iterator, List, Tuple
from bpy.types import ID, Collection, Object, Property


class Uninstancer:

    def __init__(self, duplicate: bool, reuse_data: bool):
        self.duplicate = duplicate
        self.reuse_data = reuse_data

        self.cache = dict()
        self.done = set()

    def uninstance(self, instance: Object):
        self.clear_cache()

        collection = self.copy_collection(instance.instance_collection)
        self.link_collection(instance.users_collection, collection)

        self.copy_objects_and_data(collection)
        self.replace_objects(collection)
        self.update_objects(collection)

        if self.duplicate:
            self.parent_objects(instance, collection.all_objects)
            self.clear_instance(instance)

    def clear_cache(self):
        for key, value in list(self.cache.items()):
            if not self.reuse_data or isinstance(value, (Object, Collection)):
                del self.cache[key]

        self.done.clear()

    def copy_collection(self, collection: Collection) -> Collection:
        if collection in self.cache:
            return self.cache[collection]

        collection = self.copy_data(collection)

        for child in collection.children.values():
            collection.children.unlink(child)
            collection.children.link(self.copy_collection(child))

        return collection

    def link_collection(self, parents: List[Collection], child: Collection):
        for parent in parents:
            if child not in parent.children.values():
                parent.children.link(child)

    def copy_objects_and_data(self, collection: Collection):
        for object in collection.all_objects.values():
            self.copy_data(object)

        for object in collection.all_objects.values():
            if object.data:
                self.copy_data(object.data)

    def copy_data(self, data: ID) -> ID:
        if data in self.cache:
            return self.cache[data]

        if self.duplicate:
            self.cache[data] = data.copy()
        else:
            self.cache[data] = data.make_local()

        return self.cache[data]

    def replace_objects(self, collection: Collection):
        for object in collection.objects.values():
            collection.objects.unlink(object)
            collection.objects.link(self.cache.get(object, object))

        for child in collection.children.values():
            self.replace_objects(child)

    def update_objects(self, collection: Collection):
        for object in collection.all_objects.values():
            matrix = object.matrix_parent_inverse.copy()
            self.update_props(object)
            object.matrix_parent_inverse = matrix

    def update_props(self, data: ID):
        if data not in self.done:
            self.done.add(data)

            self.update_rna_props(data)
            self.update_custom_props(data)

    def update_rna_props(self, data: ID):
        for key, prop, value in self.get_rna_props(data):
            if prop.type == 'POINTER':
                if not prop.is_readonly and value in self.cache:
                    setattr(data, key, self.cache[value])
                elif not isinstance(value, ID):
                    self.update_props(value)

            elif prop.type == 'COLLECTION':
                for item in value:
                    if not isinstance(item, ID):
                        self.update_props(item)

    def get_rna_props(self, data: ID) -> Iterator[Tuple[str, Property, Any]]:
        if hasattr(data, 'bl_rna'):
            for key, prop in data.bl_rna.properties.items():
                prop: Property

                if key != 'rna_type':
                    if prop.type in ('POINTER', 'COLLECTION'):
                        yield key, prop, getattr(data, key)

    def update_custom_props(self, data: ID):
        for key, value in self.get_custom_props(data):
            if value in self.cache:
                data[key] = self.cache[value]
            elif not isinstance(value, ID):
                self.update_props(value)

    def get_custom_props(self, data: ID) -> Iterator[Tuple[str, Any]]:
        if hasattr(data, '__getitem__'):
            yield from data.items()

    def parent_objects(self, parent: Object, children: List[Object]):
        for child in children:
            if not child.parent:
                child.parent = parent

    def clear_instance(self, instance: Object):
        instance.instance_type = 'NONE'
        instance.instance_collection = None
        instance.empty_display_size = 0.1
