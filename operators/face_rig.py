import math

import bpy

# Переменные для размеров
child_shape_size = 0.005
parent_shape_size = 0.01

# ----------------------------------------------------------------------------
# 1) Координаты для обычных (не stereo) Shape Keys
# ----------------------------------------------------------------------------

face_positions = {
    "Main Empty": {
        "location": (0.00, 0.00, 0.00)
    },
    "Brows": {
        "location": (0.025, 0.00, 0.205),
        "scale": (0.095, 0.0001, 0.020),
        "positions": {
            "innerBrowRaiser": (0.00, 0.00, 0.20),
            "outerBrowRaiser": (0.05, 0.00, 0.20),
            "browLowerer": (-0.05, 0.00, 0.20),
        }
    },
    "Eyes": {
        "location": (0.025, 0.0, 0.1325),
        "scale": (0.095, 0.0001, 0.050),
        "positions": {
            "eyeDown": (0.1, 0.00, 0.165),
            "eyeClosed": (0.1, 0.00, 0.145),
            "squint": (0.1, 0.00, 0.105),
            "cheekRaiser": (0.00, 0.00, 0.1),
            "upperLidRaiser": (0.00, 0.00, 0.165),
            "Stereo": {
                "left_eye_shapes": {
                    "location": (0.03, 0.0, 0.135),
                    "left_eyeDown_stereo": "down",
                    "left_eyeUp_stereo": "up",
                    "left_eyeLeft_stereo": "right",
                    "left_eyeRight_stereo": "left",
                },
                "right_eye_shapes": {
                    "location": (-0.03, 0.0, 0.135),
                    "right_eyeDown_stereo": "down",
                    "right_eyeUp_stereo": "up",
                    "right_eyeLeft_stereo": "right",
                    "right_eyeRight_stereo": "left",
                },
            }
        },
        "Unified": {
            "eyeSideways": {
                "left": "eyeLeft",
                "right": "eyeRight",
                "pos": (0.10, 0.00, 0.125)  # где будет располагаться контроллер на лице
            }
        }
    },
    "Nose": {
        "location": (0.025, 0.0, 0.05),
        "scale": (0.095, 0.0001, 0.025),
        "positions": {
            "dimpler": (0.1, 0.00, 0.05),
            "noseWrinkler": (0.00, 0.00, 0.06),
            "nostrilDilator": (0.00, 0.00, 0.04),
        }
    },
    "Lips": {
        "location": (0.025, 0.0, -0.02),
        "scale": (0.095, 0.0001, 0.035),
        "positions": {
            "lipComerPuller": (0.05, 0.00, 0.00),
            "lipPressor": (0.1, 0.00, -0.04),
            "lipPuckerer": (0.075, 0.00, -0.04),
            "phonemeBMP": (-0.02, 0.00, -0.02),
            "lipStretcher": (0.02, 0.0001, -0.02),
            "sharpLipPuller": (0.1, 0.00, 0.00),
            "upperLipsPart": (-0.03, 0.00, 0.00),
            "upperLipsToward": (0.01, 0.00, 0.00),
            "upperLipRaiser": (0.03, 0.00, 0.00),
            "lipCornerDepressor": (0.1, 0.00, -0.02),
            "upperLipFunneler": (-0.01, 0.00, 0.00),
            "lowerLipSuck": (0.00, 0.00, -0.04),
            "lipTightener": (0.075, 0.00, -0.02),
        },
        "Unified": {
            "lipSideways": {
                "left": "lipSidewaysL",
                "right": "lipSidewaysR",
                "pos": (0.00, 0.0001, -0.02)  # где будет располагаться контроллер на лице
        },
        }
    },
    "Jaw": {
        "location": (0.025, 0.0, -0.075),
        "scale": (0.095, 0.0001, 0.015),
        "positions": {
            "jawOpen": (0.00, 0.00, -0.075),
            "jawSuck": (0.02, 0.00, -0.075),
            "jawThrust": (-0.02, 0.00, -0.075),
        },
        "Unified": {
            "jawSideways": {
                "left": "jawSidewaysL",
                "right": "jawSidewaysR",
                "pos": (0.04, 0.00, -0.075)  # где будет располагаться контроллер на лице
        },
    },
}
}

# ----------------------------------------------------------------------------
# 4) Функции для создания пустышек и драйверов
# ----------------------------------------------------------------------------

def create_parent_empty(name, location, collection, size=0.02, parent=None):
    """Создаёт родительскую пустышку (CIRCLE) в указанных координатах."""
    parent_obj = bpy.data.objects.new(name, None)
    parent_obj.empty_display_type = 'CIRCLE'
    parent_obj.empty_display_size = size
    parent_obj.location = location
    bpy.context.evaluated_depsgraph_get().update()
    if parent:
        parent_obj.parent = parent
        parent_obj.matrix_parent_inverse = parent.matrix_world.inverted()
        parent_obj.hide_select = True
    parent_obj.hide_render = True
    collection.objects.link(parent_obj)

    return parent_obj


