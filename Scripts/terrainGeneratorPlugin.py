import bpy

bl_info = {
    "name": "",
    "description": "",
    "author": "",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "",
}


def main(context, loc):
    for ob in context.scene.objects:
        ob.location = loc


class TerrainGeneratorPlugin(bpy.types.Operator):

    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context, self.my_vec)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(
        TerrainGeneratorPlugin.bl_idname, icon='OUTLINER_OB_HAIR')


def register():
    bpy.utils.register_class(TerrainGeneratorPlugin)


def unregister():
    bpy.utils.unregister_class(TerrainGeneratorPlugin)


# if name == "main":
#     register()


# test call
# bpy.ops.object.TerrainGeneratorPlugin()
