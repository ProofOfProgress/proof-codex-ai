"""CG Python Academy course exercises — run each part headless, PASS/FAIL.

Course: https://www.skool.com/cgpython/classroom/60a44c1e

Usage:
  blender --background --python shorts_bot/production/blender/course_exercises.py
  blender --background --python shorts_bot/production/blender/course_exercises.py -- --part 3
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

RESULTS: list[dict] = []


def _record(part: str, name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append({"part": part, "name": name, "pass": ok, "detail": detail})
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] Part {part} — {name}" + (f" — {detail}" if detail else ""))


def _reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


# --- Part 1: Basics (course: variables, loops, functions) ---


def exercise_1_01_five_cubes() -> None:
    """Course: loop to create 5 cubes in a row."""
    _reset()
    for i in range(5):
        bpy.ops.mesh.primitive_cube_add(location=(i * 2.0, 0, 0))
        bpy.context.active_object.name = f"PeripheralCube_{i}"
    ok = len([o for o in bpy.data.objects if o.name.startswith("PeripheralCube_")]) == 5
    _record("1", "five_cubes_loop", ok, f"count={len(bpy.data.objects)}")


def exercise_1_02_material_function() -> None:
    """Course: function that returns a configured material."""


    def make_horror_mat(name: str, rgb: tuple[float, float, float]) -> bpy.types.Material:
        m = bpy.data.materials.new(name=name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
        return m

    _reset()
    bpy.ops.mesh.primitive_plane_add()
    obj = bpy.context.active_object
    obj.data.materials.append(make_horror_mat("Asphalt", (0.04, 0.04, 0.05)))
    ok = obj.data.materials and obj.data.materials[0].use_nodes
    _record("1", "material_function", ok)


# --- Part 2: First operator (official add-on tutorial exercise) ---


class PERIPHERAL_OT_move_x(bpy.types.Operator):
    """Course exercise: Move all objects +1 on X (add-on tutorial)."""

    bl_idname = "peripheral.move_x"
    bl_label = "Peripheral Move X"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.scene.objects:
            if obj.type == "MESH":
                obj.location.x += 1.0
        return {"FINISHED"}


def exercise_2_01_register_operator() -> None:
    """Course: register operator, run via bpy.ops, unregister."""
    _reset()
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    x0 = cube.location.x
    try:
        bpy.utils.register_class(PERIPHERAL_OT_move_x)
        bpy.ops.peripheral.move_x()
        ok = abs(cube.location.x - (x0 + 1.0)) < 0.001
    except Exception as exc:
        ok = False
        detail = str(exc)[:120]
    else:
        detail = f"x={cube.location.x:.2f}"
    finally:
        try:
            bpy.utils.unregister_class(PERIPHERAL_OT_move_x)
        except Exception:
            pass
    _record("2", "register_and_run_operator", ok, detail)


# --- Part 3: Working with objects (course + addon tutorial copy/keyframes) ---


def exercise_3_01_move_and_keyframe() -> None:
    """Course: set location + keyframe_insert on camera."""
    _reset()
    bpy.ops.object.camera_add(location=(0, 5, 1.65))
    cam = bpy.context.active_object
    cam.keyframe_insert(data_path="location", frame=1)
    cam.location = (0, -5, 1.65)
    cam.keyframe_insert(data_path="location", frame=48)
    ok = cam.animation_data and cam.animation_data.action is not None
    _record("3", "camera_keyframes", ok)


def exercise_3_02_linked_duplicate() -> None:
    """Course: obj.copy() + link — linked duplicates (add-on tutorial)."""
    _reset()
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    scene = bpy.context.scene
    dup = obj.copy()
    scene.collection.objects.link(dup)
    dup.location = (3, 0, 0)
    ok = dup.data is obj.data and dup.name != obj.name
    _record("3", "linked_duplicate", ok)


def exercise_3_03_collection() -> None:
    """Course: organize objects into collections."""
    _reset()
    col = bpy.data.collections.new("PeripheralCreatures")
    bpy.context.scene.collection.children.link(col)
    bpy.ops.mesh.primitive_cube_add()
    creature = bpy.context.active_object
    creature.name = "Form2Proxy"
    for c in creature.users_collection:
        c.objects.unlink(creature)
    col.objects.link(creature)
    ok = creature.name in col.objects and creature.name not in bpy.context.scene.collection.objects
    _record("3", "creature_collection", ok)


def exercise_3_04_camera_look_at() -> None:
    """Course apply: camera points at creature between pumps (draft #2 grammar)."""
    _reset()
    bpy.ops.object.camera_add(location=(0, -5.5, 1.55))
    cam = bpy.context.active_object
    target = (0, -9.0, 1.6)
    # Inline TRACK_TO (same as build_and_render._camera_point_at)
    empty = bpy.data.objects.new("_LookAt", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = target
    con = cam.constraints.new("TRACK_TO")
    con.target = empty
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    cam.select_set(True)
    bpy.context.view_layer.objects.active = cam
    bpy.ops.constraint.apply(constraint=con.name, owner="OBJECT")
    cam.constraints.clear()
    bpy.data.objects.remove(empty, do_unlink=True)
    forward = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    toward = (Vector(target) - cam.location).normalized()
    dot = forward.dot(toward)
    ok = dot > 0.95
    _record("3", "camera_look_at_pumps", ok, f"dot={dot:.3f}")


def run_part(part: str | None = None) -> int:
    parts = {
        "1": [exercise_1_01_five_cubes, exercise_1_02_material_function],
        "2": [exercise_2_01_register_operator],
        "3": [
            exercise_3_01_move_and_keyframe,
            exercise_3_02_linked_duplicate,
            exercise_3_03_collection,
            exercise_3_04_camera_look_at,
        ],
    }
    to_run: list = []
    if part and part in parts:
        to_run = parts[part]
    else:
        for p in ("1", "2", "3"):
            to_run.extend(parts[p])

    for fn in to_run:
        try:
            fn()
        except Exception as exc:
            _record("?", fn.__name__, False, str(exc)[:160])

    passed = sum(1 for r in RESULTS if r["pass"])
    total = len(RESULTS)
    print(f"\n=== COURSE EXERCISES: {passed}/{total} passed ===")
    out = Path("/workspace/data/research/course_exercises_results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"passed": passed, "total": total, "results": RESULTS}, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0 if passed == total else 1


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=("1", "2", "3"), default=None)
    args = parser.parse_args(argv)
    raise SystemExit(run_part(args.part))


if __name__ == "__main__":
    main()
