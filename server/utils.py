import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch

CLASSES = [
    "__background__",
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "street sign",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "hat",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "shoe",
    "eye glasses",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "plate",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    "mirror",
    "dining table",
    "window",
    "desk",
    "toilet",
    "door",
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "blender",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]

def prepare_image(image):
    image = image.convert("RGB")
    image_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1) / 255
    image_tensor = image_tensor.unsqueeze(0)
    return image_tensor

def draw_boxes(image, predictions, threshold=0.5):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for i, box in enumerate(predictions[0]['boxes']):
        score = predictions[0]['scores'][i].item()
        if score < threshold:
            continue

        label_idx = int(predictions[0]['labels'][i])
        label = CLASSES[label_idx]
        box = box.cpu().numpy().astype(int)

        draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="red", width=3)
        text = f"{label}: {score * 100:.1f}%"
        text_size = font.getbbox(text)
        text_position = (box[0], box[1] - text_size[3])

        draw.rectangle(
            [text_position, (text_position[0] + text_size[2], text_position[1] + text_size[3])],
            fill="red"
        )
        draw.text(text_position, text, fill="white", font=font)

    return image
