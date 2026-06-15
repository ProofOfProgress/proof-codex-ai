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

# Scene-first craft (course Part 3–5): polish gas station before creature returns.
SCENE_FOCAL = (0.0, -8.0, 2.2)  # pump island — camera look-at when no creature


def _include_creature() -> bool:
    raw = os.environ.get("BLENDER_INCLUDE_CREATURE", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _scene_only_mode() -> bool:
    if not _include_creature():
        return True
    return os.environ.get("BLENDER_SCENE_ONLY", "").strip().lower() in ("1", "true", "yes", "on")


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


def _add_ground_pad() -> bpy.types.Object:
    """Solid asphalt under imported FBX — closes void gaps at lot edges."""
    bpy.ops.mesh.primitive_plane_add(size=140, location=(0, -6, -0.04))
    pad = bpy.context.active_object
    pad.name = "GroundPad"
    pad.data.materials.append(_mat("AsphaltPad", (0.022, 0.022, 0.028, 1.0), rough=0.98))
    return pad


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
    fill.data.energy = 480
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


def _environment_mesh_bounds(objects: list) -> tuple[float, float, float, float, float, float] | None:
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            xs.append(world.x)
            ys.append(world.y)
            zs.append(world.z)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _texture_search_dirs(model_path: Path) -> list[Path]:
    """All local Texture folders for this gas-station pack."""
    dirs: list[Path] = []
    for candidate in (
        model_path.parent / "Textures",
        model_path.parent.parent / "Textures",
        model_path.parent.parent.parent / "Textures",
    ):
        if candidate.is_dir() and candidate not in dirs:
            dirs.append(candidate)
    return dirs


def _build_texture_index(dirs: list[Path]) -> dict[str, Path]:
    by_name: dict[str, Path] = {}
    for textures_dir in dirs:
        for img_path in textures_dir.rglob("*"):
            if img_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tga", ".bmp"}:
                by_name[img_path.name.lower()] = img_path
                by_name.setdefault(img_path.stem.lower(), img_path)
    return by_name


def _resolve_texture_path(raw: str, by_name: dict[str, Path]) -> Path | None:
    base = Path(raw.replace("\\", "/")).name.lower()
    if not base:
        return None
    hit = by_name.get(base)
    if hit:
        return hit
    stem = Path(base).stem.lower()
    return by_name.get(stem)


def _relink_environment_textures(model_path: Path) -> dict[str, int]:
    """Fix broken FBX image paths (Windows absolute) → local Textures/ dir."""
    dirs = _texture_search_dirs(model_path)
    if not dirs:
        return {"images_fixed": 0, "images_ok": 0, "images_missing": 0}

    by_name = _build_texture_index(dirs)
    stats = {"images_fixed": 0, "images_ok": 0, "images_missing": 0}

    def _fix_image(img) -> None:
        raw = (img.filepath_raw or img.filepath or img.name or "").replace("\\", "/")
        hit = _resolve_texture_path(raw, by_name)
        if hit is None:
            if img.size[0] == 0:
                stats["images_missing"] += 1
            else:
                stats["images_ok"] += 1
            return
        new_path = str(hit.resolve())
        if img.filepath_raw != new_path or img.size[0] == 0:
            img.filepath = new_path
            img.reload()
            stats["images_fixed"] += 1
        else:
            stats["images_ok"] += 1

    for img in list(bpy.data.images):
        if img.name in {"Render Result", "Viewer Node"}:
            continue
        _fix_image(img)

    for mat in bpy.data.materials:
        if not mat or not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image:
                _fix_image(node.image)
    return stats


def _material_has_texture(mat) -> bool:
    if not mat or not mat.use_nodes:
        return False
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image and node.image.size[0] > 0:
            return True
    return False


def _tweak_environment_night(root: bpy.types.Object) -> None:
    """Night horror grade — lighter when textures loaded so set stays readable."""
    for obj in root.children_recursive:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes:
                continue
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if not bsdf:
                continue
            textured = _material_has_texture(mat)
            if textured:
                # Part 5 rule: don't crush albedo when image nodes are live
                emit = bsdf.inputs.get("Emission Color")
                emit_str = bsdf.inputs.get("Emission Strength")
                if emit and emit_str and float(emit_str.default_value) > 0.05:
                    emit_str.default_value = float(emit_str.default_value) * 1.35
                continue
            col = bsdf.inputs["Base Color"].default_value
            dim = 0.42
            bsdf.inputs["Base Color"].default_value = (
                col[0] * dim,
                col[1] * (dim - 0.02 if textured else dim - 0.02),
                col[2] * (dim + 0.06 if textured else dim + 0.06),
                1.0,
            )
            bsdf.inputs["Roughness"].default_value = max(
                float(bsdf.inputs["Roughness"].default_value), 0.72 if textured else 0.78
            )
            emit = bsdf.inputs.get("Emission Color")
            emit_str = bsdf.inputs.get("Emission Strength")
            if emit and emit_str and float(emit_str.default_value) > 0.05:
                emit_str.default_value = float(emit_str.default_value) * 1.35


def _fit_environment_to_scene(root: bpy.types.Object, imported: list) -> None:
    bounds = _environment_mesh_bounds(imported)
    if not bounds:
        return
    x0, x1, y0, y1, z0, _z1 = bounds
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    offset_y = float(os.environ.get("BLENDER_ENV_OFFSET_Y", "-6"))
    root.location = (-cx, -cy + offset_y, -z0)
    bpy.context.view_layer.update()


def _import_gas_station_environment() -> bpy.types.Object | None:
    """CC0 Elbolilloduro gas station when present under channel/assets/environments/."""
    explicit = os.environ.get("BLENDER_ENVIRONMENT_MODEL", "").strip()
    workspace = Path(os.environ.get("WORKSPACE_ROOT", "/workspace"))
    hit: Path | None = None
    if explicit:
        p = Path(explicit)
        if p.is_file():
            hit = p
    if hit is None:
        try:
            sys.path.insert(0, str(workspace))
            from shorts_bot.production.blender.environment_paths import resolve_environment_model

            hit = resolve_environment_model()
        except Exception as exc:
            print(f"Environment lookup failed ({exc}) — procedural gas station")
            return None
    if not hit:
        return None

    print(f"Importing gas-station environment: {hit}")
    imported = _import_mesh_file(hit)
    if not imported:
        print(f"Environment import empty: {hit}")
        return None

    root = bpy.data.objects.new("GasStationEnv", None)
    bpy.context.collection.objects.link(root)
    scale = float(os.environ.get("BLENDER_ENV_SCALE", "0.07"))
    root.scale = Vector((scale, scale, scale))
    bpy.context.view_layer.update()
    for obj in imported:
        if obj.parent is None:
            obj.parent = root
    bpy.context.view_layer.update()
    relinked = _relink_environment_textures(hit)
    print(
        f"Environment textures: fixed={relinked['images_fixed']} "
        f"ok={relinked['images_ok']} missing={relinked['images_missing']}"
    )
    _fit_environment_to_scene(root, imported)
    _tweak_environment_night(root)
    _import_gas_station_props(root, hit.parent)
    return root


def _import_gas_station_props(env_root: bpy.types.Object, models_dir: Path) -> None:
    """Props FBX (signs, pumps detail) — parent to same env root."""
    props = models_dir / "Gas_station_Props.fbx"
    if not props.is_file():
        props = models_dir.parent / "Models" / "Gas_station_Props.fbx"
    if not props.is_file():
        return
    print(f"Importing gas-station props: {props}")
    imported = _import_mesh_file(props)
    for obj in imported:
        if obj.parent is None:
            obj.parent = env_root
    _relink_environment_textures(props)


def _tweak_imported_creature(rig: bpy.types.Object, *, profile: str = "form2_rural") -> None:
    """Peripheral Form 2 pass — darker, taller, wet-night horror."""
    if profile == "form2_rural" and not _micro_jumpscare_mode():
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


def _apply_creature_mouth_emissive(rig: bpy.types.Object) -> None:
    """Part 5 nodes — bloody mouth interior glows red when jaw opens at lunge peak."""
    if not (_micro_jumpscare_mode() or _creature_only_mode()):
        return
    strength = float(os.environ.get("BLENDER_MOUTH_EMISSIVE", "7.5"))
    mouth_rgb = (
        float(os.environ.get("BLENDER_MOUTH_RED", "0.95")),
        float(os.environ.get("BLENDER_MOUTH_GREEN", "0.04")),
        float(os.environ.get("BLENDER_MOUTH_BLUE", "0.02")),
        1.0,
    )
    for obj in rig.children_recursive:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes:
                continue
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bsdf = nodes.get("Principled BSDF")
            if not bsdf:
                continue
            tex = next((n for n in nodes if n.type == "TEX_IMAGE"), None)
            if not tex:
                continue
            sep = nodes.new("ShaderNodeSeparateColor")
            sep.mode = "RGB"
            sep.location = (tex.location.x + 220, tex.location.y - 120)
            links.new(tex.outputs["Color"], sep.inputs["Color"])
            r_gt = nodes.new("ShaderNodeMath")
            r_gt.operation = "GREATER_THAN"
            r_gt.inputs[1].default_value = 0.28
            r_gt.location = (sep.location.x + 160, sep.location.y + 40)
            links.new(sep.outputs["Red"], r_gt.inputs[0])
            rg = nodes.new("ShaderNodeMath")
            rg.operation = "SUBTRACT"
            rg.location = (sep.location.x + 160, sep.location.y - 20)
            links.new(sep.outputs["Red"], rg.inputs[0])
            links.new(sep.outputs["Green"], rg.inputs[1])
            rg_gt = nodes.new("ShaderNodeMath")
            rg_gt.operation = "GREATER_THAN"
            rg_gt.inputs[1].default_value = 0.06
            rg_gt.location = (sep.location.x + 320, sep.location.y - 20)
            links.new(rg.outputs[0], rg_gt.inputs[0])
            mask = nodes.new("ShaderNodeMath")
            mask.operation = "MULTIPLY"
            mask.location = (sep.location.x + 480, sep.location.y + 10)
            links.new(r_gt.outputs[0], mask.inputs[0])
            links.new(rg_gt.outputs[0], mask.inputs[1])
            emit_mul = nodes.new("ShaderNodeMath")
            emit_mul.operation = "MULTIPLY"
            emit_mul.inputs[1].default_value = strength
            emit_mul.location = (sep.location.x + 640, sep.location.y + 10)
            links.new(mask.outputs[0], emit_mul.inputs[0])
            bsdf.inputs["Emission Color"].default_value = mouth_rgb
            links.new(emit_mul.outputs[0], bsdf.inputs["Emission Strength"])
    print(f"Mouth emissive wired (strength={strength})")


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


def _creature_target_height() -> float:
    if _micro_jumpscare_mode():
        return float(
            os.environ.get(
                "BLENDER_CREATURE_TARGET_HEIGHT",
                os.environ.get("MICRO_CREATURE_HEIGHT", "1.85"),
            )
        )
    return float(os.environ.get("BLENDER_CREATURE_TARGET_HEIGHT", "2.45"))


def _micro_creature_uniform_scale() -> float:
    return float(os.environ.get("BLENDER_MICRO_CREATURE_SCALE", "0.82"))


def _apply_micro_creature_scale(form2: bpy.types.Object) -> None:
    """Human-scale next to gas-station FBX — not tower over the road."""
    s = _micro_creature_uniform_scale()
    form2.scale = Vector((s, s, s))
    _ground_creature(form2)
    bpy.context.view_layer.update()


def _normalize_creature_rig(rig: bpy.types.Object, *, target_height: float | None = None) -> None:
    """Scale import to target height in meters (lore or micro gas-station proportion)."""
    if target_height is None:
        target_height = _creature_target_height()
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
    _apply_creature_mouth_emissive(rig)
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


def _camera_point_at_rule_thirds(
    cam: bpy.types.Object,
    target: tuple[float, float, float],
    *,
    frame_line: float = 2 / 3,
) -> None:
    """Rule of thirds — place target on a horizontal screen line (0=bottom, 1=top)."""
    _camera_point_at(cam, target)
    # Positive shift_y moves image down; negative raises subject toward top third.
    cam.data.shift_y = (0.5 - frame_line) * 0.58


def _creature_face_target(
    form2: bpy.types.Object,
    armature: bpy.types.Object | None = None,
) -> tuple[float, float, float]:
    """World position of face/head — for gaze and framing."""
    if armature and armature.type == "ARMATURE":
        bpy.context.view_layer.update()
        pb = armature.pose.bones.get("head")
        if pb:
            w = armature.matrix_world @ pb.head
            return (float(w.x), float(w.y), float(w.z))
    loc = form2.location
    head_z = float(loc.z) + 1.52 * float(form2.scale.z)
    return (float(loc.x), float(loc.y), head_z)


def _creature_eye_target(form2: bpy.types.Object) -> tuple[float, float, float]:
    """Approximate eye height for SCP-096 / Form 2 rig."""
    return _creature_face_target(form2)


def _camera_point_at(cam: bpy.types.Object, target: tuple[float, float, float]) -> None:
    """Part 3 — aim camera at world target using TRACK_TO (course: constraints → code)."""
    empty = bpy.data.objects.new("_PeripheralLookAt", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = target
    con = cam.constraints.new("TRACK_TO")
    con.target = empty
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    bpy.context.view_layer.update()
    try:
        bpy.ops.object.select_all(action="DESELECT")
        cam.select_set(True)
        bpy.context.view_layer.objects.active = cam
        bpy.ops.constraint.apply(constraint=con.name, owner="OBJECT")
    except Exception:
        # Fallback: manual quat
        direction = Vector(target) - cam.location
        if direction.length > 0.001:
            cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    finally:
        cam.constraints.clear()
        bpy.data.objects.remove(empty, do_unlink=True)


def _setup_camera_scene() -> bpy.types.Object:
    """Part 3 — POV for environment craft (no creature)."""
    bpy.ops.object.camera_add(location=(0, -3.5, 1.6))
    cam = bpy.context.active_object
    cam.name = "POVCamera"
    cam.data.lens = 32
    _camera_point_at(cam, SCENE_FOCAL)
    bpy.context.scene.camera = cam
    return cam


def _setup_camera() -> bpy.types.Object:
    if _scene_only_mode():
        return _setup_camera_scene()
    bpy.ops.object.camera_add(location=(0, -5.5, 1.55))
    cam = bpy.context.active_object
    cam.name = "POVCamera"
    cam.data.lens = 28
    _camera_point_at(cam, (0, -9.0, 1.6))
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
    bg.inputs[0].default_value = (0.035, 0.045, 0.07, 1.0)
    bg.inputs[1].default_value = 0.85
    if hasattr(scene.view_settings, "exposure"):
        scene.view_settings.exposure = 0.6
    scene.eevee.use_ssr = True
    scene.eevee.use_ssr_refraction = False
    scene.eevee.gi_diffuse_bounces = 2
    scene.eevee.gi_cubemap_resolution = "512"


def _flicker_keyframes(lamp_obj: bpy.types.Object | bpy.types.Light | None, frame_start: int, frame_end: int) -> None:
    """Streetlight strobes — keyframes avoid headless driver restrictions."""
    if lamp_obj is None:
        return
    lamp_data = lamp_obj.data if isinstance(lamp_obj, bpy.types.Object) else lamp_obj
    if not hasattr(lamp_data, "energy"):
        return
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


def _add_fog_and_trees(*, env_loaded: bool = False) -> None:
    """Volumetric fog — skip procedural trees when real gas-station FBX is loaded."""
    scene = bpy.context.scene
    if not env_loaded:
        trunk = _mat("PineTrunk", (0.04, 0.03, 0.02, 1.0), rough=0.95)
        needle = _mat("PineNeedle", (0.02, 0.04, 0.03, 1.0), rough=0.9)
        for x, y, h in [(-12, -16, 7), (14, -18, 9), (-8, -22, 6), (18, -14, 8)]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=h * 0.35, location=(x, y, h * 0.18))
            t = bpy.context.active_object
            t.data.materials.append(trunk)
            bpy.ops.mesh.primitive_cone_add(radius1=h * 0.45, depth=h * 0.65, location=(x, y, h * 0.65))
            c = bpy.context.active_object
            c.data.materials.append(needle)

    if scene.world and scene.world.node_tree:
        nodes = scene.world.node_tree.nodes
        links = scene.world.node_tree.links
        output = nodes.get("World Output")
        if output and not output.inputs["Volume"].links:
            vol = nodes.new("ShaderNodeVolumeScatter")
            vol.inputs["Density"].default_value = 0.002 if env_loaded else 0.005
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


def _lunge_action_trim() -> tuple[int, int] | None:
    """Mixamo strip window — attack/roar frames land on lunge peak."""
    raw = os.environ.get("BLENDER_LUNGE_ACTION_TRIM", "78,140").strip()
    if not raw or raw.lower() in ("0", "none", "off", "full"):
        return None
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) != 2:
        return None
    return int(parts[0]), int(parts[1])


