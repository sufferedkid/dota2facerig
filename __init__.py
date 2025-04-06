import bpy

from .operators.set_character import SetCharacterOperator
from .operators.face_rig import FaceRigOperator

bl_info = {
    "name": "Dota2Tools",
    "author": "sufferedkid",
    "version": (0, 1),
    "blender": (4, 2, 3),
    "location": "File > Export > Dota2Tools",
    "description": "Tools for work with Dota 2 Models",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export",
}

bpy.types.Scene.face_rig_target = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Scene.set_character_target = bpy.props.PointerProperty(type=bpy.types.Object)


class ToolsPanel(bpy.types.Panel):
    bl_label = "Dota 2 Tools"
    bl_idname = "OBJECT_PT_my_addon"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dota 2 Tools"

    def draw(self, context):
        row = self.layout

        row.emboss = "PULLDOWN_MENU"

        set_character_box = row.box()
        set_character_box.label(text="Объединение частей:")
        set_character_box.prop_search(context.scene, "set_character_target", context.scene, "objects", text="Select Object")
        set_character_box.operator("object.set_character_operator")

        face_rig_box = row.box()
        face_rig_box.label(text="Face Rig:")
        face_rig_box.prop_search(context.scene, "face_rig_target", context.scene, "objects", text="Select Object")
        face_rig_box.operator("object.face_rig_operator")


classes = (
    SetCharacterOperator,
    FaceRigOperator,
    ToolsPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)


if __name__ == "__main__":
    register()
