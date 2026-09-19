import json
import sys

import bpy

out_path = sys.argv[sys.argv.index("--") + 1]
scene = bpy.context.scene
render = scene.render

def poly_count():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for inst in depsgraph.object_instances:
        obj = inst.object
        if obj.type != "MESH":
            continue
        try:
            mesh = obj.to_mesh()
        except RuntimeError:
            continue
        total += len(mesh.polygons)
        obj.to_mesh_clear()
    return total

def sample():
    if render.engine == "CYCLES":
        return scene.cycles.samples
    if render.engine.startwith("BLENDER_EEVEE"):
        return scene.eevee.taa_render_samples
    return None

def has_python_drivers():
    collections = [bpy.data.objects, bpy.data.meshes, bpy.data.materials,
                   bpy.data.armatures, bpy.data.shape_keys, bpy.data.scenes,
                   bpy.data.cameras, bpy.data.lights, bpy.data.worlds,
                   bpy.data.node_groups]
    ids = [idb for coll in collections for idb in coll]
    ids += [m.node_tree for m in bpy.data.materials if m.node_tree]
    for idb in ids:
        anim = getattr(idb, "animation_data", None)
        if not anim:
            continue
        for fcurve in anim.drivers:
            driver = fcurve.driver
            if driver.type == "SCRIPTED" and not driver.is_simple_expression:
                return True
    return False

def external_paths():
    found = []
    for img in bpy.data.images:
        if img.source in {"FILE", "SEQUENCE", "MOVIE"} and img.filepath and not img.packed_file:
            found.append({"type": "image", "name": img.name, "path": img.filepath})
    for lib in bpy.data.libraries:
        found.append({"type": "library", "name": lib.name, "path": lib.filepath})
    for cache in bpy.data.cache_files:
        found.append({"type": "cache", "name": cache.name, "path": cache.filepath})
    for volume in bpy.data.volumes:
        if volume.filepath and not volume.packed_file:
            found.append({"type": "volume", "name": volume.name, "path": volume.filepath})
    return found