def _apply_proscenium_fbx(
    armature: bpy.types.Object,
    fbx_path: Path,
    *,
    frame_start: int,
    frame_end: int,
    action_trim: tuple[int, int] | None = None,
) -> bool:
    """Import Proscenium/Mixamo FBX action onto the scene armature."""
    if armature.type != "ARMATURE" or not fbx_path.is_file():
        return False

    before_objects = {o.name for o in bpy.data.objects}
    before_actions = {a.name for a in bpy.data.actions}

    try:
        if fbx_path.suffix.lower() == ".blend":
            with bpy.data.libraries.load(str(fbx_path), link=False) as (data_from, data_to):
                if data_from.actions:
                    data_to.actions = [data_from.actions[0]]
            new_actions = [a for a in bpy.data.actions if a.name not in before_actions]
            action = new_actions[0] if new_actions else None
        else:
            bpy.ops.import_scene.fbx(
                filepath=str(fbx_path),
                use_anim=True,
                ignore_leaf_bones=False,
                automatic_bone_orientation=False,
            )
            new_actions = [a for a in bpy.data.actions if a.name not in before_actions]
            imported_armatures = [
                o for o in bpy.data.objects
                if o.name not in before_objects and o.type == "ARMATURE"
            ]
            action = new_actions[0] if new_actions else None
            if not action and imported_armatures:
                ia = imported_armatures[0]
                if ia.animation_data and ia.animation_data.action:
                    action = ia.animation_data.action
            for obj in list(bpy.data.objects):
                if obj.name not in before_objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
    except Exception as exc:
        print(f"Proscenium FBX import failed ({fbx_path}): {exc}")
        return False

    if not action:
        print(f"No animation action in export: {fbx_path}")
        return False

    _clear_armature_animation(armature)
    ad = armature.animation_data or armature.animation_data_create()
    act_start = int(action.frame_range[0])
    act_end = int(action.frame_range[1])
    if action_trim:
        act_start = max(act_start, int(action_trim[0]))
        act_end = min(act_end, int(action_trim[1]))
    if act_end <= act_start:
        act_end = act_start + int(10 * FPS)

    track = ad.nla_tracks.new()
    track.name = f"Proscenium_{fbx_path.stem}"
    strip = track.strips.new(action.name, frame_start, action)
    strip.action_frame_start = act_start
    strip.action_frame_end = act_end
    clip_frames = max(1, frame_end - frame_start)
    action_frames = max(1, act_end - act_start)
    strip.frame_end = frame_start + clip_frames
    if action_frames != clip_frames:
        strip.scale = clip_frames / action_frames
    strip.blend_type = "REPLACE"
    ad.use_nla = True
    print(f"Applied Proscenium motion: {fbx_path.name} → {armature.name}")
    return True


