import os
import bpy
from typing import List, Dict
import random
# from terrainGeneratorPlugin import PixelResolve, ColorData, init_scene_structure
# select and del all object
bpy.ops.object.select_all(action='SELECT')  # selektiert alle Objekte
# löscht selektierte objekte
bpy.ops.object.delete(use_global=False, confirm=False)
bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc.

green = (0, 255, 0)
darkGreen = (53, 101, 20)
brown = (143, 86, 59)
blue = (0, 0, 255)

conv2hex = '#%02x%02x%02x'

conv2hexGreen = conv2hex % green
conv2hexDarkGreen = conv2hex % darkGreen
conv2hexBrown = conv2hex % brown
conv2hexBlue = conv2hex % blue


class ColorData:
    handler: str
    hex: str
    name: str
    import_path: str


def init_scene_structure() -> Dict[str, bpy.types.Collection]:
    import_models: bpy.types.Collection = bpy.data.collections.new("Models")
    planes: bpy.types.Collection = bpy.data.collections.new("Ground")
    import_models.hide_viewport = True
    return {
        "models": import_models,
        "ground": planes
    }


test: ColorData = {
    "handler": "blue",
    "hex": conv2hexBlue,
    "name": "Stein",
    "import_path": "E:/athaeck/Projekte/DVMP/Exports/Stone",
}
o = init_scene_structure()
print(o)


class PixelResolve:
    _color: ColorData
    _translation_x: int
    _translation_y: int
    _plugin: any
    _fbx: bpy.types.Object
    _plane: bpy.types.Object

    def __init__(self, color: ColorData, translation_x: int, translation_y: int, plugin) -> None:
        print(color)
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
                self._fbx = bpy.context.object
                bpy.data.collections["Models"].objects.link(self._fbx)

# self._plugin.scale

    def init_plane(self) -> None:
        bpy.ops.mesh.primitive_plane_add(
            size=2, enter_editmode=False, align='WORLD', location=(self._translation_x-1 * 10/2, self._translation_y-1 * 10/2, 0), scale=(1, 1, 1))
        self._plane = bpy.context.object
        bpy.data.collections["Ground"].objects.link(self._plane)

    def handle_nodes(self) -> None:
        self._plane.modifier_add(type='NODES')
        node_group = self._plane.modifiers[0].node_group
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
            type="GeometryNodeObjectInfoNode")
        nodeObjInfo.location.x += 1150
        nodeObjInfo.location.y -= 60

        nodes["Group Output"].location.x += 1400
        nodes["Group Output"].location.y += 100

        grid.inputs[0].default_value = 10
        # self._plugin.scale
        grid.inputs[1].default_value = 10
        # self._plugin.scale
        grid.inputs[2].default_value = 32
        grid.inputs[3].default_value = 32

        pointsOnFaces.inputs[3].default_value = 1
        pointsOnFaces.inputs[4].default_value = 0.5

        nodeObjInfo.inputs[0].default_value = self._fbx

        links = node_group.links

        links.new(nodes["Grid"].outputs["Mesh"],
                  setPos.inputs["Geometry"])
        links.new(nodes["Set Position"].outputs["Geometry"],
                  setShadeSmooth.inputs["Geometry"])
        links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
                  joinGeometry.inputs["Geometry"])
        links.new(nodes["Combine XYZ"].outputs["Vector"],
                  setPos.inputs["Offset"])
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


for x in range(0, 100, 1):
    for y in range(0, 100, 1):
        PixelResolve(test, x, y, None)

# add plane
# bpy.ops.mesh.primitive_plane_add(
#     size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

# # add GeometryNodes modifier
# bpy.ops.object.modifier_add(type='NODES')

# # access active object node_group
# node_group = bpy.context.object.modifiers[0].node_group


# # add nodes
# nodes = node_group.nodes
# grid: bpy.types.Node = nodes.new(type="GeometryNodeMeshGrid")
# grid.location.x += 100
# grid.location.y += 200


# setPos: bpy.types.Node = nodes.new(type="GeometryNodeSetPosition")
# setPos.location.x += 500
# setPos.location.y += 150


# setShadeSmooth: bpy.types.Node = nodes.new(type="GeometryNodeSetShadeSmooth")
# setShadeSmooth.location.x += 700
# setShadeSmooth.location.y += 100


