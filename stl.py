import numpy as np
import trimesh


def export_stl(mesh, output_path):

    if mesh is None:
        raise ValueError("Mesh generation failed.")

    if len(mesh.faces) == 0:
        raise ValueError("Mesh has no faces.")

    # -------------------------
    # Remove duplicate faces
    # -------------------------

    faces = np.asarray(mesh.faces)

    sorted_faces = np.sort(
        faces,
        axis=1
    )

    _, unique_indices = np.unique(
        sorted_faces,
        axis=0,
        return_index=True
    )

    unique_indices = np.sort(
        unique_indices
    )

    mesh.update_faces(unique_indices)

    # -------------------------
    # Remove degenerate faces
    # -------------------------

    faces = np.asarray(mesh.faces)

    valid = (
        (faces[:, 0] != faces[:, 1]) &
        (faces[:, 1] != faces[:, 2]) &
        (faces[:, 0] != faces[:, 2])
    )

    mesh.update_faces(valid)

    # -------------------------
    # Clean vertices
    # -------------------------

    mesh.merge_vertices()

    mesh.remove_unreferenced_vertices()

    # -------------------------
    # Fix normals
    # -------------------------

    mesh.fix_normals()

    # -------------------------
    # Check mesh
    # -------------------------

    if len(mesh.faces) == 0:
        raise ValueError("Mesh has no valid triangles.")

    if not mesh.is_watertight:
        raise ValueError(
            "Generated mesh is not watertight."
        )

    # -------------------------
    # Export STL
    # -------------------------

    mesh.export(
        output_path,
        file_type="stl"
    )

    return output_path