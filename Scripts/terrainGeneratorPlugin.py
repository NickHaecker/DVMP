# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


# import string
import bpy
import cv2
from bpy_extras.io_utils import ImportHelper

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


class TerrainGeneratorPlugin(bpy.types.Operator, ImportHelper):
    bl_idname = "terraingeneratorplugin.create_terrain"
    bl_label = "Terrain Generator"
    bl_description = "Generate Terrain"
    bl_options = {"REGISTER", "UNDO"}

    _patternPath: bpy.props.StringProperty(
        name="File Selection", description="Choose a File", default="", maxlen="1024", subtype="FILE_PATH")

    _patternWidth: int
    _patternHeight: int
    _resizedPattern: any
    _rgb_pattern: any
    _convertPattern = '#%02x%02x%02x'

    def handle_pixel_color(self, x_position, y_position):
        color = self._rgb_pattern[y_position, x_position]
        colorInHex = self._convertPattern % (color[0], color[1], color[2])
        print(color)
        print(colorInHex)

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        pattern = cv2.imread(self.filepath)
        scale_percent = 120  # percent of original size
        self._patternWidth = int(
            pattern.shape[1] * scale_percent / 100)
        self._patternHeight = int(
            pattern.shape[0] * scale_percent / 100)
        self._resizedPattern = cv2.resize(
            pattern, (self._patternWidth,  self._patternHeight))
        self._rgb_pattern = self._resizedPattern[:, :, ::-1]
        for x in range(0, self._patternWidth, 1):
            for y in range(0, self._patternHeight, 1):
                self.handle_pixel_color(x, y)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(
        TerrainGeneratorPlugin.bl_idname, icon='MOD_FLUID')


def register():
    bpy.utils.register_class(TerrainGeneratorPlugin)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TerrainGeneratorPlugin)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
