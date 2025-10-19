import bpy

from .operators.set_character import SetCharacterOperator
from .operators.face_rig import FaceRigOperator

bl_info = {
    "name": "Dota2Tools",
    "author": "sufferedkid",
    "version": (0, 2),
    "blender": (4, 2, 3),
    "location": "View - Tools",
    "description": "Tools for work with Dota 2 Models",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UI",
}

bpy.types.Scene.face_rig_target = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Scene.set_character_target = bpy.props.PointerProperty(type=bpy.types.Object)


class ToolsPanel(bpy.types.Panel):
    bl_label = "Dota2Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dota2Tools"

    def draw(self, context):
        character_build = self.layout

        character_build_row = character_build.box()
        character_build_row.label(text="Сборка персонажа", icon="MOD_BUILD")
        character_build_row.label(text="Кости предметов удалятся!", icon="ERROR")

        character_build_row.label(text="1. Выберите главную модель", icon="INFO")
        character_build_row.prop_search(context.scene, "set_character_target", context.scene, "objects", text="")

        character_build_row.label(text="2. Выделите части сета/персонажа", icon="INFO")
        character_build_row.operator("object.set_character_operator")


        face_rig_build = self.layout

        face_rig_build_box = face_rig_build.box()
        face_rig_build_box.label(text="Создание фейс-рига", icon="MOD_BUILD")

        face_rig_build_box.label(text="Выберите модель головы", icon="INFO")
        face_rig_build_box.prop_search(context.scene, "face_rig_target", context.scene, "objects", text="")

        face_rig_build_box.operator("object.face_rig_operator")


classes = (
    SetCharacterOperator,
    FaceRigOperator,
    ToolsPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()