
from gradio_client import Client, handle_file
from ultralytics import YOLO
import cv2


def directYOLO(name):
    # Load a pre-trained YOLOv10 model
    model = YOLO("yolov10n.pt")  # Use any YOLOv10 model, e.g., yolov10n.pt, yolov10s.pt

    # Load an image
    image_path = name
    image = cv2.imread(image_path)

    # Run inference on the image
    # You can pass the image path or the OpenCV image array
    # The `save=False` argument prevents the library from saving the annotated image file.
    # The `stream=False` argument ensures a list of Results objects is returned, not a generator.
    results = model.predict(source=image, save=False, stream=False, save_crop=True)

    # Process the first result (assuming you have one image)
    result = results[0]

    # Extract the bounding box information
    boxes = result.boxes.xyxy.tolist()  # Get the coordinates as a list of lists [x1, y1, x2, y2]
    scores = result.boxes.conf.tolist()  # Get the confidence scores
    class_ids = result.boxes.cls.tolist()  # Get the class IDs
    class_names = result.names  # Get the class names mapping from the model

    # Construct the output dictionary
    # You can use a list of dictionaries for a more structured output
    detections_list = []
    for box, score, class_id in zip(boxes, scores, class_ids):
        detections_list.append({
            "box": [round(coord) for coord in box],  # Round coordinates to integers
            "score": round(score, 4),
            "class_id": int(class_id),
            "class_name": class_names[int(class_id)]
        })

    # The final output is a Python dictionary
    output_dict = {
        "image_path": image_path,
        "detections": detections_list
    }

    # Print the final dictionary
    import json
    print(json.dumps(output_dict, indent=2))

def doit(name):
    # Use a breakpoint in the code line below to debug your script.
    client = Client("sanjanatanna/ObjectDetectionTool")
    result = client.predict(
        image=handle_file(name),
        api_name="/predict"
    )
#    print(result)

    client = Client("Roboflow/RF-DETR")
    result = client.predict(
        input_image=handle_file(filepath_or_url=name),
        confidence=0.5,
        resolution=896,
        checkpoint="segmentation preview",
        api_name="/image_processing_inference"
    )
    print(result)
def info():
    client = Client("sanjanatanna/ObjectDetectionTool")
    print(client.view_api())  # This shows all available endpoints and their parameters
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
#    info()
    directYOLO('/Users/wdawson/Downloads/The-Importance-of-Perches-for-Chickens.jpeg')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
