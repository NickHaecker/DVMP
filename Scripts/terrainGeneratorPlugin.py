import bpy
from numpy import number
from skimage import io
import cv2
from colormap import rgb2hex


bl_info = {
    "name": "Terrain Generator",
    "description": "A Terrain will be generated out of a colored pattern.",
    "author": "Nick Philipp Häcker, Jasmin Meyer, Laura Moser, Violetta Pyralov",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Add > Terrain",
    "doc_url": "https://github.com/NickHaecker/DVMP",
    "tracker_url": "https://github.com/NickHaecker/DVMP",
    "category": "Add Mesh",
}


# def main(context, loc):
#     for ob in context.scene.objects:
#         ob.location = loc


class TerrainGeneratorPlugin(bpy.types.Operator):

    """Tooltip"""
    bl_idname = "terraingeneratorplugin.create_terrain"
    bl_label = "Terrain Generator"
    bl_description = "Generate Terrain"
    bl_options = {"REGISTER", "UNDO"}

    _patternPath: bpy.props.StringProperty(
        name="File Selection", description="Choose a File", default="", maxlen="1024", subtype="FILE_PATH")

    _patternWidth: number
    _patternHeight: number

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        # main(context, self.my_vec)
        if self._patternPath.endswith(".png"):
            pattern = io.imread(self._patternPath)
            if pattern:
                self._patternWidth = pattern.shape[0]
                self._patternHeight = pattern.shape[1]
            print(pattern)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(
        TerrainGeneratorPlugin.bl_idname, icon='OUTLINER_OB_HAIR')


def register():
    bpy.utils.register_class(TerrainGeneratorPlugin)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TerrainGeneratorPlugin)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


# if name == "main":
#     register()


# test call
# bpy.ops.object.TerrainGeneratorPlugin()
