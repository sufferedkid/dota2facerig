import glob
import os
import subprocess

import bpy


def addon_root():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def default_texture_upscaler_root():
    return os.path.join(addon_root(), "texture_upscaler")


def default_ncnn_path():
    root = default_texture_upscaler_root()
    if os.name == "nt":
        return os.path.join(root, "win-bin.exe")
    return os.path.join(root, "linux-bin")


def default_models_path():
    return os.path.join(default_texture_upscaler_root(), "models")


def get_upscale_models(self=None, context=None):
    models_dir = default_models_path()
    if context:
        scene_models_dir = getattr(context.scene, "texture_upscale_models_path", "")
        if scene_models_dir:
            models_dir = bpy.path.abspath(scene_models_dir)

    param_files = glob.glob(os.path.join(models_dir, "*.param"))
    items = []
    for param_file in sorted(param_files):
        model_name = os.path.splitext(os.path.basename(param_file))[0]
        bin_file = os.path.join(models_dir, f"{model_name}.bin")
        if os.path.exists(bin_file):
            items.append((model_name, model_name, model_name))

    if not items:
        items.append(("realesrgan-x4plus", "realesrgan-x4plus", "Default model name"))
    return items


def selected_meshes(context):
    meshes = []

    def add_mesh_children(obj):
        for child in obj.children:
            if child.type == 'MESH':
                meshes.append(child)
            add_mesh_children(child)

    for obj in context.selected_objects:
        if obj.type == 'MESH':
            meshes.append(obj)
        add_mesh_children(obj)
    return list(dict.fromkeys(meshes))


def iter_image_nodes(meshes):
    for mesh in meshes:
        for material_slot in mesh.material_slots:
            material = material_slot.material
            if not material or not material.use_nodes or not material.node_tree:
                continue
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    yield material, node, node.image


def unique_selected_images(context):
    images = []
    seen_images = set()
    image_nodes = []
    for material, node, image in iter_image_nodes(selected_meshes(context)):
        if image.source == 'VIEWER':
            continue
        image_key = image.as_pointer()
        if image_key not in seen_images:
            images.append(image)
            seen_images.add(image_key)
        image_nodes.append((material, node, image))
    return images, image_nodes


def safe_color_space(image):
    try:
        return image.colorspace_settings.name
    except Exception:
        return None


def apply_color_space(image, color_space):
    if not color_space:
        return
    try:
        image.colorspace_settings.name = color_space
    except Exception:
        pass


def image_source_path(image, output_dir):
    source_path = bpy.path.abspath(image.filepath_raw or image.filepath)
    source_ext = os.path.splitext(source_path)[1].lower().lstrip(".")
    supported_input_formats = {"png", "jpg", "jpeg", "webp"}
    if source_path and os.path.exists(source_path) and source_ext in supported_input_formats:
        return source_path

    os.makedirs(output_dir, exist_ok=True)
    safe_name = bpy.path.clean_name(image.name)
    png_source_path = os.path.join(output_dir, f"{safe_name}_source.png")
    old_format = image.file_format
    try:
        image.file_format = 'PNG'
        image.save(filepath=png_source_path, quality=100)
    finally:
        image.file_format = old_format
    return png_source_path


def keep_aspect_resolution(image, target_resolution):
    width, height = image.size
    if width <= 0 or height <= 0:
        return target_resolution, target_resolution

    if width >= height:
        output_width = target_resolution
        output_height = max(1, round(target_resolution * height / width))
    else:
        output_width = max(1, round(target_resolution * width / height))
        output_height = target_resolution

    return output_width, output_height


def output_image_path(image, output_dir, output_width, output_height, output_format):
    source_name = bpy.path.clean_name(os.path.splitext(image.name)[0])
    extension = output_format.lower()
    if extension == "auto":
        extension = image.file_format.lower() or "png"
    if extension == "jpeg":
        extension = "jpg"
    return os.path.join(output_dir, f"{source_name}_{output_width}x{output_height}.{extension}")


def replace_nodes_for_selected_materials(image_nodes, old_image, new_image, color_space):
    apply_color_space(new_image, color_space)
    for _, node, node_image in image_nodes:
        if node_image == old_image:
            node.image = new_image


class TextureUpscaleSelectedOperator(bpy.types.Operator):
    bl_idname = "object.dota2_texture_upscale_selected"
    bl_label = "Апскейлить текстуры выделенного"
    bl_description = "Upscale image textures used by selected mesh objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(selected_meshes(context))

    def execute(self, context):
        scene = context.scene
        ncnn_path = bpy.path.abspath(scene.texture_upscale_ncnn_path)
        models_path = bpy.path.abspath(scene.texture_upscale_models_path)
        output_dir = bpy.path.abspath(scene.texture_upscale_output_path)
        target_resolution = scene.texture_upscale_target_resolution
        model_name = scene.texture_upscale_model
        output_format = scene.texture_upscale_output_format
        gpu = scene.texture_upscale_gpu

        if not os.path.exists(ncnn_path):
            self.report({'ERROR'}, f"NCNN binary not found: {ncnn_path}")
            return {'CANCELLED'}
        if not os.path.isdir(models_path):
            self.report({'ERROR'}, f"Models folder not found: {models_path}")
            return {'CANCELLED'}

        images, image_nodes = unique_selected_images(context)
        if not images:
            self.report({'ERROR'}, "Selected objects do not use image texture nodes.")
            return {'CANCELLED'}

        os.makedirs(output_dir, exist_ok=True)
        upscaled_count = 0

        for image in images:
            color_space = safe_color_space(image)
            try:
                source_path = image_source_path(image, output_dir)
            except Exception as error:
                self.report({'ERROR'}, f"Could not save source copy for {image.name}: {error}")
                return {'CANCELLED'}
            output_width, output_height = keep_aspect_resolution(image, target_resolution)
            new_path = output_image_path(image, output_dir, output_width, output_height, output_format)

            command = [
                ncnn_path,
                "-i", source_path,
                "-o", new_path,
                "-n", model_name,
                "-m", models_path,
                "-r", f"{output_width}x{output_height}",
            ]
            if output_format != "auto":
                command.extend(["-f", output_format])
            if gpu != "Auto":
                command.extend(["-g", gpu])

            try:
                process = subprocess.run(command, capture_output=True, text=True, check=False)
            except OSError as error:
                self.report({'ERROR'}, f"Could not run upscaler: {error}")
                return {'CANCELLED'}

            if process.returncode != 0 or not os.path.exists(new_path):
                print(process.stdout)
                print(process.stderr)
                self.report({'ERROR'}, f"Upscale failed for {image.name}")
                return {'CANCELLED'}

            upscaled_image = bpy.data.images.load(new_path, check_existing=True)
            replace_nodes_for_selected_materials(image_nodes, image, upscaled_image, color_space)
            upscaled_count += 1

        self.report({'INFO'}, f"Upscaled {upscaled_count} texture(s), long side {target_resolution}px.")
        return {'FINISHED'}
