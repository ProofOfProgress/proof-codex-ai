"""Build Peripheral Form 2 gas-station scene in Blender (bpy).

Run headless:
  blender --background --python shorts_bot/production/blender/build_and_render.py -- \\
      --draft-id 2 --preview
"""

from __future__ import annotations

import argparse
import json
import math
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


def _add_gas_station() -> bpy.types.Object:
    mats = {
        "pump": _mat("Pump", (0.12, 0.12, 0.14, 1.0)),
        "canopy": _mat("Canopy", (0.08, 0.08, 0.1, 1.0)),
    }
    for i, x in enumerate((-3.5, 3.5)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -8, 1.2))
        pump = bpy.context.active_object
        pump.name = f"Pump_{i}"
        pump.scale = (0.6, 0.5, 2.4)
        pump.data.materials.append(mats["pump"])
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
    lamp.data.energy = 800
    lamp.data.color = (1.0, 0.55, 0.2)
    lamp.parent = pole_empty
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
    bg.inputs[0].default_value = (0.008, 0.012, 0.02, 1.0)
    bg.inputs[1].default_value = 0.15


def _flicker_keyframes(lamp_data: bpy.types.Light, frame_start: int, frame_end: int) -> None:
    """Streetlight strobes — keyframes avoid headless driver restrictions."""
    prev = -1.0
    for f in range(frame_start, frame_end + 1):
        if int(f / 6) % 2 == 0:
            energy = 800.0
        elif int(f / 3) % 5 == 0:
            energy = 80.0
        else:
            energy = 20.0
        if energy != prev:
            lamp_data.energy = energy
            lamp_data.keyframe_insert(data_path="energy", frame=f)
            prev = energy


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
            vol.inputs["Density"].default_value = 0.025
            vol.inputs["Anisotropy"].default_value = 0.2
            links.new(vol.outputs["Volume"], output.inputs["Volume"])


def _animate_camera_wave_lunge(
    cam: bpy.types.Object,
    form2: bpy.types.Object,
    *,
    frame_start: int,
    frame_end: int,
    phase: str,
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
        cam.location = (1.5, -4, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_start)
        cam.location = (0.5, -7, 1.65)
        cam.keyframe_insert(data_path="location", frame=frame_end)
        form2.location = (0, -9, 0)
        form2.keyframe_insert(data_path="location", frame=frame_start)
        # creepy wave — rotate arm proxy via rig Z
        form2.rotation_euler = (0, 0, 0)
        form2.keyframe_insert(data_path="rotation_euler", frame=frame_start + 6)
        form2.rotation_euler = (0, 0, math.radians(8))
        form2.keyframe_insert(data_path="rotation_euler", frame=frame_end - 8)
        form2.location = (0, -7.5, 0)
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


def build_scene(*, samples: int = 32) -> dict:
    _clear_scene()
    scene = bpy.context.scene
    _add_ground_and_road()
    _add_gas_station()
    pole_empty, lamp = _add_streetlight()
    form2 = _build_form2()
    cam = _setup_camera()
    _setup_render(scene, samples=samples)
    _add_fog_and_trees()
    return {"scene": scene, "camera": cam, "form2": form2, "lamp": lamp}


def render_clip(
    out_path: Path,
    *,
    phase: str,
    seconds: float = 10.0,
    frame_offset: int = 0,
    samples: int = 32,
) -> None:
    ctx = build_scene(samples=samples)
    scene = ctx["scene"]
    cam = ctx["camera"]
    form2 = ctx["form2"]
    lamp = ctx["lamp"]
    f0 = 1 + frame_offset
    f1 = f0 + int(seconds * FPS) - 1
    scene.frame_start = f0
    scene.frame_end = f1
    _flicker_keyframes(lamp, f0, f1)
    _animate_camera_wave_lunge(cam, form2, frame_start=f0, frame_end=f1, phase=phase)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_path.with_suffix(""))
    bpy.ops.render.render(animation=True)
    if not out_path.exists():
        matches = sorted(out_path.parent.glob(f"{out_path.stem}*.mp4"))
        if matches:
            matches[-1].replace(out_path)
    print(f"Rendered {out_path}")


def render_preview(out_png: Path, *, samples: int = 32) -> None:
    ctx = build_scene(samples=samples)
    scene = ctx["scene"]
    cam = ctx["camera"]
    form2 = ctx["form2"]
    _animate_camera_wave_lunge(cam, form2, frame_start=1, frame_end=48, phase="lunge")
    scene.frame_set(40)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(out_png)
    bpy.ops.render.render(write_still=True)
    print(f"Preview {out_png}")


def render_draft_short(draft_id: int, pack_dir: Path, *, seconds: float = 10.0, samples: int = 32) -> list[Path]:
    clips_dir = pack_dir / "clips"
    phases = ("open", "wave", "lunge")
    paths: list[Path] = []
    offset = 0
    for i, phase in enumerate(phases, start=1):
        dest = clips_dir / f"blender_part_{i:02d}.mp4"
        render_clip(dest, phase=phase, seconds=seconds, frame_offset=offset, samples=samples)
        paths.append(dest)
        offset += int(seconds * FPS)
    spec = {"backend": "blender", "clips": [p.name for p in paths], "draft_id": draft_id}
    (clips_dir / "blender_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return paths


def main(argv: list[str] | None = None) -> None:
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--seconds", type=float, default=None, help="Clip length (default from env)")
    parser.add_argument("--samples", type=int, default=None, help="EEVEE TAA samples")
    args, _ = parser.parse_known_args(argv)

    seconds = args.seconds or float(os.environ.get("BLENDER_CLIP_SECONDS", "10"))
    samples = args.samples or int(os.environ.get("BLENDER_SAMPLES", "32"))

    pack = args.pack_dir or OUTPUT_ROOT / f"draft_{args.draft_id}"
    if args.preview:
        render_preview(pack / "blender_preview.png", samples=samples)
        return
    render_draft_short(args.draft_id, pack, seconds=seconds, samples=samples)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:])
