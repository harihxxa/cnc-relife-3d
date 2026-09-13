from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

import os
import uuid

from depth import create_depth_map
from relief import create_relief
from stl import export_stl


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )


@app.route("/<path:filename>")
def static_files(filename):

    return send_from_directory(
        ".",
        filename
    )


@app.route(
    "/generate",
    methods=["POST"]
)
def generate():

    try:

        if "image" not in request.files:

            raise ValueError(
                "No image uploaded."
            )


        image = request.files["image"]


        width = float(
            request.form.get(
                "width",
                300
            )
        )

        height = float(
            request.form.get(
                "height",
                200
            )
        )

        max_depth = float(
            request.form.get(
                "depth",
                10
            )
        )

        base = float(
            request.form.get(
                "base",
                5
            )
        )

        detail = request.form.get(
            "detail",
            "medium"
        )

        background = request.form.get(
            "background",
            "keep"
        )


        file_id = uuid.uuid4().hex

        input_path = os.path.join(
            UPLOAD_FOLDER,
            file_id + ".png"
        )

        output_path = os.path.join(
            OUTPUT_FOLDER,
            file_id + ".stl"
        )


        image.save(input_path)


        # Image → AI Depth Map

        depth_map = create_depth_map(
            input_path
        )


        # Depth Map → 3D Relief

        mesh = create_relief(
            depth_map,
            width,
            height,
            max_depth,
            base,
            detail=detail,
            background=background
        )


        # 3D Relief → STL

        export_stl(
            mesh,
            output_path
        )


        return jsonify({

            "success": True,

            "download_url":
                "/download/" +
                file_id +
                ".stl"

        })


    except Exception as error:

        print(
            "ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


@app.route(
    "/download/<filename>"
)
def download(filename):

    return send_from_directory(
        OUTPUT_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
