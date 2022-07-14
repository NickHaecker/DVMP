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
        "import_path": "C:/Users/meyer/OneDrive/Desktop/DVMP/Exports/Gras",
        "name": "Gras"
    },
    "darkGreen": {
        "hex": conv2hexDarkGreen,
        "name": "Busch",
        "import_path": "C:/Users/meyer/OneDrive/Desktop/DVMP/Exports/Bush"
    },
    "brown": {
        "hex": conv2hexBrown,
        "name": "Baum",
        "import_path": "C:/Users/meyer/OneDrive/Desktop/DVMP/Exports/Tree",
    },
    "blue": {
        "hex": conv2hexBlue,
        "name": "Stein",
        "import_path": "C:/Users/meyer/OneDrive/Desktop/DVMP/Exports/Stone",
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

    def plane_texture(self) -> bpy.types.Material:
        mat: bpy.types.Material = bpy.data.materials.new(
            "Base Plane Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.images.load(
            "C:/athaeck/DVMP/Pattern/grass_tex_dark.jpg")
        mat.node_tree.links.new(
            bsdf.inputs['Base Color'], texImage.outputs['Color'])

        return mat

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

    def init_plane(self) -> None:
        bpy.ops.mesh.primitive_plane_add(
            size=2, enter_editmode=False, align='WORLD', location=(self._translation_x * self._plugin._scale, - self._translation_y * self._plugin._scale, 0), scale=(1, 1, 1))
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

        currObjectNode: bpy.types.Node = nodes.new(
            type="GeometryNodeObjectInfo")
        currObjectNode.location.x += 0
        currObjectNode.location.y -= 60

        currObjectNode.inputs[0].default_value = self._plane

        currPos: bpy.types.Node = nodes.new(
            type="GeometryNodeInputPosition")
        currPos.location.x += 0
        currPos.location.y -= 200

        vecAdd: bpy.types.Node = nodes.new(
            type="ShaderNodeVectorMath")
        vecAdd.location.x += 0
        vecAdd.location.y -= 100

        noise: bpy.types.Node = nodes.new(type="ShaderNodeTexNoise")
        noise.location.x -= 100
        noise.location.y -= 50

        noise.inputs[2].default_value = 0.54
        noise.inputs[3].default_value = 2.000
        noise.inputs[4].default_value = 0.5

        comXYZ: bpy.types.Node = nodes.new(type="ShaderNodeCombineXYZ")
        comXYZ.location.x += 300
        comXYZ.location.y -= 60

        setPos: bpy.types.Node = nodes.new(type="GeometryNodeSetPosition")
        setPos.location.x += 500
        setPos.location.y += 150

        joinGrid: bpy.types.Node = nodes.new(
            type="GeometryNodeJoinGeometry")
        joinGrid.location.x += 100
        joinGrid.location.y += 100

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
        pointsOnFaces.distribute_method = 'POISSON'
        pointsOnFaces.location.x += 900
        pointsOnFaces.location.y -= 60

        setMaterial: bpy.types.Node = nodes.new(
            type="GeometryNodeSetMaterial")
        setMaterial.inputs[2].default_value = self.plane_texture()

        instanceOnFaces: bpy.types.Node = nodes.new(
            type="GeometryNodeInstanceOnPoints")
        instanceOnFaces.location.x += 1150
        instanceOnFaces.location.y -= 60

        nodeObjInfo: bpy.types.Node = nodes.new(
            type="GeometryNodeObjectInfo")
        nodeObjInfo.location.x += 1150
        nodeObjInfo.location.y -= 60

        randomValue: bpy.types.Node = nodes.new(
            type="FunctionNodeRandomValue")
        randomValue.data_type = 'FLOAT_VECTOR'
        randomValue.inputs[0].default_value[2] = -360
        randomValue.inputs[1].default_value[2] = 360
        randomValue.inputs[1].default_value[1] = 0
        randomValue.inputs[1].default_value[0] = 0

        randomValueS: bpy.types.Node = nodes.new(
            type="FunctionNodeRandomValue")
        randomValueS.data_type = 'FLOAT_VECTOR'
        randomValueS.inputs[0].default_value[2] = 0.5
        randomValueS.inputs[0].default_value[1] = 1
        randomValueS.inputs[0].default_value[0] = 1
        randomValueS.inputs[1].default_value[2] = 1.5
        randomValueS.inputs[1].default_value[1] = 1
        randomValueS.inputs[1].default_value[0] = 1

        nodes["Group Output"].location.x += 1400
        nodes["Group Output"].location.y += 100

        grid.inputs[0].default_value = self._plugin._scale
        grid.inputs[1].default_value = self._plugin._scale
        grid.inputs[2].default_value = 32
        grid.inputs[3].default_value = 32

        distance_min: int
        density_max: int
        density_factor: int

        if self._color["name"] == "Busch":
            distance_min = 1
            density_max = 1
            density_factor = 0.8

        elif self._color["name"] == "Gras":

            distance_min = 1
            density_max = 1
            density_factor = 1

        elif self._color["name"] == "Baum":

            distance_min = 1.4
            density_max = 1.2
            density_factor = 0.453

        elif self._color["name"] == "Stein":

            distance_min = 4
            density_max = 3
            density_factor = 0.4

        else:
            distance_min = 2
            density_max = 0.5
            density_factor = 0.380

        pointsOnFaces.inputs[2].default_value = distance_min
        pointsOnFaces.inputs[3].default_value = density_max
        pointsOnFaces.inputs[5].default_value = density_factor
        pointsOnFaces.inputs[6].default_value = random.randint(-150, 150)

        nodeObjInfo.inputs[0].default_value = self._fbx

        links = node_group.links

        links.new(nodes["Grid"].outputs["Mesh"],
                  joinGrid.inputs["Geometry"])
        links.new(joinGrid.outputs["Geometry"],
                  setPos.inputs["Geometry"])
        links.new(nodes["Group Input"].outputs["Geometry"],
                  joinGrid.inputs["Geometry"])
        links.new(nodes["Set Position"].outputs["Geometry"],
                  setShadeSmooth.inputs["Geometry"])
        links.new(nodes["Combine XYZ"].outputs["Vector"],
                  setPos.inputs["Offset"])
        links.new(nodes["Noise Texture"].outputs["Fac"],
                  comXYZ.inputs["Z"])
        links.new(vecAdd.outputs["Vector"],
                  noise.inputs["Vector"])
        links.new(currPos.outputs["Position"],
                  vecAdd.inputs[1])
        links.new(currObjectNode.outputs["Location"],
                  vecAdd.inputs[0])
        links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
                  setMaterial.inputs["Geometry"])
        links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
                  pointsOnFaces.inputs["Mesh"])
        links.new(nodes["Distribute Points on Faces"].outputs["Points"],
                  instanceOnFaces.inputs["Points"])
        links.new(nodeObjInfo.outputs["Geometry"],
                  instanceOnFaces.inputs["Instance"])
        links.new(nodes["Instance on Points"].outputs["Instances"],
                  joinGeometry.inputs["Geometry"])
        links.new(nodes["Set Material"].outputs["Geometry"],
                  joinGeometry.inputs["Geometry"])
        links.new(randomValue.outputs["Value"],
                  instanceOnFaces.inputs["Rotation"])
        links.new(randomValueS.outputs["Value"],
                  instanceOnFaces.inputs["Scale"])

        links.new(joinGeometry.outputs["Geometry"],
                  nodes["Group Output"].inputs["Geometry"])