def _resolve_proscenium_fbx(pack_dir: Path | None, phase: str) -> Path | None:
    if not pack_dir:
        return None
    workspace = Path(os.environ.get("WORKSPACE_ROOT", "/workspace"))
    try:
        sys.path.insert(0, str(workspace))
        from shorts_bot.production.blender.motion_exports import draft_id_from_pack, resolve_motion_fbx

        draft_id = draft_id_from_pack(pack_dir)
        if draft_id is None:
            return None
        return resolve_motion_fbx(draft_id, phase)
    except Exception as exc:
        print(f"Proscenium FBX lookup failed: {exc}")
        return None


def _play_creature_action(
    armature: bpy.types.Object,
    *,
    phase: str,
    frame_start: int,
    frame_end: int,
    pack_dir: Path | None = None,
) -> None:
    """Motion from Proscenium FBX export, motion_{phase}.json, or procedural fallback."""
    _clear_armature_animation(armature)

    from shorts_bot.production.blender.motion_backend import use_downloaded_motion

    if use_downloaded_motion() and pack_dir:
        fbx = _resolve_proscenium_fbx(pack_dir, phase)
        trim = _lunge_action_trim() if phase == "lunge" else None
        if fbx and _apply_proscenium_fbx(
            armature,
            fbx,
            frame_start=frame_start,
            frame_end=frame_end,
            action_trim=trim,
        ):
            return

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
        dur = max(1, frame_end - frame_start)
        t = lambda frac: frame_start + int(dur * frac)
        lunge_f = frame_end - max(8, int(dur * 0.15))
        snap_f = frame_end - 4
        for name, rot, fr in [
            ("pelvis", (0, 0, 0), frame_start),
            ("pelvis", (0.22, 0, 0), lunge_f),
            ("pelvis", (0.38, 0, 0), frame_end),
            ("ripcage", (0.12, 0, 0), t(0.35)),
            ("ripcage", (0.35, 0, 0), lunge_f),
            ("ripcage", (0.58, 0, 0), frame_end),
            ("neck", (0.15, 0, 0), lunge_f),
            ("neck", (0.42, 0, 0), snap_f),
            ("neck", (0.52, 0, 0), frame_end),
            ("head", (0.08, 0, 0), lunge_f),
            ("head", (0.38, 0, 0), snap_f),
            ("head", (0.48, 0, 0), frame_end),
            ("lowerjaw", (0.05, 0, 0), lunge_f),
            ("lowerjaw", (0.45, 0, 0), snap_f),
            ("lowerjaw", (0.72, 0, 0), frame_end),
            ("Bone_007", (-1.4, 0.1, -0.2), lunge_f),
            ("Bone_007", (-2.35, 0, 0.15), frame_end),
            ("Bone_008", (-1.35, -0.1, 0.2), lunge_f),
            ("Bone_008", (-2.3, 0, -0.12), frame_end),
        ]:
            _key_bone(name, rot, fr)

    bpy.ops.object.mode_set(mode="OBJECT")
    if prev_active:
        bpy.context.view_layer.objects.active = prev_active


