from flask import Flask, request, send_file, jsonify
from PIL import Image
from io import BytesIO
import torch
import base64
import uuid

from model import model, device
from utils import prepare_image, draw_boxes

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

detection_history = []


@app.route("/detect", methods=["POST"])
def detect():
    file = request.files["image"]
    image = Image.open(file.stream)

    tensor = prepare_image(image).to(device)

    with torch.no_grad():
        predictions = model(tensor)

    image_with_boxes = draw_boxes(image, predictions)

    orig_buf = BytesIO()
    image.save(orig_buf, format="JPEG")
    orig_bytes = orig_buf.getvalue()

    result_buf = BytesIO()
    image_with_boxes.save(result_buf, format="JPEG")
    result_bytes = result_buf.getvalue()

    detection_id = str(uuid.uuid4())

    detection_history.append({
        "id": detection_id,
        "original_image": orig_bytes,
        "result_image": result_bytes,
    })

    buf = BytesIO(result_bytes)
    buf.seek(0)
    response = send_file(buf, mimetype='image/jpeg')
    response.headers["X-Detection-ID"] = detection_id
    return response


@app.route("/history", methods=["GET"])
def history():
    previews = []
    for item in detection_history:
        image = Image.open(BytesIO(item["result_image"]))
        image.thumbnail((100, 100))
        thumb_buf = BytesIO()
        image.save(thumb_buf, format="JPEG")
        b64_thumb = base64.b64encode(thumb_buf.getvalue()).decode("utf-8")
        previews.append({"id": item["id"], "thumbnail": b64_thumb})
    return jsonify(previews)


@app.route("/history/<detection_id>", methods=["GET"])
def get_detection(detection_id):
    item = next((x for x in detection_history if x["id"] == detection_id), None)
    if not item:
        return jsonify({"error": "Detection not found"}), 404

    buf = BytesIO(item["result_image"])
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(debug=True)