class TerrainGeneratorPlugin(bpy.types.Operator, ImportHelper):
    """Tooltip"""
    bl_idname = "terraingeneratorplugin.create_terrain"
    bl_label = "Terrain Generator"
    bl_description = "Generate Terrain"
    bl_options = {"REGISTER", "UNDO"}
    bl_context = "scene"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    PATTERN_PATH: bpy.props.StringProperty(
        name="Pattern Selection", description="Choose Pattern", subtype="FILE_PATH", default="")

    GRASS_PATH: bpy.props.StringProperty(
        name="Grass Folder Selection", description="Choose Grass Path", subtype="DIR_PATH", default="")

    BUSH_PATH: bpy.props.StringProperty(
        name="Bush Folder Selection", description="Choose Bush Path", subtype="DIR_PATH", default="")

    TREE_PATH: bpy.props.StringProperty(
        name="Tree Folder Selection", description="Choose Tree Path", subtype="DIR_PATH", default="")

    STONE_PATH: bpy.props.StringProperty(
        name="Stone Folder Selection", description="Choose Stone Path", subtype="DIR_PATH", default="")

    WIDTH_BASE: bpy.props.FloatProperty(name="Base Width", default=0.01, min=0)

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
        return context.mode == "OBJECT"

    def execute(self, context):
        pattern = cv2.imread(self.filepath)

        # green = colorMap["green"]
        # green["import_path"] = self.GRASS_PATH

        # darkGreen = colorMap["darkGreen"]
        # darkGreen["import_path"] = self.BUSH_PATH

        # brown = colorMap["brown"]
        # brown["import_patch"] = self.TREE_PATH

        # blue = colorMap["blue"]
        # blue["import_path"] = self.STONE_PATH

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
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TerrainGeneratorPlugin)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)
