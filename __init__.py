import bpy

from .operators.set_character import SetCharacterOperator
from .operators.face_rig import FaceRigOperator
from .operators.texture_upscale import (
    TextureUpscaleSelectedOperator,
    default_models_path,
    default_ncnn_path,
    get_upscale_models,
)

bl_info = {
    "name": "Dota2Tools",
    "author": "sufferedkid",
    "version": (0, 3),
    "blender": (4, 2, 3),
    "location": "View - Tools",
    "description": "Tools for work with Dota 2 Models",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UI",
}

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

        texture_upscale_box = self.layout.box()
        texture_upscale_box.label(text="Апскейл текстур", icon="TEXTURE")
        texture_upscale_box.label(text="Выделите модели с нужными материалами", icon="INFO")
        texture_upscale_box.prop(context.scene, "texture_upscale_target_resolution")
        texture_upscale_box.prop(context.scene, "texture_upscale_model")
        texture_upscale_box.prop(context.scene, "texture_upscale_output_format")
        texture_upscale_box.prop(context.scene, "texture_upscale_gpu")
        texture_upscale_box.prop(context.scene, "texture_upscale_ncnn_path")
        texture_upscale_box.prop(context.scene, "texture_upscale_models_path")
        texture_upscale_box.prop(context.scene, "texture_upscale_output_path")
        texture_upscale_box.operator("object.dota2_texture_upscale_selected")


classes = (
    SetCharacterOperator,
    FaceRigOperator,
    TextureUpscaleSelectedOperator,
    ToolsPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.face_rig_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.set_character_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.texture_upscale_target_resolution = bpy.props.IntProperty(
        name="Длинная сторона",
        description="Target size for the longest texture side while keeping aspect ratio",
        default=4096,
        min=256,
        max=16384,
        subtype='PIXEL',
    )
    bpy.types.Scene.texture_upscale_model = bpy.props.EnumProperty(
        name="Модель",
        description="NCNN upscale model",
        items=get_upscale_models,
    )
    bpy.types.Scene.texture_upscale_output_format = bpy.props.EnumProperty(
        name="Формат",
        description="Output image format",
        items=[
            ("auto", "Auto", "Use source image format"),
            ("png", "PNG", "PNG"),
            ("jpg", "JPG", "JPG"),
            ("webp", "WEBP", "WEBP"),
        ],
        default="png",
    )
    bpy.types.Scene.texture_upscale_gpu = bpy.props.EnumProperty(
        name="GPU",
        description="GPU device passed to the upscaler",
        items=[
            ("Auto", "Auto", "Let the upscaler choose"),
            ("0", "Device 0", "Device 0"),
            ("1", "Device 1", "Device 1"),
            ("2", "Device 2", "Device 2"),
        ],
        default="Auto",
    )
    bpy.types.Scene.texture_upscale_ncnn_path = bpy.props.StringProperty(
        name="NCNN",
        description="Path to Texture_Upscaler executable",
        default=default_ncnn_path(),
        subtype='FILE_PATH',
    )
    bpy.types.Scene.texture_upscale_models_path = bpy.props.StringProperty(
        name="Models",
        description="Folder with .param/.bin upscaler models",
        default=default_models_path(),
        subtype='DIR_PATH',
    )
    bpy.types.Scene.texture_upscale_output_path = bpy.props.StringProperty(
        name="Output",
        description="Folder for upscaled textures",
        default="//upscaled_textures",
        subtype='DIR_PATH',
    )


def unregister():
    if hasattr(bpy.types.Scene, "set_character_target"):
        del bpy.types.Scene.set_character_target
    if hasattr(bpy.types.Scene, "face_rig_target"):
        del bpy.types.Scene.face_rig_target
    if hasattr(bpy.types.Scene, "texture_upscale_output_path"):
        del bpy.types.Scene.texture_upscale_output_path
    if hasattr(bpy.types.Scene, "texture_upscale_models_path"):
        del bpy.types.Scene.texture_upscale_models_path
    if hasattr(bpy.types.Scene, "texture_upscale_ncnn_path"):
        del bpy.types.Scene.texture_upscale_ncnn_path
    if hasattr(bpy.types.Scene, "texture_upscale_gpu"):
        del bpy.types.Scene.texture_upscale_gpu
    if hasattr(bpy.types.Scene, "texture_upscale_output_format"):
        del bpy.types.Scene.texture_upscale_output_format
    if hasattr(bpy.types.Scene, "texture_upscale_model"):
        del bpy.types.Scene.texture_upscale_model
    if hasattr(bpy.types.Scene, "texture_upscale_target_resolution"):
        del bpy.types.Scene.texture_upscale_target_resolution

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
