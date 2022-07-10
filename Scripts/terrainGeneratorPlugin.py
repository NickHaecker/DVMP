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
import os
import cv2
import random
from bpy_extras.io_utils import ImportHelper
from typing import List, Dict

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

green = (0, 255, 0)
darkGreen = (53, 101, 20)
brown = (143, 86, 59)
blue = (0, 0, 255)

# Umwandlung RGB in Hex

# convert to hex
conv2hex = '#%02x%02x%02x'

conv2hexGreen = conv2hex % green
conv2hexDarkGreen = conv2hex % darkGreen
conv2hexBrown = conv2hex % brown
conv2hexBlue = conv2hex % blue


class ColorData:
    hex: str
    name: str
    import_path: str


colorMap: Dict[str, ColorData] = {
    "green": {
        "hex": conv2hexGreen,
        "import_path": "E:/athaeck/Projekte/DVMP/Exports/Gras",
        "name": "Gras"
    },
    "darkGreen": {
        "hex": conv2hexDarkGreen,
        "name": "Busch",
        "import_path": "E:/athaeck/Projekte/DVMP/Exports/Bush"
    },
    "brown": {
        "hex": conv2hexBrown,
        "name": "Baum",
        "import_path": "E:/athaeck/Projekte/DVMP/Exports/Tree",
    },
    "blue": {
        "hex": conv2hexBlue,
        "name": "Stein",
        "import_path": "E:/athaeck/Projekte/DVMP/Exports/Stone",
    },
    "white": {
        "hex": "#ffffff",
        "name": "",
        "import_path": "",
    }
}


def handle_color_map(hex: str) -> ColorData:
    current: ColorData = None
    for key in colorMap:
        curr: ColorData = colorMap[key]
        _hex: str = curr["hex"]
        if _hex == hex:
            current = curr
    return current


def refresh():
    # select and del all object
    bpy.ops.object.select_all(action='SELECT')  # selektiert alle Objekte
    # löscht selektierte objekte
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc.


def init_scene_structure() -> None:
    import_models: bpy.types.Collection = bpy.data.collections.new("Models")
    bpy.context.scene.collection.children.link(import_models)
    planes: bpy.types.Collection = bpy.data.collections.new("Ground")
    bpy.context.scene.collection.children.link(planes)
    import_models.hide_viewport = True


id: int = 0


class PixelResolve:
    _color: ColorData
    _translation_x: int
    _translation_y: int
    _plugin: any
    _fbx: bpy.types.Object
    _plane: bpy.types.Object

    def __init__(self, color: ColorData, translation_x: int, translation_y: int, plugin) -> None:
        self._color = color
        self._translation_x = translation_x
        self._translation_y = translation_y
        self._plugin = plugin
        self.import_model()
        self.init_plane()
        self.handle_nodes()
        # i = i+1

    def import_model(self) -> None:
        if len(self._color["import_path"]) > 0:
            dir_list = os.listdir(self._color["import_path"])
            random_entry: int = random.randint(0, len(dir_list)-1)
            new_fbx: str = dir_list[random_entry]
            new_fbx_name: str = new_fbx.split(".")[0]

            self._fbx = bpy.context.scene.objects.get(new_fbx_name)
            if self._fbx is None:
                bpy.ops.import_scene.fbx(
                    filepath=self._color["import_path"] + "/" + new_fbx)
                self._fbx = bpy.context.scene.objects.get(new_fbx_name)
                bpy.ops.object.move_to_collection(collection_index=2)