def create_child_empty(name, parent, collection, size=0.01, type=None):
    """Создаёт дочернюю пустышку (CIRCLE) с локальным смещением (0,0,0)."""
    child = bpy.data.objects.new(name, None)
    child.empty_display_type = 'CIRCLE'
    child.empty_display_size = size
    child.parent = parent
    child.hide_render = True
    if not type:
        child.constraints.new(type='LIMIT_DISTANCE')
        child.constraints["Limit Distance"].target = parent
        child.constraints["Limit Distance"].distance = 0.14
        child.lock_location[1] = True
        child.lock_location[2] = True
    child.location = (0, 0, 0)  # локальные координаты
    collection.objects.link(child)

    return child


def create_frames(display_text, collection, scale, location, parent=None):
    frame = bpy.data.objects.new(display_text, None)

    font_curve = bpy.data.curves.new(type="FONT", name=display_text)
    font_curve.body = display_text
    font_curve.fill_mode = "NONE"
    font_curve.size = 0.0125
    font_curve.align_y = "TOP"

    frame_text = bpy.data.objects.new(display_text, object_data=font_curve)
    frame_text.location = (location[0] - scale[0] + 0.002, location[1], location[2] + scale[2])
    frame_text.rotation_euler[0] = math.radians(90)

    bpy.context.evaluated_depsgraph_get().update()

    frame.empty_display_type = "CUBE"
    frame.empty_display_size = 1
    frame.location = location

    frame.scale[0] = scale[0]
    frame.scale[1] = scale[1]
    frame.scale[2] = scale[2]

    if parent:
        frame.parent = parent

        frame_text.parent = parent
        frame_text.matrix_parent_inverse = parent.matrix_world.inverted()

        frame.hide_select = True

    frame.hide_render = True
    frame_text.hide_select = True
    frame_text.hide_render = True

    if not parent:
        frame_text = None

    collection.objects.link(frame)
    if frame_text:
        collection.objects.link(frame_text)
    return frame


def add_driver_for_shape_key(shape_key, expression, child_empty, rig_master, var_names_axes):
    """
    Создаёт драйвер для shape_key.value с заданным expression (строка).
    - rig_master: объект, у которого есть свойство ["controller_strength"].
    - var_names_axes: список кортежей вида [("varX", 'LOC_X'), ("varY", 'LOC_Y'), ...].

    Внутри драйвера создаём:
      - varX, varY (и т.д.) для координат child_empty
      - mult для чтения rig_master["controller_strength"]
    Итоговое выражение:  mult * (expression)
    """
    shape_key.driver_remove("value")
    fcurve = shape_key.driver_add("value")
    driver = fcurve.driver

    # Чтобы работали функции max() и т.п., у драйвера должен быть тип 'SCRIPTED'
    driver.type = 'SCRIPTED'

    # 1) Создаём переменные для координат
    for var_name, axis in var_names_axes:
        var = driver.variables.new()
        var.name = var_name
        var.type = 'TRANSFORMS'
        target = var.targets[0]
        target.id = child_empty
        target.transform_type = axis
        target.transform_space = 'LOCAL_SPACE'

    # 2) Создаём переменную для считывания mult (controller_strength)
    var_mult = driver.variables.new()
    var_mult.name = "mult"
    var_mult.type = 'SINGLE_PROP'
    var_mult.targets[0].id_type = 'OBJECT'
    var_mult.targets[0].id = rig_master
    var_mult.targets[0].data_path = '["controller_strength"]'

    # 3) Итоговое выражение
    # Если expression="max(0, varX)", то станет "mult * (max(0, varX))"
    driver.expression = f"mult * ({expression})"


# ----------------------------------------------------------------------------
# 5) Основная функция
# ----------------------------------------------------------------------------