def _apply_lunge_gaze_correction(
    armature: bpy.types.Object,
    form2: bpy.types.Object,
    cam: bpy.types.Object,
    *,
    bait_f: int,
    frame_end: int,
    mixamo_overlay: bool = True,
) -> None:
    """Tilt head/neck up toward camera at lunge peak — counter Mixamo forward lean."""
    if armature.type != "ARMATURE":
        return
    eye = Vector(_creature_face_target(form2, armature))
    delta = Vector(cam.location) - eye
    horiz = math.sqrt(delta.x ** 2 + delta.y ** 2)
    # Positive X euler = look up (rig convention used in _pose_wave_or_lunge lunge keys).
    base_pitch = math.atan2(delta.z, horiz) if horiz > 0.01 else 0.0
    mixamo_boost = 0.48 if mixamo_overlay else 0.12
    head_pitch = min(1.08, max(0.5, base_pitch + mixamo_boost))
    neck_pitch = head_pitch * 0.74
    rib_pitch = head_pitch * 0.4
    mid_f = bait_f + max(2, int((frame_end - bait_f) * 0.42))

    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = armature
    if armature.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")

    def _key_bone(name: str, rot: tuple[float, float, float], frame: int) -> None:
        pb = armature.pose.bones.get(name)
        if not pb:
            return
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = rot
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    for fr, hp, np, rp in [
        (bait_f, 0.08, 0.06, 0.04),
        (mid_f, head_pitch * 0.55, neck_pitch * 0.55, rib_pitch * 0.55),
        (frame_end, head_pitch, neck_pitch, rib_pitch),
    ]:
        _key_bone("ripcage", (rp, 0, 0), fr)
        _key_bone("neck", (np, 0, 0), fr)
        _key_bone("head", (hp, 0, 0), fr)

    bpy.ops.object.mode_set(mode="OBJECT")
    if prev_active:
        bpy.context.view_layer.objects.active = prev_active


