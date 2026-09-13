import cv2
import numpy as np
import torch

from transformers import (
    AutoImageProcessor,
    AutoModelForDepthEstimation
)


MODEL_NAME = (
    "depth-anything/"
    "Depth-Anything-V2-Small-hf"
)


_processor = None
_model = None


def load_model():

    global _processor
    global _model

    if _model is None:

        _processor = (
            AutoImageProcessor.from_pretrained(
                MODEL_NAME
            )
        )

        _model = (
            AutoModelForDepthEstimation
            .from_pretrained(
                MODEL_NAME
            )
        )

        _model.eval()


def create_depth_map(image_path):

    load_model()

    image = cv2.imread(
        image_path
    )

    if image is None:

        raise ValueError(
            "Could not read image."
        )

    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    inputs = _processor(
        images=image_rgb,
        return_tensors="pt"
    )

    with torch.no_grad():

        outputs = _model(
            **inputs
        )

    predicted_depth = (
        outputs.predicted_depth
    )

    depth = (
        torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=image_rgb.shape[:2],
            mode="bicubic",
            align_corners=False
        )
        .squeeze()
        .cpu()
        .numpy()
    )

    # --------------------------------
    # Depth normalization
    # --------------------------------

    depth = depth.astype(np.float32)

    min_depth = np.percentile(
        depth,
        2
    )

    max_depth = np.percentile(
        depth,
        98
    )

    depth = np.clip(
        depth,
        min_depth,
        max_depth
    )

    depth = (
        (depth - min_depth)
        /
        (max_depth - min_depth + 1e-6)
    )

    # --------------------------------
    # Depth contrast / strength
    # --------------------------------

    depth = np.power(
        depth,
        0.75
    )

    # Convert to 0-255
    depth = (
        depth * 255.0
    )

    # --------------------------------
    # Smooth tiny noise
    # --------------------------------

    depth = cv2.GaussianBlur(
        depth.astype(np.float32),
        (3, 3),
        0
    )

    return depth