def create_face_rig(context):
    # 5.1 Проверяем объект с Shape Keys

    obj = context.scene.face_rig_target
    if not obj or not obj.data.shape_keys:
        print("Активный объект не найден или не имеет Shape Keys.")
        return

    sk_data = obj.data.shape_keys
    key_blocks = sk_data.key_blocks

    # 5.2 Создаём/находим коллекцию для контроллеров

    frames_collection_name = "Frames_Controller"
    if frames_collection_name not in bpy.data.collections:
        frames_collection = bpy.data.collections.new(frames_collection_name)
        bpy.context.scene.collection.children.link(frames_collection)
    else:
        frames_collection = bpy.data.collections[frames_collection_name]

    # 5.3 Создаём (или берём существующий) FaceRigMaster с controller_strength
    rig_master_name = "FaceRigMaster"
    if rig_master_name in bpy.data.objects:
        rig_master = bpy.data.objects[rig_master_name]
    else:
        rig_master = bpy.data.objects.new(rig_master_name, None)
        rig_master.empty_display_type = 'PLAIN_AXES'
        rig_master.empty_display_size = 0.001
        bpy.context.scene.collection.objects.link(rig_master)

    if "controller_strength" not in rig_master:
        rig_master["controller_strength"] = 10.0  # по умолчанию

    main_frame = create_parent_empty("Face Rig",
                               collection=frames_collection,
                               size=0.0001,
                               location=face_positions["Main Empty"]["location"]
                               )

    for frame_name, frame_info in face_positions.items():
            if frame_name == "Main Empty":
                continue

            frame = create_frames(frame_name,
                                  collection=frames_collection,
                                  scale=frame_info["scale"],
                                  location=frame_info["location"],
                                  parent=main_frame
                                  )
            if frame_info.get("Unified"):
                for group_name, info in frame_info["Unified"].items():
                    left_sk = info.get("left")
                    right_sk = info.get("right")
                    pos = info.get("pos", (0, 0, 4))

                    # Проверяем, есть ли хотя бы один из этих шейпов
                    have_left = (left_sk in key_blocks) if left_sk else False
                    have_right = (right_sk in key_blocks) if right_sk else False

                    # Если вообще нет ни левого, ни правого — пропускаем
                    if not (have_left or have_right):
                        continue

                    # Иначе создаём контроллер
                    parent_name = f"{group_name}_PARENT"
                    child_name = f"{group_name}_CTRL"

                    parent_obj = create_parent_empty(parent_name, pos, frames_collection, size=parent_shape_size,
                                                     parent=frame)
                    child_obj = create_child_empty(child_name, parent_obj, frames_collection,
                                                   size=child_shape_size)

                    # Если есть левый шейп
                    if have_left:
                        shape_key = key_blocks[left_sk]
                        expr = "max(0, -varX)"  # движение по X < 0
                        add_driver_for_shape_key(
                            shape_key=shape_key,
                            expression=expr,
                            child_empty=child_obj,
                            rig_master=rig_master,
                            var_names_axes=[("varX", 'LOC_X')]
                        )

                    # Если есть правый шейп
                    if have_right:
                        shape_key = key_blocks[right_sk]
                        expr = "max(0, varX)"  # движение по X > 0
                        add_driver_for_shape_key(
                            shape_key=shape_key,
                            expression=expr,
                            child_empty=child_obj,
                            rig_master=rig_master,
                            var_names_axes=[("varX", 'LOC_X')]
                        )

            if frame_info.get("positions"):
                for sk_name, coord in frame_info["positions"].items():
                    if sk_name not in key_blocks:
                        if sk_name == "Stereo":
                            for sk_shape_name, info in coord.items():
                                eye_parent = create_parent_empty(sk_shape_name + "_PARENT",
                                                                 info["location"],
                                                                 frames_collection, parent=frame)
                                eye_child = create_child_empty(sk_shape_name + "_CTRL", eye_parent, frames_collection,
                                                               type=1)
                                for sk_eye_name, direction in info.items():
                                    if sk_eye_name not in key_blocks:
                                        continue  # нет такого шейпа, пропускаем

                                    shape_key = key_blocks[sk_eye_name]

                                    if direction == "up":
                                        expr = "max(0, varZ)"
                                    elif direction == "down":
                                        expr = "max(0, -varZ)"
                                    elif direction == "left":
                                        expr = "max(0, -varX)"
                                    elif direction == "right":
                                        expr = "max(0, varX)"
                                    else:
                                        expr = "0.0"

                                    add_driver_for_shape_key(
                                        shape_key=shape_key,
                                        expression=expr,
                                        child_empty=eye_child,
                                        rig_master=rig_master,
                                        var_names_axes=[("varX", 'LOC_X'), ("varZ", 'LOC_Z')]
                                    )
                        continue

                    # Если он в списке stereo-глаз или в парных, пропускаем


                    # Создаём одиночный контроллер
                    shape_key = key_blocks[sk_name]

                    parent_name = sk_name + "_PARENT"
                    child_name = sk_name + "_CTRL"

                    parent_empty = create_parent_empty(parent_name, coord, frames_collection, size=parent_shape_size,
                                                       parent=frame)
                    child_empty = create_child_empty(child_name, parent_empty, frames_collection, size=child_shape_size,
                                                     type=None)

                    # По умолчанию — двигаем по X
                    expr = "varX"

                    add_driver_for_shape_key(
                        shape_key=shape_key,
                        expression=expr,
                        child_empty=child_empty,
                        rig_master=rig_master,
                        var_names_axes=[("varX", 'LOC_X')]
                    )

    main_frame.location[2] = 4
    main_frame.location[0] = 0.4

    print("Face rig создан!\n"
          "• 'FaceRigMaster' содержит свойство 'controller_strength' для регулировки силы.\n"
          "• Глаза объединены в два контроллера (LeftEye_CTRL, RightEye_CTRL).\n"
          "• lipSidewaysL/R объединены в один контроллер lipSideways_CTRL.\n"
          "• Прочие Shape Keys — каждый со своим контроллером.\n"
          "• Если шейпов нет, контроллеры для них не создаются.\n"
          "• Двигайте контроллеры по нужным осям. В (0,0,0) Shape Keys = 0.\n")


# ----------------------------------------------------------------------------
# 6) Запуск
# ----------------------------------------------------------------------------


class FaceRigOperator(bpy.types.Operator):
    bl_idname = "object.face_rig_operator"
    bl_label = "Создать риг лица"

    def execute(self, context):
        obj = context
        create_face_rig(obj)
        return {'FINISHED'}