# self._plugin.scale

    def init_plane(self) -> None:
        bpy.ops.mesh.primitive_plane_add(
            size=2, enter_editmode=False, align='WORLD', location=(self._translation_x * self._plugin._scale, self._translation_y * self._plugin._scale, 0), scale=(1, 1, 1))
        name: str = "Plane" + "_" + \
            str(self._translation_x) + "_" + str(self._translation_y)
        bpy.context.selected_objects[0].name = name
        self._plane = bpy.context.scene.objects.get(name)
        bpy.ops.object.move_to_collection(collection_index=3)

    def handle_nodes(self) -> None:
        self._plane.modifiers.new("Geometry Nodes", "NODES")
        bpy.ops.node.new_geometry_node_group_assign()
        node_group = bpy.context.object.modifiers[0].node_group
        nodes = node_group.nodes

        grid: bpy.types.Node = nodes.new(type="GeometryNodeMeshGrid")
        grid.location.x += 100
        grid.location.y += 200

        setPos: bpy.types.Node = nodes.new(type="GeometryNodeSetPosition")
        setPos.location.x += 500
        setPos.location.y += 150

        setShadeSmooth: bpy.types.Node = nodes.new(
            type="GeometryNodeSetShadeSmooth")
        setShadeSmooth.location.x += 700
        setShadeSmooth.location.y += 100

        joinGeometry: bpy.types.Node = nodes.new(
            type="GeometryNodeJoinGeometry")
        joinGeometry.location.x += 1350
        joinGeometry.location.y += 100

        pointsOnFaces: bpy.types.Node = nodes.new(
            type="GeometryNodeDistributePointsOnFaces")
        pointsOnFaces.location.x += 900
        pointsOnFaces.location.y -= 60

        instanceOnFaces: bpy.types.Node = nodes.new(
            type="GeometryNodeInstanceOnPoints")
        instanceOnFaces.location.x += 1150
        instanceOnFaces.location.y -= 60

        nodeObjInfo: bpy.types.Node = nodes.new(
            type="GeometryNodeObjectInfo")
        nodeObjInfo.location.x += 1150
        nodeObjInfo.location.y -= 60

        nodes["Group Output"].location.x += 1400
        nodes["Group Output"].location.y += 100

        grid.inputs[0].default_value = self._plugin._scale
        # self._plugin.scale
        grid.inputs[1].default_value = self._plugin._scale
        # self._plugin.scale
        grid.inputs[2].default_value = 32
        grid.inputs[3].default_value = 32

        pointsOnFaces.inputs[3].default_value = 1
        pointsOnFaces.inputs[4].default_value = 0.5
        pointsOnFaces.inputs[6].default_value = random.randint(-150, 150)

        # instanceOnFaces.inputs[6].default_value[0] = 0.01
        # instanceOnFaces.inputs[6].default_value[1] = 0.01
        # instanceOnFaces.inputs[6].default_value[2] = 0.01

        nodeObjInfo.inputs[0].default_value = self._fbx

        links = node_group.links

        links.new(nodes["Grid"].outputs["Mesh"],
                  setPos.inputs["Geometry"])
        links.new(nodes["Set Position"].outputs["Geometry"],
                  setShadeSmooth.inputs["Geometry"])
        links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
                  joinGeometry.inputs["Geometry"])
        links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
                  pointsOnFaces.inputs["Mesh"])
        links.new(nodes["Distribute Points on Faces"].outputs["Points"],
                  instanceOnFaces.inputs["Points"])
        links.new(nodes["Object Info"].outputs["Geometry"],
                  instanceOnFaces.inputs["Instance"])
        links.new(nodes["Instance on Points"].outputs["Instances"],
                  joinGeometry.inputs["Geometry"])
        links.new(nodes["Join Geometry"].outputs["Geometry"],
                  nodes["Group Output"].inputs["Geometry"])


class TerrainGeneratorPlugin(bpy.types.Operator, ImportHelper):
    bl_idname = "terraingeneratorplugin.create_terrain"
    bl_label = "Terrain Generator"
    bl_description = "Generate Terrain"
    bl_options = {"REGISTER", "UNDO"}

    patternPath: bpy.props.StringProperty(
        name="File Selection", description="Choose a File", default="", maxlen="1024", subtype="FILE_PATH")

    _patternWidth: int
    _patternHeight: int
    _resizedPattern: any
    _rgb_pattern: any
    _resolvedPattern: List[PixelResolve] = []
    _collections: Dict[str, bpy.types.Collection]
    _scale: int = 10

    def handle_pixel_color(self, x_position, y_position):
        color = self._rgb_pattern[y_position, x_position]
        colorInHex = conv2hex % (color[0], color[1], color[2])
        current: ColorData = handle_color_map(
            colorInHex)
        if current != None:
            self._resolvedPattern.append(
                PixelResolve(current, x_position, y_position, self))

    @classmethod
    def poll(cls, context):
        # löscht überbleibende Meshdaten etc.
        bpy.ops.outliner.orphans_purge()

    def execute(self, context):
        pattern = cv2.imread(self.filepath)
        refresh()
        init_scene_structure()
        scale_percent = 100  # percent of original size
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