# joinGeometry: bpy.types.Node = nodes.new(type="GeometryNodeJoinGeometry")
# joinGeometry.location.x += 1350
# joinGeometry.location.y += 100

# noise: bpy.types.Node = nodes.new(type="ShaderNodeTexNoise")
# noise.location.x -= 100
# noise.location.y -= 50

# mapRange: bpy.types.Node = nodes.new(type="ShaderNodeMapRange")
# mapRange.location.x += 100
# mapRange.location.y -= 50

# comXYZ: bpy.types.Node = nodes.new(type="ShaderNodeCombineXYZ")
# comXYZ.location.x += 300
# comXYZ.location.y -= 60

# pointsOnFaces: bpy.types.Node = nodes.new(
#     type="GeometryNodeDistributePointsOnFaces")
# pointsOnFaces.location.x += 900
# pointsOnFaces.location.y -= 60

# instanceOnFaces: bpy.types.Node = nodes.new(
#     type="GeometryNodeInstanceOnPoints")
# instanceOnFaces.location.x += 1150
# instanceOnFaces.location.y -= 60


# nodeColInfo: bpy.types.Node = nodes.new(type="GeometryNodeObjectInfoNode")
# nodeColInfo.location.x += 0
# nodeColInfo.location.y -= 0


# nodes["Group Output"].location.x += 1400
# nodes["Group Output"].location.y += 100


# # change inputs
# # grid
# grid.inputs[0].default_value = 10
# grid.inputs[1].default_value = 10
# grid.inputs[2].default_value = 64
# grid.inputs[3].default_value = 64

# # noise Texture
# noise.inputs[2].default_value = 0.290
# noise.inputs[3].default_value = 5.000
# noise.inputs[4].default_value = 0.325

# # Distribute Points on Faces
# pointsOnFaces.inputs[4].default_value = 2.5

# # Map Range
# mapRange.inputs[3].default_value = -1.600
# mapRange.inputs[4].default_value = 1.800

# # Collection Info
# grassCollection: bpy.types.Collection = None
# if "Grass" in bpy.data.collections:
#     grassCollection = bpy.data.collections["Grass"]
# else:
#     grassCollection = bpy.data.collections.new("Grass")
# try:
#     bpy.context.scene.collection.children.link(grassCollection)
# except:
#     ...

# # bpy.ops.import_scene.fbx(
# #     filepath="E:/athaeck/Projekte/DVMP/Exports/Gras/Gras.fbx")
# # grassCollection.objects.link(

# # )
# nodeColInfo.inputs[0].default_value = grassCollection
# nodeColInfo.inputs[2].default_value = True
# # Exports\Gras\Gras.fbx
# # E: \athaeck\Projekte\DVMP\Exports\Gras\Gras.fbx

# # connect
# links = node_group.links

# # links.new(nodes["Group Input"].outputs["size_y"],       meshline_1.inputs["Count"])
# links.new(nodes["Grid"].outputs["Mesh"],
#           setPos.inputs["Geometry"])
# links.new(nodes["Set Position"].outputs["Geometry"],
#           setShadeSmooth.inputs["Geometry"])
# links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
#           joinGeometry.inputs["Geometry"])
# links.new(nodes["Noise Texture"].outputs["Fac"],
#           mapRange.inputs["Value"])
# links.new(nodes["Map Range"].outputs["Result"],
#           comXYZ.inputs["Z"])
# links.new(nodes["Combine XYZ"].outputs["Vector"],
#           setPos.inputs["Offset"])
# links.new(nodes["Set Shade Smooth"].outputs["Geometry"],
#           pointsOnFaces.inputs["Mesh"])
# links.new(nodes["Distribute Points on Faces"].outputs["Points"],
#           instanceOnFaces.inputs["Points"])
# links.new(nodes["Collection Info"].outputs["Geometry"],
#           instanceOnFaces.inputs["Instance"])
# links.new(nodes["Instance on Points"].outputs["Instances"],
#           joinGeometry.inputs["Geometry"])
# links.new(nodes["Join Geometry"].outputs["Geometry"],
#           nodes["Group Output"].inputs["Geometry"])
