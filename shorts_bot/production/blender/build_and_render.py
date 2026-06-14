"""Build Peripheral Form 2 gas-station scene in Blender (bpy).

Run headless:
  blender --background --python shorts_bot/production/blender/build_and_render.py -- \\
      --draft-id 2 --preview
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

# Only import bpy inside Blender
import bpy  # type: ignore
from mathutils import Vector  # type: ignore


OUTPUT_ROOT = Path("/workspace/data/production")
FPS = 24
RES_X = 720
RES_Y = 1280


def _clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _mat(name: str, color: tuple[float, float, float, float], *, rough: float = 0.85):
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = rough
    return m


def _add_ground_and_road() -> None:
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.data.materials.append(_mat("Asphalt", (0.03, 0.03, 0.04, 1.0), rough=0.95))

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2, 0.01))
    road = bpy.context.active_object
    road.name = "Road"
    road.scale = (4, 18, 0.02)
    road.data.materials.append(_mat("WetRoad", (0.06, 0.06, 0.08, 1.0)))


def _emissive_mat(name: str, color: tuple[float, float, float, float], *, strength: float = 2.0):
    m = _mat(name, color, rough=0.4)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = strength
    return m


def _add_gas_station() -> bpy.types.Object:
    mats = {
        "pump": _mat("Pump", (0.12, 0.12, 0.14, 1.0)),
        "canopy": _mat("Canopy", (0.08, 0.08, 0.1, 1.0)),
        "pump_glow": _emissive_mat("PumpGlow", (1.0, 0.45, 0.12, 1.0), strength=1.5),
    }
    for i, x in enumerate((-3.5, 3.5)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -8, 1.2))
        pump = bpy.context.active_object
        pump.name = f"Pump_{i}"
        pump.scale = (0.6, 0.5, 2.4)
        pump.data.materials.append(mats["pump"])
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -8, 2.35))
        glow = bpy.context.active_object
        glow.name = f"PumpGlow_{i}"
        glow.scale = (0.35, 0.25, 0.08)
        glow.data.materials.append(mats["pump_glow"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -10, 3.5))
    canopy = bpy.context.active_object
    canopy.name = "Canopy"
    canopy.scale = (8, 3, 0.3)
    canopy.data.materials.append(mats["canopy"])
    return canopy


def _add_streetlight() -> tuple[bpy.types.Object, bpy.types.Light]:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(4, -6, 0))
    pole_empty = bpy.context.active_object
    pole_empty.name = "StreetlightRig"
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=5, location=(4, -6, 2.5))
    pole = bpy.context.active_object
    pole.name = "StreetlightPole"
    pole.parent = pole_empty
    bpy.ops.object.light_add(type="POINT", location=(4, -6, 5.2))
    lamp = bpy.context.active_object
    lamp.name = "Streetlight"
    lamp.data.energy = 1800
    lamp.data.color = (1.0, 0.55, 0.2)
    lamp.parent = pole_empty
    # Fill + rim so Form 2 reads against fog (Blender Guru lighting)
    bpy.ops.object.light_add(type="AREA", location=(-3, -7, 3))
    fill = bpy.context.active_object
    fill.name = "CreatureFill"
    fill.data.energy = 350
    fill.data.color = (0.75, 0.82, 1.0)
    fill.data.size = 4.0
    fill.rotation_euler = (math.radians(65), 0, math.radians(-30))
    bpy.ops.object.light_add(type="SPOT", location=(2, -5, 4))
    rim = bpy.context.active_object
    rim.name = "CreatureRim"
    rim.data.energy = 600
    rim.data.color = (1.0, 0.45, 0.15)
    rim.data.spot_size = math.radians(55)
    rim.rotation_euler = (math.radians(110), 0, math.radians(200))
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 30))
    moon = bpy.context.active_object
    moon.name = "MoonFill"
    moon.data.energy = 0.35
    moon.data.color = (0.55, 0.62, 0.85)
    moon.rotation_euler = (math.radians(55), 0, math.radians(-25))
    return pole_empty, lamp.data


def _build_form2(location=(0, -12, 0)) -> bpy.types.Object:
    """Form 2 rural anomaly — too tall, wrong joints."""
    skin = _mat("Form2Skin", (0.18, 0.16, 0.15, 1.0), rough=0.7)
    rig = bpy.data.objects.new("Form2Rig", None)
    bpy.context.collection.objects.link(rig)
    rig.location = Vector(location)

    def part(name, loc, scale):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        obj.location = Vector(loc)
        obj.parent = rig
        obj.data.materials.append(skin)
        return obj

    part("Torso", (0, 0, 2.8), (0.55, 0.35, 1.8))
    part("Head", (0, 0, 5.2), (0.35, 0.28, 0.45))
    part("Arm_L", (-0.9, 0, 3.8), (0.12, 0.12, 1.6))
    part("Arm_R", (0.9, 0, 3.8), (0.12, 0.12, 1.6))
    part("Leg_L", (-0.35, 0, 0.9), (0.14, 0.14, 1.8))
    part("Leg_R", (0.35, 0, 0.9), (0.14, 0.14, 1.8))
    rig.scale = (1.0, 1.0, 1.35)  # too tall
    return rig


def _import_mesh_file(path: Path) -> list:
    ext = path.suffix.lower()
    before = {o.name for o in bpy.data.objects}
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext == ".dae":
        bpy.ops.wm.collada_import(filepath=str(path))
    else:
        raise ValueError(f"Unsupported creature model format: {ext}")
    return [o for o in bpy.data.objects if o.name not in before and o.type in {"MESH", "ARMATURE", "EMPTY"}]


def _tweak_imported_creature(rig: bpy.types.Object, *, profile: str = "form2_rural") -> None:
    """Peripheral Form 2 pass — darker, taller, wet-night horror."""
    if profile == "form2_rural":
        extra = float(os.environ.get("BLENDER_CREATURE_SCALE", "1.0"))
        rig.scale = Vector(rig.scale) * Vector((1.05, 1.05, 1.15)) * extra
    for obj in rig.children_recursive:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes:
                continue
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if not bsdf:
                continue
            col = bsdf.inputs["Base Color"].default_value
            bsdf.inputs["Base Color"].default_value = (
                col[0] * 0.55,
                col[1] * 0.50,
                col[2] * 0.48,
                1.0,
            )
            bsdf.inputs["Roughness"].default_value = max(
                float(bsdf.inputs["Roughness"].default_value), 0.72
            )
            spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
            if spec:
                spec.default_value = 0.18


def _mesh_world_height(rig: bpy.types.Object) -> float:
    zmin, zmax = 1e9, -1e9
    for obj in rig.children_recursive:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            zmin = min(zmin, world.z)
            zmax = max(zmax, world.z)
    return max(0.01, zmax - zmin)


def _apply_creature_texture(rig: bpy.types.Object, tex_path: Path) -> None:
    if not tex_path.is_file():
        return
    img = bpy.data.images.load(str(tex_path), check_existing=True)
    for obj in rig.children_recursive:
        if obj.type != "MESH":
            continue
        if not obj.data.materials:
            obj.data.materials.append(_mat("CreatureSkin", (0.7, 0.65, 0.6, 1.0)))
        for slot in obj.material_slots:
            mat = slot.material
            if not mat:
                continue
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bsdf = nodes.get("Principled BSDF")
            if not bsdf:
                continue
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = img
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])


def _ground_creature(rig: bpy.types.Object) -> None:
    bpy.context.view_layer.update()
    zmin = 1e9
    for obj in rig.children_recursive:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            zmin = min(zmin, world.z)
    if zmin < 1e8:
        rig.location.z -= zmin


def _normalize_creature_rig(rig: bpy.types.Object, *, target_height: float = 2.45) -> None:
    """SCP-096 lore height ~2.38m — scale import to match scene."""
    bpy.context.view_layer.update()
    h = _mesh_world_height(rig)
    if h > 0.05:
        factor = target_height / h
        rig.scale = Vector((factor, factor, factor))
    rig.rotation_euler = (0, 0, 0)
    _ground_creature(rig)
    bpy.context.view_layer.update()


def _build_creature_from_file(path: Path, location=(0, -12, 0)) -> bpy.types.Object:
    imported = _import_mesh_file(path)
    if not imported:
        raise RuntimeError(f"Import produced no objects: {path}")
    rig = bpy.data.objects.new("Form2Rig", None)
    bpy.context.collection.objects.link(rig)
    rig.location = Vector(location)
    for obj in imported:
        if obj.parent is None:
            obj.parent = rig
    _normalize_creature_rig(rig)
    tex = path.parent / "scp_096.png"
    _apply_creature_texture(rig, tex)
    _tweak_imported_creature(rig)
    return rig


def _build_creature(location=(0, -12, 0)) -> bpy.types.Object:
    model_path = os.environ.get("BLENDER_CREATURE_MODEL", "").strip()
    if model_path:
        p = Path(model_path)
        if p.is_file():
            return _build_creature_from_file(p, location=location)
    # Default slot — channel/assets/creatures/scp_096/*
    workspace = Path(os.environ.get("WORKSPACE_ROOT", "/workspace"))
    try:
        sys.path.insert(0, str(workspace))
        from shorts_bot.production.blender.creature_paths import resolve_creature_model

        hit = resolve_creature_model()
        if hit:
            return _build_creature_from_file(hit, location=location)
    except Exception as exc:
        print(f"Creature model lookup failed ({exc}) — using procedural Form 2")
    return _build_form2(location=location)


def _finalize_clip_output(expected: Path) -> Path:
    """Blender FFMPEG animation writes stem0001-0240.mp4 — rename + faststart for browsers."""
    import subprocess

    if expected.is_file() and expected.stat().st_size > 50000:
        path = expected
    else:
        matches = sorted(expected.parent.glob(f"{expected.stem}*.mp4"))
        if not matches:
            raise FileNotFoundError(f"No Blender video output for {expected}")
        src = matches[-1]
        if src != expected:
            expected.unlink(missing_ok=True)
            src.rename(expected)
        path = expected
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0 or not (probe.stdout or "").strip():
        raise RuntimeError(f"Invalid Blender clip (ffprobe failed): {path}")
    _faststart_mp4(path)
    # Remove stale partial writes so preview page cannot serve them
    for partial in path.parent.glob(f"{path.stem}*.mp4"):
        if partial != path and "0001-" in partial.name:
            partial.unlink(missing_ok=True)
    return path


def _faststart_mp4(path: Path) -> None:
    """Move moov atom to front — browsers need this or video looks frozen on frame 1."""
    import subprocess

    tmp = path.with_name(f".{path.stem}_faststart.mp4")
    proc = subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
            "-c", "copy", "-movflags", "+faststart", str(tmp),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0 and tmp.is_file() and tmp.stat().st_size > 1000:
        tmp.replace(path)
    else:
        tmp.unlink(missing_ok=True)


def _setup_camera() -> bpy.types.Object:
    bpy.ops.object.camera_add(location=(0, 2, 1.65))
    cam = bpy.context.active_object
    cam.name = "POVCamera"
    cam.data.lens = 24
    cam.rotation_euler = (math.radians(88), 0, math.radians(180))
    bpy.context.scene.camera = cam
    return cam


def _setup_render(scene: bpy.types.Scene, *, samples: int = 32) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.fps = FPS
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.eevee.use_gtao = True
    scene.eevee.use_bloom = True
    scene.eevee.bloom_intensity = 0.08
    scene.eevee.taa_render_samples = max(8, min(samples, 128))
    if scene.world is None:
        scene.world = bpy.data.worlds.new("PeripheralWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.025, 0.035, 0.055, 1.0)
    bg.inputs[1].default_value = 0.65
    scene.eevee.use_ssr = True
    scene.eevee.use_ssr_refraction = False
    scene.eevee.gi_diffuse_bounces = 2
    scene.eevee.gi_cubemap_resolution = "512"


def _flicker_keyframes(lamp_data: bpy.types.Light, frame_start: int, frame_end: int) -> None:
    """Streetlight strobes — keyframes avoid headless driver restrictions."""
    prev = -1.0
    for f in range(frame_start, frame_end + 1):
        if int(f / 6) % 2 == 0:
            energy = 1600.0
        elif int(f / 3) % 5 == 0:
            energy = 350.0
        else:
            energy = 120.0
        if energy != prev:
            lamp_data.energy = energy
            lamp_data.keyframe_insert(data_path="energy", frame=f)
            prev = energy


def _add_eevee_light_probes() -> None:
    """Irradiance grid + reflection cubemap — EEVEE course: indirect light on night scenes."""
    scene = bpy.context.scene
    if scene.render.engine != "BLENDER_EEVEE":
        return
    bpy.ops.object.lightprobe_add(type="GRID", location=(0, -8, 2.5))
    grid = bpy.context.active_object
    grid.name = "GasStationGI"
    grid.scale = (14, 16, 6)
    if grid.data:
        grid.data.grid_bake_samples = 256
        grid.data.grid_capture_indirect = True
        grid.data.grid_capture_emission = True
    bpy.ops.object.lightprobe_add(type="CUBEMAP", location=(0, -10, 3))
    cube = bpy.context.active_object
    cube.name = "GasStationRefl"
    if cube.data:
        cube.data.influence_distance = 18.0
    # Headless probe bake can corrupt skinned meshes — opt-in only
    if os.environ.get("BLENDER_BAKE_PROBES", "").strip().lower() in ("1", "true", "yes"):
        try:
            bpy.ops.object.lightprobe_cache_bake()
        except Exception as exc:
            print(f"Light probe bake skipped: {exc}")


def _add_fog_and_trees() -> None:
    """Low pine silhouettes + volumetric fog for rural night mood."""
    trunk = _mat("PineTrunk", (0.04, 0.03, 0.02, 1.0), rough=0.95)
    needle = _mat("PineNeedle", (0.02, 0.04, 0.03, 1.0), rough=0.9)
    for x, y, h in [(-12, -16, 7), (14, -18, 9), (-8, -22, 6), (18, -14, 8)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=h * 0.35, location=(x, y, h * 0.18))
        t = bpy.context.active_object
        t.data.materials.append(trunk)
        bpy.ops.mesh.primitive_cone_add(radius1=h * 0.45, depth=h * 0.65, location=(x, y, h * 0.65))
        c = bpy.context.active_object
        c.data.materials.append(needle)

    scene = bpy.context.scene
    if scene.world and scene.world.node_tree:
        nodes = scene.world.node_tree.nodes
        links = scene.world.node_tree.links
        output = nodes.get("World Output")
        if output and not output.inputs["Volume"].links:
            vol = nodes.new("ShaderNodeVolumeScatter")
            vol.inputs["Density"].default_value = 0.005
            vol.inputs["Anisotropy"].default_value = 0.2
            links.new(vol.outputs["Volume"], output.inputs["Volume"])


def _find_armature(rig: bpy.types.Object) -> bpy.types.Object | None:
    for obj in rig.children_recursive:
        if obj.type == "ARMATURE":
            return obj
    return None


def _clear_armature_animation(armature: bpy.types.Object) -> None:
    if not armature.animation_data:
        return
    armature.animation_data.action = None
    while armature.animation_data.nla_tracks:
        armature.animation_data.nla_tracks.remove(armature.animation_data.nla_tracks[0])


def _read_motion_json(pack_dir: Path, phase: str) -> list[dict] | None:
    path = pack_dir / f"motion_{phase}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        kf = data.get("keyframes")
        if isinstance(kf, list) and len(kf) >= 2:
            return kf
    except Exception as exc:
        print(f"Motion JSON read failed ({path}): {exc}")
    return None


def _apply_motion_keyframes(
    armature: bpy.types.Object,
    keyframes: list[dict],
    *,
    frame_start: int,
    frame_end: int,
) -> None:
    """Apply English→JSON pose keys from motion_{phase}.json."""
    if armature.type != "ARMATURE":
        return
    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = armature
    if armature.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")

    dur = max(1, frame_end - frame_start)

    def _key_bone(name: str, rot: tuple[float, float, float], frame: int) -> None:
        pb = armature.pose.bones.get(name)
        if not pb:
            return
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = rot
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    for item in keyframes:
        t_frac = float(item.get("t", 0))
        frame = frame_start + int(dur * max(0.0, min(1.0, t_frac)))
        bones = item.get("bones") or {}
        if not isinstance(bones, dict):
            continue
        for bname, rot in bones.items():
            if not isinstance(rot, (list, tuple)) or len(rot) != 3:
                continue
            _key_bone(bname, (float(rot[0]), float(rot[1]), float(rot[2])), frame)

    if armature.animation_data and armature.animation_data.action:
        for fcu in armature.animation_data.action.fcurves:
            for kp in fcu.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"

    bpy.ops.object.mode_set(mode="OBJECT")
    if prev_active:
        bpy.context.view_layer.objects.active = prev_active


def _play_creature_action(
    armature: bpy.types.Object,
    *,
    phase: str,
    frame_start: int,
    frame_end: int,
    pack_dir: Path | None = None,
) -> None:
    """Motion from motion_{phase}.json (English prompt) or procedural/NLA fallback."""
    _clear_armature_animation(armature)

    if pack_dir:
        motion = _read_motion_json(pack_dir, phase)
        if motion:
            _apply_motion_keyframes(armature, motion, frame_start=frame_start, frame_end=frame_end)
            return

    # Wave / lunge without JSON — built-in pose keys
    if phase in ("wave", "lunge"):
        _pose_wave_or_lunge(armature, phase=phase, frame_start=frame_start, frame_end=frame_end)
        return

    action = bpy.data.actions.get("anim_Armature1") or bpy.data.actions.get("Armature1")
    if not action:
        for act in bpy.data.actions:
            if "armature" in act.name.lower() or "anim" in act.name.lower():
                action = act
                break
    if not action:
        _pose_wave_or_lunge(armature, phase=phase, frame_start=frame_start, frame_end=frame_end)
        return

    ad = armature.animation_data or armature.animation_data_create()
    act_end = int(min(action.frame_range[1], 600))
    phase_ranges = {
        "open": (1, min(120, act_end)),
        "lunge": (min(300, act_end // 2), min(480, act_end)),
    }
    a0, a1 = phase_ranges.get(phase, (1, min(120, act_end)))
    track = ad.nla_tracks.new()
    track.name = f"Form2_{phase}"
    strip = track.strips.new(action.name, frame_start, action)
    strip.action_frame_start = a0
    strip.action_frame_end = a1
    strip.frame_end = frame_end
    strip.blend_type = "REPLACE"
    ad.use_nla = True

    if phase == "lunge":
        _pose_wave_or_lunge(armature, phase=phase, frame_start=frame_start, frame_end=frame_end)


def _pose_wave_or_lunge(
    armature: bpy.types.Object,
    *,
    phase: str,
    frame_start: int,
    frame_end: int,
) -> None:
    """Procedural creepy wave (right arm chain) + jumpscare lunge pose."""
    if armature.type != "ARMATURE":
        return
    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = armature
    if armature.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")

    # Right arm: Bone_007 (shoulder) → Bone_009 → Bone_012 → Bone_011
    def _key_bone(name: str, rot: tuple[float, float, float], frame: int) -> None:
        pb = armature.pose.bones.get(name)
        if not pb:
            return
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = rot
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    if phase == "wave":
        # Slow uncanny wave — arm up, wrist bent backward, slight sway
        dur = frame_end - frame_start
        t = lambda frac: frame_start + int(dur * frac)
        poses = [
            (t(0.05), {"Bone_007": (0, 0, 0), "Bone_009": (0, 0, 0), "Bone_012": (0, 0, 0), "Bone_011": (0, 0, 0)}),
            (t(0.20), {"Bone_007": (-1.4, 0.15, -0.25), "Bone_009": (-0.4, 0, 0.1), "Bone_012": (0.3, 0, 0.5), "Bone_011": (0, 0, 0.6)}),
            (t(0.38), {"Bone_007": (-2.0, 0.2, -0.35), "Bone_009": (-0.9, 0.1, -0.15), "Bone_012": (0.5, 0.15, 0.9), "Bone_011": (0.2, 0, 1.1)}),
            (t(0.52), {"Bone_007": (-2.15, 0.18, -0.3), "Bone_009": (-1.0, 0.08, -0.2), "Bone_012": (0.45, 0.1, 1.0), "Bone_011": (0.15, 0, 1.2)}),
            (t(0.65), {"Bone_007": (-1.85, 0.12, -0.28), "Bone_009": (-0.75, 0, 0.05), "Bone_012": (0.35, 0, 0.75), "Bone_011": (0, 0, 0.9)}),
            (t(0.78), {"Bone_007": (-2.05, 0.16, -0.32), "Bone_009": (-0.95, 0.06, -0.1), "Bone_012": (0.4, 0.08, 0.95), "Bone_011": (0.1, 0, 1.05)}),
            (t(0.92), {"Bone_007": (-1.6, 0.1, -0.2), "Bone_009": (-0.5, 0, 0), "Bone_012": (0.2, 0, 0.4), "Bone_011": (0, 0, 0.5)}),
        ]
        for frame, bones in poses:
            for bname, rot in bones.items():
                _key_bone(bname, rot, frame)
        # Smooth wave motion (avoid robotic linear default)
        if armature.animation_data and armature.animation_data.action:
            for fcu in armature.animation_data.action.fcurves:
                for kp in fcu.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = "AUTO_CLAMPED"
                    kp.handle_right_type = "AUTO_CLAMPED"
        # Subtle head tilt toward camera during wave
        _key_bone("neck", (0.08, 0, 0.05), t(0.38))
        _key_bone("neck", (0.12, 0, 0.08), t(0.65))
        _key_bone("head", (0.05, 0, 0.1), t(0.52))
    elif phase == "lunge":
        lunge_f = frame_end - 10
        for name, rot, fr in [
            ("pelvis", (0, 0, 0), frame_start),
            ("ripcage", (0.15, 0, 0), lunge_f),
            ("ripcage", (0.5, 0, 0), frame_end),
            ("neck", (0.2, 0, 0), lunge_f),
            ("neck", (0.45, 0, 0), frame_end),
            ("head", (0.1, 0, 0), lunge_f),
            ("head", (0.35, 0, 0), frame_end),
            ("Bone_007", (-2.2, 0, 0), frame_end),
        ]:
            _key_bone(name, rot, fr)

    bpy.ops.object.mode_set(mode="OBJECT")
    if prev_active:
        bpy.context.view_layer.objects.active = prev_active


def _animate_camera_wave_lunge(
    cam: bpy.types.Object,
    form2: bpy.types.Object,
    *,
    frame_start: int,
    frame_end: int,
    phase: str,
    armature: bpy.types.Object | None = None,
    pack_dir: Path | None = None,
) -> None:
    cam.animation_data_clear()
    form2.animation_data_clear()
    cam.keyframe_insert(data_path="location", frame=frame_start)

    if phase == "open":
        cam.location = (0, 4, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_start)
        cam.location = (0, -1, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_end - 4)
        form2.location = (0, -14, 0)
        form2.keyframe_insert(data_path="location", frame=frame_start)
        form2.location = (0, -11, 0)
        form2.keyframe_insert(data_path="location", frame=frame_end)
    elif phase == "wave":
        cam.location = (1.2, -5, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_start)
        cam.location = (0.3, -6.5, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_end)
        form2.location = (0, -7.5, 0)
        form2.keyframe_insert(data_path="location", frame=frame_start)
        # creepy wave — rotate arm proxy via rig Z
        form2.rotation_euler = (0, 0, 0)
        form2.keyframe_insert(data_path="rotation_euler", frame=frame_start + 6)
        form2.rotation_euler = (0, 0, math.radians(8))
        form2.keyframe_insert(data_path="rotation_euler", frame=frame_end - 8)
        form2.location = (0, -6.0, 0)
        form2.keyframe_insert(data_path="location", frame=frame_end)
    else:  # lunge / jumpscare
        cam.location = (0, -6, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_start)
        form2.location = (0, -8, 0)
        form2.scale = (1.0, 1.0, 1.35)
        form2.keyframe_insert(data_path="location", frame=frame_start)
        form2.keyframe_insert(data_path="scale", frame=frame_start)
        # JUMPSCARE — last 12 frames explode toward camera
        lunge_f = frame_end - 12
        form2.location = (0, -8, 0)
        form2.keyframe_insert(data_path="location", frame=lunge_f)
        form2.location = (0, -2.2, 0.5)
        form2.scale = (1.3, 1.3, 1.5)
        form2.keyframe_insert(data_path="location", frame=frame_end)
        form2.keyframe_insert(data_path="scale", frame=frame_end)
        cam.location = (0, -6, 1.65)
        cam.keyframe_insert(data_path="location", frame=lunge_f)
        cam.location = (0, -3.5, 1.4)
        cam.keyframe_insert(data_path="location", frame=frame_end)

    if armature:
        _play_creature_action(
            armature,
            phase=phase,
            frame_start=frame_start,
            frame_end=frame_end,
            pack_dir=pack_dir,
        )


def build_scene(*, samples: int = 32) -> dict:
    _clear_scene()
    scene = bpy.context.scene
    _add_ground_and_road()
    _add_gas_station()
    pole_empty, lamp = _add_streetlight()
    form2 = _build_creature()
    cam = _setup_camera()
    _setup_render(scene, samples=samples)
    _add_eevee_light_probes()
    _add_fog_and_trees()
    return {"scene": scene, "camera": cam, "form2": form2, "lamp": lamp, "armature": _find_armature(form2)}


def render_clip(
    ctx: dict,
    out_path: Path,
    *,
    phase: str,
    seconds: float = 10.0,
) -> None:
    scene = ctx["scene"]
    cam = ctx["camera"]
    form2 = ctx["form2"]
    lamp = ctx["lamp"]
    armature = ctx.get("armature")
    f0 = 1
    f1 = int(seconds * FPS)
    scene.frame_start = f0
    scene.frame_end = f1
    _flicker_keyframes(lamp, f0, f1)
    _animate_camera_wave_lunge(
        cam, form2, frame_start=f0, frame_end=f1, phase=phase, armature=armature,
        pack_dir=ctx.get("pack_dir"),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_path.with_suffix(""))
    bpy.ops.render.render(animation=True)
    _finalize_clip_output(out_path)
    print(f"Rendered {out_path}")


def render_draft_short(draft_id: int, pack_dir: Path, *, seconds: float = 10.0, samples: int = 32) -> list[Path]:
    """One scene build → three clip renders (faster than rebuild per clip)."""
    clips_dir = pack_dir / "clips"
    phases = ("open", "wave", "lunge")
    paths: list[Path] = []
    ctx = build_scene(samples=samples)
    ctx["pack_dir"] = pack_dir
    for i, phase in enumerate(phases, start=1):
        dest = clips_dir / f"blender_part_{i:02d}.mp4"
        render_clip(ctx, dest, phase=phase, seconds=seconds)
        paths.append(dest)
    spec = {"backend": "blender", "clips": [p.name for p in paths], "draft_id": draft_id}
    (clips_dir / "blender_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return paths


def render_preview(out_png: Path, *, samples: int = 32, phase: str = "wave", pack_dir: Path | None = None) -> None:
    ctx = build_scene(samples=samples)
    if pack_dir:
        ctx["pack_dir"] = pack_dir
    scene = ctx["scene"]
    cam = ctx["camera"]
    form2 = ctx["form2"]
    armature = ctx.get("armature")
    f1 = 48
    _animate_camera_wave_lunge(
        cam, form2, frame_start=1, frame_end=f1, phase=phase, armature=armature,
        pack_dir=ctx.get("pack_dir"),
    )
    # Peak wave frame ~52% through clip
    peak = 1 + int((f1 - 1) * (0.52 if phase == "wave" else 0.85))
    scene.frame_set(peak)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(out_png)
    bpy.ops.render.render(write_still=True)
    print(f"Preview {out_png}")


def main(argv: list[str] | None = None) -> None:
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument(
        "--phase",
        choices=("open", "wave", "lunge"),
        default="wave",
        help="Animation phase for preview or single-clip test",
    )
    parser.add_argument("--clip-only", action="store_true", help="Render one clip for --phase only")
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--seconds", type=float, default=None, help="Clip length (default from env)")
    parser.add_argument("--samples", type=int, default=None, help="EEVEE TAA samples")
    args, _ = parser.parse_known_args(argv)

    seconds = args.seconds or float(os.environ.get("BLENDER_CLIP_SECONDS", "10"))
    samples = args.samples or int(os.environ.get("BLENDER_SAMPLES", "32"))

    pack = args.pack_dir or OUTPUT_ROOT / f"draft_{args.draft_id}"
    if args.preview:
        render_preview(
            pack / f"blender_preview_{args.phase}.png",
            samples=samples,
            phase=args.phase,
            pack_dir=pack,
        )
        return
    if args.clip_only:
        ctx = build_scene(samples=samples)
        ctx["pack_dir"] = pack
        dest = (pack / "clips" / f"blender_part_{args.phase}.mp4")
        render_clip(ctx, dest, phase=args.phase, seconds=seconds)
        return
    render_draft_short(args.draft_id, pack, seconds=seconds, samples=samples)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:])