def _apply_lunge_mouth_open(
    armature: bpy.types.Object,
    *,
    bait_f: int,
    frame_end: int,
) -> None:
    """Drop jaw into screaming pose at lunge peak — face fills the lens."""
    if armature.type != "ARMATURE":
        return
    snap_f = max(bait_f + 2, frame_end - 6)
    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = armature
    if armature.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")

    def _key_bone(name: str, rot: tuple[float, float, float], frame: int) -> None:
        pb = armature.pose.bones.get(name)
        if not pb:
            return
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = rot
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    for fr, jaw in [
        (bait_f, 0.02),
        (snap_f, 0.28),
        (frame_end, 0.92),
    ]:
        for jaw_bone in ("lowerjaw", "lowerjaw_001"):
            _key_bone(jaw_bone, (jaw, 0, 0), fr)

    bpy.ops.object.mode_set(mode="OBJECT")
    if prev_active:
        bpy.context.view_layer.objects.active = prev_active


def _animate_scene_camera(
    cam: bpy.types.Object,
    *,
    frame_start: int,
    frame_end: int,
    phase: str,
) -> None:
    """Environment-only camera — slow dolly/pan across gas-station lot (Part 3)."""
    cam.animation_data_clear()
    focal = SCENE_FOCAL
    if phase == "open":
        start, end = (0, 1.5, 1.65), (0, -2.5, 1.55)
    elif phase == "wave":
        start, end = (0, -4.0, 1.55), (1.2, -6.5, 1.5)
    else:
        start, end = (0.5, -5.5, 1.55), (0, -7.0, 1.85)
    cam.location = start
    _camera_point_at(cam, focal)
    cam.keyframe_insert(data_path="location", frame=frame_start)
    cam.keyframe_insert(data_path="rotation_euler", frame=frame_start)
    cam.location = end
    _camera_point_at(cam, focal)
    cam.keyframe_insert(data_path="location", frame=frame_end)
    cam.keyframe_insert(data_path="rotation_euler", frame=frame_end)


def _creature_only_mode() -> bool:
    return os.environ.get("BLENDER_CREATURE_ONLY", "").strip().lower() in ("1", "true", "yes", "on")


def _micro_jumpscare_mode() -> bool:
    return os.environ.get("BLENDER_MICRO_JUMPSCARE", "").strip().lower() in ("1", "true", "yes")


