import re

import bpy


DUPLICATE_BONE_SUFFIX_RE = re.compile(r"\.\d+$")


def _bone_name_without_duplicate_suffix(bone_name):
    match = DUPLICATE_BONE_SUFFIX_RE.search(bone_name)
    if not match:
        return bone_name, False
    return bone_name[:match.start()], True


def fuse_armatures_into_base(context, base_armature, armatures_to_fuse):
    if not base_armature or base_armature.type != 'ARMATURE':
        return 0

    armatures = []
    for armature in [base_armature, *armatures_to_fuse]:
        if armature and armature.type == 'ARMATURE' and armature.name in bpy.data.objects and armature not in armatures:
            armatures.append(armature)

    if len(armatures) < 2:
        return 0

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    context.view_layer.objects.active = base_armature
    base_armature.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    original_bone_names = {bone.name for bone in base_armature.data.edit_bones}
    bpy.ops.object.mode_set(mode='OBJECT')

    for armature in armatures:
        armature.select_set(True)

    with context.temp_override(
        active_object=base_armature,
        selected_objects=armatures,
        selected_editable_objects=armatures,
    ):
        bpy.ops.object.join()

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = base_armature.data.edit_bones
    duplicate_bone_names = []

    for bone in edit_bones:
        base_bone_name, has_duplicate_suffix = _bone_name_without_duplicate_suffix(bone.name)
        if (
            has_duplicate_suffix
            and base_bone_name in original_bone_names
            and bone.name not in original_bone_names
        ):
            duplicate_bone_names.append(bone.name)

    for duplicate_bone_name in duplicate_bone_names:
        duplicate_bone = edit_bones.get(duplicate_bone_name)
        if not duplicate_bone:
            continue

        base_bone_name, _ = _bone_name_without_duplicate_suffix(duplicate_bone_name)
        base_bone = edit_bones.get(base_bone_name)

        if base_bone:
            for child_bone in list(duplicate_bone.children):
                _, child_has_duplicate_suffix = _bone_name_without_duplicate_suffix(child_bone.name)
                if not child_has_duplicate_suffix:
                    child_bone.parent = base_bone

        edit_bones.remove(duplicate_bone)

    bpy.ops.object.mode_set(mode='OBJECT')
    return len(duplicate_bone_names)

def collection_persona(context):
    def apply_pose_to_rest(armature_object):
        try:
            bpy.context.view_layer.objects.active = armature_object
            bpy.context.object.data.pose_position = 'REST'
            bpy.ops.object.posemode_toggle()
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.visual_transform_apply()
            bpy.context.object.data.pose_position = 'POSE'
            bpy.ops.object.posemode_toggle()
            return True
        except Exception as e:
            print(f"Error applying pose to rest pose: {e}")
            return False

    obj_rod = context.scene.set_character_target
    if not obj_rod:
        print("Parent object not found.")
        return

    selected_objects = [obj for obj in bpy.context.selected_objects if obj != obj_rod]

    if not selected_objects:
        print("Select at least one object to be parented.")
        return

    armatures_to_fuse = [obj for obj in selected_objects if obj.type == 'ARMATURE']
    non_armatures_to_remove = [obj for obj in selected_objects if obj.type != 'ARMATURE']

    for obj in selected_objects:
        obj_doch = obj.children
        valid_children = [child for child in obj_doch if child.type == 'MESH']

        if not valid_children:
            print(f"Object '{obj.name}' has no mesh children. Skipping.")
            continue

        for child in valid_children:
            for modifier in child.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.object = obj_rod

        for child in valid_children:
            child.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.select_all(action='DESELECT')

        bpy.context.view_layer.objects.active = obj_rod
        for child in valid_children:
            child.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.object.select_all(action='DESELECT')

    removed_duplicate_bones = fuse_armatures_into_base(context, obj_rod, armatures_to_fuse)

    for obj in non_armatures_to_remove:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj)

    if obj_rod.type == 'ARMATURE':
        if apply_pose_to_rest(obj_rod):
            print("Rest Pose converted to Pose Position for obj_rod.")
    else:
        print("obj_rod is not an armature. Rest Pose conversion skipped.")

    print(f"Parenting, fuse, and pose conversion complete. Removed duplicate bones: {removed_duplicate_bones}.")




class SetCharacterOperator(bpy.types.Operator):
    bl_idname = "object.set_character_operator"
    bl_label = "Собрать персонажа"

    def execute(self, context):
        obj_rod_name = context
        collection_persona(obj_rod_name)
        return {'FINISHED'}
