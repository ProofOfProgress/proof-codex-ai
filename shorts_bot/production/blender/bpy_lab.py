"""Blender Python (bpy) hands-on lab — run headless to verify mastery drills.

Usage:
  blender --background --python shorts_bot/production/blender/bpy_lab.py

Each module prints PASS/FAIL. Used by agents to validate bpy knowledge on the VM.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

RESULTS: list[dict] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append({"module": name, "pass": ok, "detail": detail})
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


def lab_01_scene_graph() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    cube = bpy.context.active_object
    cube.name = "LabCube"
    ok = cube.name in bpy.data.objects and cube.type == "MESH"
    _record("01_scene_graph", ok, f"objects={len(bpy.data.objects)}")


def lab_02_materials() -> None:
    mat = bpy.data.materials.new("LabMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.1, 0.2, 0.3, 1.0)
    obj = bpy.data.objects.get("LabCube")
    if obj:
        obj.data.materials.append(mat)
    ok = mat.use_nodes and obj and len(obj.data.materials) == 1
    _record("02_materials", ok)


def lab_03_pose_keyframes() -> None:
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode="EDIT")
    bone = arm_obj.data.edit_bones.new("WaveArm")
    bone.head = (0, 0, 1)
    bone.tail = (0, 0, 2)
    bpy.ops.object.mode_set(mode="POSE")
    pb = arm_obj.pose.bones["WaveArm"]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (0, 0, 0)
    pb.keyframe_insert(data_path="rotation_euler", frame=1)
    pb.rotation_euler = (math.radians(-90), 0, 0)
    pb.keyframe_insert(data_path="rotation_euler", frame=24)
    ad = arm_obj.animation_data
    ok = ad is not None and ad.action is not None and len(ad.action.fcurves) >= 1
    _record("03_pose_keyframes", ok, f"fcurves={len(ad.action.fcurves) if ad and ad.action else 0}")


def lab_04_nla_strip() -> None:
    arm_obj = bpy.context.active_object
    if not arm_obj or arm_obj.type != "ARMATURE":
        _record("04_nla_strip", False, "no armature")
        return
    action = arm_obj.animation_data.action
    ad = arm_obj.animation_data
    track = ad.nla_tracks.new()
    strip = track.strips.new(action.name, 1, action)
    strip.frame_end = 48
    ad.use_nla = True
    ok = len(ad.nla_tracks) == 1 and len(ad.nla_tracks[0].strips) == 1
    _record("04_nla_strip", ok)
    bpy.ops.object.mode_set(mode="OBJECT")


def lab_05_eevee_probes() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    view_layer = bpy.context.view_layer
    if view_layer.objects.active and view_layer.objects.active.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.lightprobe_add(type="GRID", location=(0, -5, 2))
    probe = bpy.context.active_object
    probe.scale = (8, 8, 4)
    bpy.ops.object.lightprobe_add(type="CUBEMAP", location=(0, -8, 3))
    cube_probe = bpy.context.active_object
    ok = probe.type == "LIGHT_PROBE" and cube_probe.type == "LIGHT_PROBE"
    _record("05_eevee_probes", ok, f"grid={probe.data.type} cube={cube_probe.data.type}")


def lab_06_camera_path() -> None:
    bpy.ops.object.camera_add(location=(0, 5, 1.6))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam
    cam.location = (0, 5, 1.6)
    cam.keyframe_insert(data_path="location", frame=1)
    cam.location = (0, -3, 1.6)
    cam.keyframe_insert(data_path="location", frame=48)
    ok = cam.animation_data and cam.animation_data.action
    _record("06_camera_path", ok)


def lab_07_headless_render() -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = 320
    scene.render.resolution_y = 180
    scene.render.filepath = "/tmp/bpy_lab_frame.png"
    scene.render.image_settings.file_format = "PNG"
    scene.frame_set(24)
    bpy.ops.render.render(write_still=True)
    ok = Path("/tmp/bpy_lab_frame.png").is_file()
    _record("07_headless_render", ok)


def lab_08_creature_import() -> None:
    workspace = Path("/workspace")
    sys.path.insert(0, str(workspace))
    try:
        from shorts_bot.production.blender.creature_paths import resolve_creature_model

        model = resolve_creature_model()
    except Exception as exc:
        _record("08_creature_import", False, str(exc))
        return
    if not model or not model.is_file():
        _record("08_creature_import", False, "model missing")
        return
    ext = model.suffix.lower()
    before = len(bpy.data.objects)
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(model))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(model))
    else:
        _record("08_creature_import", False, f"unsupported {ext}")
        return
    arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
    ok = arm is not None and len(bpy.data.objects) > before
    _record("08_creature_import", ok, f"armature={arm.name if arm else None}")


def main() -> None:
    labs = [
        lab_01_scene_graph,
        lab_02_materials,
        lab_03_pose_keyframes,
        lab_04_nla_strip,
        lab_05_eevee_probes,
        lab_06_camera_path,
        lab_07_headless_render,
        lab_08_creature_import,
    ]
    for fn in labs:
        try:
            fn()
        except Exception as exc:
            _record(fn.__name__, False, str(exc)[:200])

    passed = sum(1 for r in RESULTS if r["pass"])
    print(f"\n=== LAB SUMMARY: {passed}/{len(RESULTS)} passed ===")
    out = Path("/workspace/data/research/bpy_lab_results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"passed": passed, "total": len(RESULTS), "results": RESULTS}, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