def _setup_creature_only_world(scene: bpy.types.Scene) -> None:
    """Void backdrop — monster lunge lab only."""
    if scene.world is None:
        scene.world = bpy.data.worlds.new("PeripheralWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.008, 0.01, 0.014, 1.0)
    bg.inputs[1].default_value = 1.0
    if hasattr(scene.view_settings, "exposure"):
        scene.view_settings.exposure = float(os.environ.get("BLENDER_EXPOSURE", "0.65"))


def _add_creature_only_lights() -> bpy.types.Light:
    """Horror rim + key — no streetlight, no environment."""
    bpy.ops.object.light_add(type="AREA", location=(1.5, -2, 2.8))
    key = bpy.context.active_object
    key.name = "CreatureKey"
    key.data.energy = 620
    key.data.color = (0.82, 0.88, 1.0)
    key.data.size = 3.5
    key.rotation_euler = (math.radians(58), 0, math.radians(200))
    bpy.ops.object.light_add(type="SPOT", location=(-1.2, -1.5, 2.2))
    rim = bpy.context.active_object
    rim.name = "CreatureRim"
    rim.data.energy = 900
    rim.data.color = (1.0, 0.42, 0.18)
    rim.data.spot_size = math.radians(48)
    rim.rotation_euler = (math.radians(115), 0, math.radians(160))
    bpy.ops.object.light_add(type="POINT", location=(0, -3, 1.2))
    fill = bpy.context.active_object
    fill.name = "CreatureFill"
    fill.data.energy = 240
    fill.data.color = (0.55, 0.6, 0.75)
    bpy.ops.object.light_add(type="POINT", location=(0, -4.6, 1.52))
    mouth = bpy.context.active_object
    mouth.name = "CreatureMouthFill"
    mouth.data.energy = 0.0
    mouth.data.color = (1.0, 0.12, 0.05)
    mouth.data.shadow_soft_size = 0.06
    return fill


def _animate_creature_mouth_light(
    *,
    frame_start: int,
    bait_f: int,
    frame_end: int,
    peak_location: tuple[float, float, float],
) -> None:
    """Pulse red mouth fill at lunge peak so final frame reads bloody."""
    mouth = bpy.data.objects.get("CreatureMouthFill")
    if not mouth or mouth.type != "LIGHT":
        return
    px, py, pz = peak_location
    mouth.animation_data_clear()
    mouth.location = (px, py - 2.0, pz)
    mouth.data.energy = 0.0
    mouth.keyframe_insert(data_path="location", frame=frame_start)
    mouth.data.keyframe_insert(data_path="energy", frame=frame_start)
    snap_f = max(bait_f + 2, frame_end - 8)
    mouth.location = (px, py + 0.12, pz - 0.08)
    mouth.data.energy = 55.0
    mouth.keyframe_insert(data_path="location", frame=snap_f)
    mouth.data.keyframe_insert(data_path="energy", frame=snap_f)
    mouth.location = (px, py + 0.06, pz - 0.03)
    mouth.data.energy = 980.0
    mouth.keyframe_insert(data_path="location", frame=frame_end)
    mouth.data.keyframe_insert(data_path="energy", frame=frame_end)


def _lunge_camera_height() -> float:
    """Part 3 — POV height (m). Raised default so viewer looks slightly down at the creature."""
    return float(os.environ.get("BLENDER_LUNGE_CAMERA_Z", "2.18"))


def _creature_lunge_look_target() -> tuple[float, float, float]:
    """Static fallback — prefer _keyframe_camera_track_face at runtime."""
    return (
        0.0,
        -8.0,
        float(os.environ.get("BLENDER_LUNGE_LOOK_Z", "2.05")),
    )


def _keyframe_camera_track_face(
    cam: bpy.types.Object,
    form2: bpy.types.Object,
    armature: bpy.types.Object | None,
    frame: int,
    *,
    frame_line: float,
) -> None:
    """Aim camera at creature head on this frame (pose must be keyed before call)."""
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    face = _creature_face_target(form2, armature)
    _camera_point_at_rule_thirds(cam, face, frame_line=frame_line)
    cam.keyframe_insert(data_path="rotation_euler", frame=frame)
    cam.data.keyframe_insert(data_path="shift_y", frame=frame)


def _creature_lunge_camera_positions() -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Start/end camera locations — locked heading, dolly only (course Part 3 keyframes)."""
    z = _lunge_camera_height()
    return (0.0, -4.35, z), (0.0, -3.92, z - 0.08)


def _setup_creature_lunge_camera() -> bpy.types.Object:
    """Fixed POV for lunge training — wide lens, eyes on top third at peak."""
    line = float(os.environ.get("BLENDER_RULE_OF_THIRDS", str(2 / 3)))
    bpy.ops.object.camera_add(location=(0.0, -4.2, _lunge_camera_height()))
    cam = bpy.context.active_object
    cam.name = "LungeCamera"
    cam.data.lens = float(os.environ.get("BLENDER_LUNGE_FOCAL_MM", "26"))
    _camera_point_at_rule_thirds(cam, _creature_lunge_look_target(), frame_line=line)
    bpy.context.scene.camera = cam
    return cam


def _animate_creature_lunge_lab(
    cam: bpy.types.Object,
    form2: bpy.types.Object,
    *,
    frame_start: int,
    frame_end: int,
    armature: bpy.types.Object | None = None,
    pack_dir: Path | None = None,
) -> None:
    """Monster-only: dolly + sprint — camera tracks head; open mouth fills lens at peak."""
    line = float(os.environ.get("BLENDER_RULE_OF_THIRDS", str(2 / 3)))
    peak_line = float(os.environ.get("BLENDER_LUNGE_PEAK_FRAME_LINE", "0.78"))
    bait_f = frame_start + max(6, int((frame_end - frame_start) * 0.12))
    lunge_f = frame_start + max(bait_f + 2, int((frame_end - frame_start) * 0.38))
    base_s = 1.0 if _creature_only_mode() else (
        _micro_creature_uniform_scale() if _micro_jumpscare_mode() else 1.0
    )
    face_scale = float(os.environ.get("BLENDER_LUNGE_FACE_SCALE", "1.38"))
    cam_start, cam_end = _creature_lunge_camera_positions()
    creep_end = (0.0, -7.2, 0.0)
    face_end = (0.0, -4.62, -0.05)

    cam.animation_data_clear()
    form2.animation_data_clear()
    # Dolly only on location — rotation tracks head each beat (never lock on pelvis/crotch).
    cam.location = cam_start
    cam.keyframe_insert(data_path="location", frame=frame_start)
    cam.location = cam_start
    cam.keyframe_insert(data_path="location", frame=bait_f)
    cam.location = cam_end
    cam.keyframe_insert(data_path="location", frame=frame_end)

    # Creature — far hold → sprint → in-your-face (mouth open at frame_end)
    form2.location = (0, -9.5, 0)
    form2.scale = (base_s, base_s, base_s)
    form2.rotation_euler = (0, 0, 0)
    form2.keyframe_insert(data_path="location", frame=frame_start)
    form2.keyframe_insert(data_path="scale", frame=frame_start)
    form2.keyframe_insert(data_path="rotation_euler", frame=frame_start)
    form2.location = creep_end
    form2.keyframe_insert(data_path="location", frame=bait_f)
    form2.location = (0, -5.4, 0.0)
    form2.keyframe_insert(data_path="location", frame=lunge_f)
    form2.location = face_end
    form2.scale = (base_s * face_scale, base_s * face_scale, base_s * face_scale)
    form2.rotation_euler = (0.10, 0, 0)
    form2.keyframe_insert(data_path="location", frame=frame_end)
    form2.keyframe_insert(data_path="scale", frame=frame_end)
    form2.keyframe_insert(data_path="rotation_euler", frame=frame_end)
    if armature:
        from shorts_bot.production.blender.motion_backend import use_downloaded_motion

        downloaded = use_downloaded_motion()
        _play_creature_action(
            armature,
            phase="lunge",
            frame_start=frame_start,
            frame_end=frame_end,
            pack_dir=pack_dir,
        )
        _apply_lunge_gaze_correction(
            armature,
            form2,
            cam,
            bait_f=bait_f,
            frame_end=frame_end,
            mixamo_overlay=downloaded,
        )
        _apply_lunge_mouth_open(armature, bait_f=bait_f, frame_end=frame_end)
    for fr, fl in (
        (frame_start, line),
        (bait_f, line),
        (lunge_f, line + 0.04),
        (frame_end, peak_line),
    ):
        _keyframe_camera_track_face(cam, form2, armature, fr, frame_line=fl)
    saved_loc = form2.location.copy()
    saved_scale = form2.scale.copy()
    form2.location = face_end
    form2.scale = (base_s * face_scale, base_s * face_scale, base_s * face_scale)
    bpy.context.view_layer.update()
    peak_face = _creature_face_target(form2, armature)
    form2.location = saved_loc
    form2.scale = saved_scale
    _animate_creature_mouth_light(
        frame_start=frame_start,
        bait_f=bait_f,
        frame_end=frame_end,
        peak_location=peak_face,
    )


def _animate_micro_jumpscare(
    cam: bpy.types.Object,
    form2: bpy.types.Object,
    *,
    frame_start: int,
    frame_end: int,
    armature: bpy.types.Object | None = None,
    pack_dir: Path | None = None,
) -> None:
    """3s format: ~0.4s bait → lunge; fixed camera heading (dolly only — no spin)."""
    line = float(os.environ.get("BLENDER_RULE_OF_THIRDS", str(2 / 3)))
    base_s = _micro_creature_uniform_scale()
    bait_f = frame_start + max(8, int((frame_end - frame_start) * 0.14))
    cam.animation_data_clear()
    form2.animation_data_clear()
    cam.data.shift_y = 0.0
    # Lock POV down the lot — rotation stays constant; only dolly forward on lunge.
    look_target = SCENE_FOCAL
    cam.location = (0, -5.0, 2.15)
    _camera_point_at_rule_thirds(cam, look_target, frame_line=line)
    fixed_rot = cam.rotation_euler.copy()
    fixed_shift = cam.data.shift_y
    cam.keyframe_insert(data_path="location", frame=frame_start)
    cam.keyframe_insert(data_path="rotation_euler", frame=frame_start)
    cam.data.keyframe_insert(data_path="shift_y", frame=frame_start)
    form2.location = (0, -11.0, 0)
    form2.scale = (base_s, base_s, base_s)
    form2.keyframe_insert(data_path="location", frame=frame_start)
    form2.keyframe_insert(data_path="scale", frame=frame_start)
    # Bait hold — same heading
    cam.location = (0, -5.0, 2.15)
    cam.rotation_euler = fixed_rot
    cam.data.shift_y = fixed_shift
    cam.keyframe_insert(data_path="location", frame=bait_f)
    cam.keyframe_insert(data_path="rotation_euler", frame=bait_f)
    cam.data.keyframe_insert(data_path="shift_y", frame=bait_f)
    form2.keyframe_insert(data_path="location", frame=bait_f)
    # Lunge — dolly in; creature runs into fixed frame (no look-at whip)
    lunge_s = base_s * 1.06
    form2.location = (0, -2.4, 0.88)
    form2.scale = (lunge_s, lunge_s, lunge_s)
    form2.keyframe_insert(data_path="location", frame=frame_end)
    form2.keyframe_insert(data_path="scale", frame=frame_end)
    cam.location = (0, -2.85, 2.35)
    cam.rotation_euler = fixed_rot
    cam.data.shift_y = fixed_shift
    cam.keyframe_insert(data_path="location", frame=frame_end)
    cam.keyframe_insert(data_path="rotation_euler", frame=frame_end)
    cam.data.keyframe_insert(data_path="shift_y", frame=frame_end)
    if armature:
        from shorts_bot.production.blender.motion_backend import use_downloaded_motion

        downloaded = use_downloaded_motion()
        _play_creature_action(
            armature,
            phase="lunge",
            frame_start=frame_start,
            frame_end=frame_end,
            pack_dir=pack_dir,
        )
        _apply_lunge_gaze_correction(
            armature,
            form2,
            cam,
            bait_f=bait_f,
            frame_end=frame_end,
            mixamo_overlay=downloaded,
        )


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
    from shorts_bot.production.blender.scene_layout import creature_wave_positions, load_scene_layout

    layout = load_scene_layout(pack_dir)
    cam.animation_data_clear()
    form2.animation_data_clear()
    cam.keyframe_insert(data_path="location", frame=frame_start)

    if phase == "open":
        cam.location = (0, 4, 1.65)
        _camera_point_at(cam, (0, -8, 2.0))
        cam.keyframe_insert(data_path="location", frame=frame_start)
        cam.keyframe_insert(data_path="rotation_euler", frame=frame_start)
        cam.location = (0, -2, 1.65)
        _camera_point_at(cam, (0, -9, 1.5))
        cam.keyframe_insert(data_path="location", frame=frame_end - 4)
        cam.keyframe_insert(data_path="rotation_euler", frame=frame_end - 4)
        form2.location = (0, -14, 0)
        form2.keyframe_insert(data_path="location", frame=frame_start)
        form2.location = (0, -11, 0)
        form2.keyframe_insert(data_path="location", frame=frame_end)
    elif phase == "wave":
        wave_start, wave_end, wave_scale = creature_wave_positions(layout)
        cam_start = (0, -5.5, 1.55)
        cam_end = (0.4, -7.0, 1.5)
        cam.location = cam_start
        _camera_point_at(cam, tuple(wave_start))
        cam.keyframe_insert(data_path="location", frame=frame_start)
        cam.keyframe_insert(data_path="rotation_euler", frame=frame_start)
        cam.location = cam_end
        _camera_point_at(cam, (wave_start[0], wave_start[1] - 0.5, 1.65))
        cam.keyframe_insert(data_path="location", frame=frame_end)
        cam.keyframe_insert(data_path="rotation_euler", frame=frame_end)
        form2.location = tuple(wave_start)
        form2.keyframe_insert(data_path="location", frame=frame_start)
        form2.rotation_euler = (0, 0, 0)
        form2.keyframe_insert(data_path="rotation_euler", frame=frame_start + 6)
        form2.rotation_euler = (0, 0, math.radians(8))
        form2.keyframe_insert(data_path="rotation_euler", frame=frame_end - 8)
        form2.location = tuple(wave_end)
        form2.keyframe_insert(data_path="location", frame=frame_end)
        if wave_scale:
            form2.scale = tuple(wave_scale)
            form2.keyframe_insert(data_path="scale", frame=frame_start)
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


def build_scene(*, samples: int = 32, pack_dir: Path | None = None) -> dict:
    _clear_scene()
    scene = bpy.context.scene
    env = None
    lamp: bpy.types.Light | None = None
    if _creature_only_mode():
        print("Creature-only lunge lab — no environment")
        _setup_render(scene, samples=samples)
        _setup_creature_only_world(scene)
        lamp = _add_creature_only_lights()
        form2 = _build_creature() if _include_creature() else None
        armature = _find_armature(form2) if form2 else None
        cam = _setup_creature_lunge_camera()
        if form2 and _micro_jumpscare_mode() and not _creature_only_mode():
            _apply_micro_creature_scale(form2)
        return {
            "scene": scene,
            "camera": cam,
            "form2": form2,
            "lamp": lamp,
            "armature": armature,
            "environment": None,
            "pack_dir": pack_dir,
            "scene_only": False,
            "creature_only": True,
        }
    env = _import_gas_station_environment()
    if env is None:
        _add_ground_and_road()
        _add_gas_station()
    else:
        _add_ground_pad()
    pole_empty, lamp = _add_streetlight()
    form2: bpy.types.Object | None = None
    armature = None
    if _include_creature():
        form2 = _build_creature()
        armature = _find_armature(form2)
    else:
        print("Scene-only mode — creature skipped (set BLENDER_INCLUDE_CREATURE=1 to restore)")
    cam = _setup_camera()
    _setup_render(scene, samples=samples)
    _add_eevee_light_probes()
    _add_fog_and_trees(env_loaded=env is not None)
    if pack_dir and form2 is not None:
        from shorts_bot.production.blender.scene_layout import apply_scene_layout

        apply_scene_layout(pack_dir, camera=cam, creature=form2, environment=env)
        if _micro_jumpscare_mode():
            _apply_micro_creature_scale(form2)
    elif pack_dir and env is not None:
        from shorts_bot.production.blender.scene_layout import load_scene_layout

        layout = load_scene_layout(pack_dir)
        env_cfg = layout.get("environment") or {}
        if scale := env_cfg.get("scale"):
            s = float(scale)
            env.scale = Vector((s, s, s))
    return {
        "scene": scene,
        "camera": cam,
        "form2": form2,
        "lamp": lamp,
        "armature": armature,
        "environment": env,
        "pack_dir": pack_dir,
        "scene_only": _scene_only_mode(),
        "creature_only": False,
    }


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
    if lamp and not ctx.get("creature_only"):
        _flicker_keyframes(lamp, f0, f1)
    if ctx.get("scene_only") or form2 is None:
        _animate_scene_camera(cam, frame_start=f0, frame_end=f1, phase=phase)
    elif ctx.get("creature_only") and phase == "lunge":
        _animate_creature_lunge_lab(
            cam, form2, frame_start=f0, frame_end=f1, armature=armature,
            pack_dir=ctx.get("pack_dir"),
        )
    elif _micro_jumpscare_mode() and phase == "lunge":
        _animate_micro_jumpscare(
            cam, form2, frame_start=f0, frame_end=f1, armature=armature,
            pack_dir=ctx.get("pack_dir"),
        )
    else:
        _animate_camera_wave_lunge(
            cam, form2, frame_start=f0, frame_end=f1, phase=phase, armature=armature,
            pack_dir=ctx.get("pack_dir"),
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_path.with_suffix(""))
    bpy.ops.render.render(animation=True)
    _finalize_clip_output(out_path)
    print(f"Rendered {out_path}")


def render_micro_jumpscare(draft_id: int, pack_dir: Path, *, seconds: float = 3.0, samples: int = 32) -> Path:
    """Single 3s lunge clip — creature on, one blender_part_01.mp4."""
    clips_dir = pack_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    os.environ["BLENDER_INCLUDE_CREATURE"] = "1"
    os.environ["BLENDER_MICRO_JUMPSCARE"] = "1"
    os.environ["BLENDER_CREATURE_ONLY"] = "1"
    ctx = build_scene(samples=samples, pack_dir=pack_dir)
    ctx["pack_dir"] = pack_dir
    dest = clips_dir / "blender_part_01.mp4"
    render_clip(ctx, dest, phase="lunge", seconds=seconds)
    spec = {
        "backend": "blender",
        "format": "micro_jumpscare",
        "creature_only": True,
        "clips": [dest.name],
        "draft_id": draft_id,
        "clip_seconds": seconds,
    }
    (clips_dir / "blender_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    lab_marker = {
        "lab": "creature_lunge",
        "creature_only": True,
        "draft_id": draft_id,
        "clip_seconds": seconds,
    }
    (pack_dir / "creature_lunge_lab.json").write_text(json.dumps(lab_marker, indent=2), encoding="utf-8")
    return dest


def render_draft_short(draft_id: int, pack_dir: Path, *, seconds: float = 10.0, samples: int = 32) -> list[Path]:
    """One scene build → three clip renders (faster than rebuild per clip)."""
    clips_dir = pack_dir / "clips"
    phases = ("open", "wave", "lunge")
    paths: list[Path] = []
    ctx = build_scene(samples=samples, pack_dir=pack_dir)
    ctx["pack_dir"] = pack_dir
    for i, phase in enumerate(phases, start=1):
        dest = clips_dir / f"blender_part_{i:02d}.mp4"
        render_clip(ctx, dest, phase=phase, seconds=seconds)
        paths.append(dest)
    spec = {"backend": "blender", "clips": [p.name for p in paths], "draft_id": draft_id}
    (clips_dir / "blender_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return paths


def save_scene_blend(out_path: Path, *, samples: int = 32, pack_dir: Path | None = None) -> Path:
    """Write current scene to .blend so owner can open in Blender Desktop."""
    ctx = build_scene(samples=samples, pack_dir=pack_dir)
    if pack_dir:
        ctx["pack_dir"] = pack_dir
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_path))
    print(f"Saved blend {out_path}")
    return out_path


def render_preview(out_png: Path, *, samples: int = 32, phase: str = "wave", pack_dir: Path | None = None) -> None:
    ctx = build_scene(samples=samples, pack_dir=pack_dir)
    if pack_dir:
        ctx["pack_dir"] = pack_dir
    scene = ctx["scene"]
    cam = ctx["camera"]
    form2 = ctx["form2"]
    armature = ctx.get("armature")
    f1 = 48
    if ctx.get("scene_only") or form2 is None:
        _animate_scene_camera(cam, frame_start=1, frame_end=f1, phase=phase)
        peak = 1 + int((f1 - 1) * 0.45)
    else:
        _animate_camera_wave_lunge(
            cam, form2, frame_start=1, frame_end=f1, phase=phase, armature=armature,
            pack_dir=ctx.get("pack_dir"),
        )
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
        "--save-blend",
        action="store_true",
        help="Save peripheral_draft_N.blend for owner (Blender Desktop)",
    )
    parser.add_argument(
        "--phase",
        choices=("open", "wave", "lunge"),
        default="wave",
        help="Animation phase for preview or single-clip test",
    )
    parser.add_argument(
        "--micro-jumpscare",
        action="store_true",
        help="Single 3s lunge clip with creature (volume-sting format)",
    )
    parser.add_argument(
        "--scene-only",
        action="store_true",
        help="Environment craft — no creature (default unless BLENDER_INCLUDE_CREATURE=1)",
    )
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--seconds", type=float, default=None, help="Clip length (default from env)")
    parser.add_argument("--samples", type=int, default=None, help="EEVEE TAA samples")
    args, _ = parser.parse_known_args(argv)

    seconds = args.seconds or float(os.environ.get("BLENDER_CLIP_SECONDS", "10"))
    samples = args.samples or int(os.environ.get("BLENDER_SAMPLES", "32"))
    if args.scene_only:
        os.environ["BLENDER_INCLUDE_CREATURE"] = "0"

    pack = args.pack_dir or OUTPUT_ROOT / f"draft_{args.draft_id}"
    if args.save_blend:
        save_scene_blend(
            pack / f"peripheral_draft_{args.draft_id}.blend",
            samples=samples,
            pack_dir=pack,
        )
        return
    if args.preview:
        render_preview(
            pack / f"blender_preview_{args.phase}.png",
            samples=samples,
            phase=args.phase,
            pack_dir=pack,
        )
        return
    if args.micro_jumpscare:
        render_micro_jumpscare(args.draft_id, pack, seconds=seconds, samples=samples)
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
