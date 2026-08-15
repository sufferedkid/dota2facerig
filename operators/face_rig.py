import math

import bpy

# Переменные для размеров
child_shape_size = 0.005
parent_shape_size = 0.01
rig_object_marker = "_dota2_face_rig"

category_colors = {
    "Face Rig": (0.95, 0.95, 0.95, 1.0),
    "Brows": (1.0, 0.72, 0.18, 1.0),
    "Eyes": (0.22, 0.72, 1.0, 1.0),
    "Nose": (0.30, 0.95, 0.58, 1.0),
    "Cheeks": (1.0, 0.50, 0.20, 1.0),
    "Lips": (1.0, 0.28, 0.48, 1.0),
    "Jaw": (0.72, 0.45, 1.0, 1.0),
}
default_rig_color = (0.85, 0.85, 0.85, 1.0)

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
            "eyeClosed": (0.06, 0.00, 0.145),
            "squint": (0.1, 0.00, 0.105),
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
        "scale": (0.095, 0.0001, 0.018),
        "positions": {
            "noseWrinkler": (0.00, 0.00, 0.06),
            "nostrilDilator": (0.00, 0.00, 0.04),
        }
    },
    "Cheeks": {
        "location": (0.025, 0.0, 0.02),
        "scale": (0.095, 0.0001, 0.018),
        "positions": {
            "cheekRaiser": (-0.03, 0.00, 0.02),
            "dimpler": (0.05, 0.00, 0.02),
        }
    },
    "Lips": {
        "location": (0.025, 0.0, -0.035),
        "scale": (0.095, 0.0001, 0.030),
        "positions": {
            "lipComerPuller": (0.05, 0.00, -0.015),
            "lipPressor": (0.1, 0.00, -0.055),
            "lipPuckerer": (0.075, 0.00, -0.055),
            "phonemeBMP": (-0.02, 0.00, -0.035),
            "lipStretcher": (0.02, 0.0001, -0.035),
            "sharpLipPuller": (0.1, 0.00, -0.015),
            "upperLipsPart": (-0.03, 0.00, -0.015),
            "upperLipsToward": (0.01, 0.00, -0.015),
            "upperLipRaiser": (0.03, 0.00, -0.015),
            "lipCornerDepressor": (0.1, 0.00, -0.035),
            "upperLipFunneler": (-0.01, 0.00, -0.015),
            "lowerLipSuck": (0.00, 0.00, -0.055),
            "lipTightener": (0.075, 0.00, -0.035),
        },
        "Unified": {
            "lipSideways": {
                "left": "lipSidewaysL",
                "right": "lipSidewaysR",
                "pos": (0.00, 0.0001, -0.035)  # где будет располагаться контроллер на лице
        },
        }
    },
    "Jaw": {
        "location": (0.025, 0.0, -0.09),
        "scale": (0.095, 0.0001, 0.015),
        "positions": {
            "jawOpen": (0.00, 0.00, -0.09),
            "jawSuck": (0.02, 0.00, -0.09),
            "jawThrust": (-0.02, 0.00, -0.09),
        },
        "Unified": {
            "jawSideways": {
                "left": "jawSidewaysL",
                "right": "jawSidewaysR",
                "pos": (0.04, 0.00, -0.09)  # где будет располагаться контроллер на лице
        },
    },
}
}

# ----------------------------------------------------------------------------
# 4) Функции для создания пустышек и драйверов
# ----------------------------------------------------------------------------

def mark_face_rig_object(obj):
    obj[rig_object_marker] = True
    obj.show_in_front = True
    obj.show_name = False
    return obj


def clean_previous_face_rig(collection):
    for obj in list(collection.objects):
        if obj.get(rig_object_marker):
            obj_data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if isinstance(obj_data, bpy.types.Curve) and obj_data.users == 0:
                bpy.data.curves.remove(obj_data)


