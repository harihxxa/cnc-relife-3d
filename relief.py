import numpy as np
import trimesh
import cv2


def create_relief(
    depth_map,
    width,
    height,
    max_depth,
    base_thickness,
    detail="medium",
    background="keep"
):

    depth = depth_map.copy()

    # -------------------------
    # Limit mesh resolution
    # -------------------------

    MAX_SIZE = 700

    rows, cols = depth.shape

    scale = min(
        MAX_SIZE / rows,
        MAX_SIZE / cols,
        1.0
    )

    if scale < 1.0:

        new_rows = max(
            2,
            int(rows * scale)
        )

        new_cols = max(
            2,
            int(cols * scale)
        )

        depth = cv2.resize(
            depth,
            (new_cols, new_rows),
            interpolation=cv2.INTER_AREA
        )

    # -------------------------
    # Detail control
    # -------------------------

    if detail == "smooth":

        depth = cv2.GaussianBlur(
            depth,
            (7, 7),
            0
        )

    elif detail == "medium":

        depth = cv2.GaussianBlur(
            depth,
            (3, 3),
            0
        )

    rows, cols = depth.shape

    # -------------------------
    # X / Y coordinates
    # -------------------------

    x_values = np.linspace(
        0,
        width,
        cols,
        dtype=np.float32
    )

    y_values = np.linspace(
        0,
        height,
        rows,
        dtype=np.float32
    )

    # -------------------------
    # Create top + bottom
    # -------------------------

    total_vertices = rows * cols * 2

    vertices = np.empty(
        (total_vertices, 3),
        dtype=np.float32
    )

    index = 0

    # -------------------------
    # Top relief surface
    # -------------------------

    for row in range(rows):

        for col in range(cols):

            vertices[index, 0] = x_values[col]
            vertices[index, 1] = y_values[row]

            vertices[index, 2] = (
                base_thickness
                +
                (
                    float(depth[row, col])
                    / 255.0
                    * max_depth
                )
            )

            index += 1

    # -------------------------
    # Base surface
    # -------------------------

    base_start = rows * cols

    for row in range(rows):

        for col in range(cols):

            vertices[index, 0] = x_values[col]
            vertices[index, 1] = y_values[row]
            vertices[index, 2] = 0

            index += 1

    # -------------------------
    # Faces
    # -------------------------

    faces = []

    # -------------------------
    # Relief surface
    # -------------------------

    for row in range(rows - 1):

        for col in range(cols - 1):

            a = row * cols + col
            b = a + 1
            c = (row + 1) * cols + col
            d = c + 1

            faces.append([a, b, c])
            faces.append([b, d, c])

    # -------------------------
    # Bottom
    # -------------------------

    for row in range(rows - 1):

        for col in range(cols - 1):

            a = base_start + row * cols + col
            b = a + 1
            c = base_start + (row + 1) * cols + col
            d = c + 1

            faces.append([a, c, b])
            faces.append([b, c, d])

    # -------------------------
    # Side walls
    # -------------------------

    # Front + Back

    for col in range(cols - 1):

        top_a = col
        top_b = col + 1

        bottom_a = base_start + col
        bottom_b = base_start + col + 1

        faces.append([
            top_a,
            bottom_a,
            top_b
        ])

        faces.append([
            top_b,
            bottom_a,
            bottom_b
        ])

        top_a = (
            (rows - 1) * cols
            + col
        )

        top_b = top_a + 1

        bottom_a = (
            base_start
            + (rows - 1) * cols
            + col
        )

        bottom_b = bottom_a + 1

        faces.append([
            top_a,
            top_b,
            bottom_a
        ])

        faces.append([
            top_b,
            bottom_b,
            bottom_a
        ])

    # Left + Right

    for row in range(rows - 1):

        top_a = row * cols
        top_b = (row + 1) * cols

        bottom_a = (
            base_start
            + row * cols
        )

        bottom_b = (
            base_start
            + (row + 1) * cols
        )

        faces.append([
            top_a,
            top_b,
            bottom_a
        ])

        faces.append([
            top_b,
            bottom_b,
            bottom_a
        ])

        top_a = (
            row * cols
            + cols - 1
        )

        top_b = (
            (row + 1) * cols
            + cols - 1
        )

        bottom_a = (
            base_start
            + row * cols
            + cols - 1
        )

        bottom_b = (
            base_start
            + (row + 1) * cols
            + cols - 1
        )

        faces.append([
            top_a,
            bottom_a,
            top_b
        ])

        faces.append([
            top_b,
            bottom_a,
            bottom_b
        ])

    # -------------------------
    # Convert faces
    # -------------------------

    faces = np.asarray(
        faces,
        dtype=np.int32
    )

    # -------------------------
    # Create mesh
    # -------------------------

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=True
    )

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

    mesh.update_faces(
        unique_indices
    )

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

    return mesh