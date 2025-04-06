import bpy
import mathutils

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

    selected_objects = [obj for obj in bpy.context.selected_objects if obj.name != context]

    if not selected_objects:
        print("Select at least one object to be parented.")
        return

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

    for obj in selected_objects:
        bpy.data.objects.remove(obj)

    if obj_rod.type == 'ARMATURE':
        if apply_pose_to_rest(obj_rod):
            print("Rest Pose converted to Pose Position for obj_rod.")
    else:
        print("obj_rod is not an armature. Rest Pose conversion skipped.")

    print("Parenting, deletion, and pose conversion complete.")




class SetCharacterOperator(bpy.types.Operator):
    bl_idname = "object.set_character_operator"
    bl_label = "Объединить части"

    def execute(self, context):
        obj_rod_name = context
        collection_persona(obj_rod_name)
        return {'FINISHED'}