def get_or_create_collection(name):
    collection = bpy.data.collections.get(name)
    if not collection:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def get_rig_material(name, color):
    material_name = f"Dota2FaceRig_{name}"
    material = bpy.data.materials.get(material_name)
    if not material:
        material = bpy.data.materials.new(material_name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = color[3]
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.35
    return material


def get_category_color(category_name):
    return category_colors.get(category_name, default_rig_color)


def create_curve_object(name, points, collection, color, bevel_depth=0.001):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3

    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (co[0], co[1], co[2], 1.0)

    curve.materials.append(get_rig_material(name, color))
    obj = mark_face_rig_object(bpy.data.objects.new(name, curve))
    obj.hide_render = True
    collection.objects.link(obj)
    return obj


def circle_points(radius, segments=32):
    points = []
    for index in range(segments):
        angle = 2.0 * math.pi * index / segments
        points.append((math.cos(angle) * radius, 0.0, math.sin(angle) * radius))
    points.append(points[0])
    return points


def rectangle_points(scale):
    width, _, height = scale
    return [
        (-width, 0.0, -height),
        (width, 0.0, -height),
        (width, 0.0, height),
        (-width, 0.0, height),
        (-width, 0.0, -height),
    ]


def diamond_points(radius):
    return [
        (0.0, 0.0, radius),
        (radius, 0.0, 0.0),
        (0.0, 0.0, -radius),
        (-radius, 0.0, 0.0),
        (0.0, 0.0, radius),
    ]


def relative_location(location, origin):
    return (
        location[0] - origin[0],
        location[1] - origin[1],
        location[2] - origin[2],
    )


def create_parent_empty(name, location, collection, size=0.02, parent=None, color=default_rig_color):
    """Создаёт цветную опорную форму контроллера."""
    parent_obj = create_curve_object(name, circle_points(size), collection, color, bevel_depth=size * 0.09)
    if parent:
        parent_obj.parent = parent
        parent_obj.hide_select = True
    parent_obj.location = location

    return parent_obj


def create_child_empty(name, parent, collection, size=0.01, free_move=False, color=default_rig_color):
    """Создаёт выделяемый цветной контроллер."""
    points = circle_points(size * 1.35) if free_move else diamond_points(size * 1.65)
    child = create_curve_object(name, points, collection, color, bevel_depth=size * 0.16)
    child.parent = parent
    child.lock_location[1] = True
    if not free_move:
        constraint = child.constraints.new(type='LIMIT_DISTANCE')
        constraint.target = parent
        constraint.distance = 0.14
        child.lock_location[2] = True
    child.location = (0, 0, 0)  # локальные координаты

    return child


def create_frames(display_text, collection, scale, location, parent=None, color=default_rig_color):
    frame = create_curve_object(display_text, rectangle_points(scale), collection, color, bevel_depth=0.0012)

    font_curve = bpy.data.curves.new(type="FONT", name=display_text)
    font_curve.body = display_text
    font_curve.fill_mode = "NONE"
    font_curve.size = 0.0125
    font_curve.align_y = "TOP"

    frame_text = mark_face_rig_object(bpy.data.objects.new(display_text, object_data=font_curve))
    frame_text.location = (-scale[0] + 0.002, 0.0, scale[2] - 0.002)
    frame_text.rotation_euler[0] = math.radians(90)
    font_curve.materials.append(get_rig_material(f"{display_text}_Text", color))

    if parent:
        frame.parent = parent
        frame.hide_select = True

    frame.location = location
    frame_text.parent = frame

    frame.hide_render = True
    frame_text.hide_select = True
    frame_text.hide_render = True

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
    try:
        shape_key.driver_remove("value")
    except (TypeError, ValueError, RuntimeError):
        pass
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
    if not obj or obj.type != 'MESH' or not obj.data.shape_keys:
        print("Активный объект не найден или не имеет Shape Keys.")
        return

    sk_data = obj.data.shape_keys
    key_blocks = sk_data.key_blocks

    # 5.2 Создаём/находим коллекцию для контроллеров

    rig_master_name = "FaceRigMaster"
    previous_rig_master = bpy.data.objects.get(rig_master_name)
    rig_master_strength = previous_rig_master.get("controller_strength", 10.0) if previous_rig_master else 10.0

    frames_collection_name = "Frames_Controller"
    frames_collection = get_or_create_collection(frames_collection_name)
    clean_previous_face_rig(frames_collection)

    # 5.3 Создаём (или берём существующий) FaceRigMaster с controller_strength
    rig_master = bpy.data.objects.get(rig_master_name)
    if rig_master and rig_master.type == 'EMPTY':
        bpy.data.objects.remove(rig_master, do_unlink=True)
        rig_master = None

    if not rig_master:
        rig_master = create_curve_object(
            rig_master_name,
            circle_points(0.006),
            frames_collection,
            get_category_color("Face Rig"),
            bevel_depth=0.0008,
        )
    mark_face_rig_object(rig_master)

    if "controller_strength" not in rig_master:
        rig_master["controller_strength"] = rig_master_strength  # по умолчанию

    main_frame = create_parent_empty("Face Rig",
                               collection=frames_collection,
                               size=0.0001,
                               location=face_positions["Main Empty"]["location"],
                               color=get_category_color("Face Rig")
                               )

    for frame_name, frame_info in face_positions.items():
            if frame_name == "Main Empty":
                continue

            frame_color = get_category_color(frame_name)
            frame_location = frame_info["location"]
            frame = create_frames(frame_name,
                                  collection=frames_collection,
                                  scale=frame_info["scale"],
                                  location=frame_location,
                                  parent=main_frame,
                                  color=frame_color
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
                    controller_pos = relative_location(pos, frame_location)

                    parent_obj = create_parent_empty(parent_name, controller_pos, frames_collection, size=parent_shape_size,
                                                     parent=frame, color=frame_color)
                    child_obj = create_child_empty(child_name, parent_obj, frames_collection,
                                                   size=child_shape_size, color=frame_color)

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
                                controller_pos = relative_location(info["location"], frame_location)
                                eye_parent = create_parent_empty(sk_shape_name + "_PARENT",
                                                                 controller_pos,
                                                                 frames_collection, parent=frame,
                                                                 color=frame_color)
                                eye_child = create_child_empty(sk_shape_name + "_CTRL", eye_parent, frames_collection,
                                                               free_move=True, color=frame_color)
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
                    controller_pos = relative_location(coord, frame_location)

                    parent_empty = create_parent_empty(parent_name, controller_pos, frames_collection, size=parent_shape_size,
                                                       parent=frame, color=frame_color)
                    child_empty = create_child_empty(child_name, parent_empty, frames_collection, size=child_shape_size,
                                                     free_move=False, color=frame_color)

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
