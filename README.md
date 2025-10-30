# Chicken Counter - Home Assistant Custom Integration

A Home Assistant custom integration that uses YOLOv12 to count chickens from camera snapshots.

## Features

- 🐔 Count chickens using YOLOv12 object detection
- 📷 Works with any Home Assistant camera entity
- 🎯 On-demand detection via service call
- 📊 Sensor entity showing chicken count
- 🖼️ Camera entity displaying annotated images with bounding boxes
- 🔔 Fires events for automation triggers

## Installation

### 1. Copy Files

Copy the `chicken_counter` folder to your Home Assistant `custom_components` directory:

```
custom_components/
└── chicken_counter/
    ├── __init__.py
    ├── camera.py
    ├── config_flow.py
    ├── const.py
    ├── coordinator.py
    ├── manifest.json
    ├── sensor.py
    └── services.yaml
```

### 2. Prepare Your YOLO Model (ONNX Format)

**Important**: This integration uses ONNX format (not PyTorch .pt files) for Python 3.13 compatibility.

**Step 1: Train or download a YOLO model**
```python
from ultralytics import YOLO

# Option A: Start with a pretrained model
model = YOLO('yolov8n.pt')

# Option B: Train on your chicken dataset
# model.train(data='chickens.yaml', epochs=100)
```

**Step 2: Export to ONNX format**
```python
# Export the model to ONNX
model.export(format='onnx')
# This creates: yolov8n.onnx
```

**Step 3: Copy to Home Assistant**
Place your ONNX model file somewhere accessible to Home Assistant:
```
/config/models/chicken_detector.onnx
```

**Quick Start - Use a Pre-trained Model:**
```bash
# Download YOLOv8 nano model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Convert to ONNX (requires ultralytics on your computer, not in HA)
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='onnx')"

# Copy to Home Assistant
cp yolov8n.onnx /path/to/homeassistant/config/models/
```

### 3. Restart Home Assistant

Restart Home Assistant to load the custom integration.

### 4. Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Chicken Counter"
4. Enter configuration:
   - **Model Path**: Full path to your YOLO model (e.g., `/config/models/chicken_detector.pt`)
   - **Confidence Threshold**: 0.5 (adjust based on your needs)
   - **Device**: cpu (or cuda if you have GPU support)

## Usage

### Service Call

Call the `chicken_counter.count_chickens` service to detect chickens:

```yaml
service: chicken_counter.count_chickens
data:
  camera_entity: camera.chicken_coop
```

### Entities Created

After detection runs, you'll have:

1. **Sensor**: `sensor.chicken_count`
   - Shows the number of chickens detected
   - Attributes include last detection time

2. **Camera**: `camera.chicken_detection_camera`
   - Displays the annotated image with bounding boxes
   - Shows the last detection result

### Automation Example

Trigger notifications when chicken count changes:

```yaml
automation:
  - alias: "Notify on Chicken Count"
    trigger:
      - platform: event
        event_type: chicken_counter_detection_complete
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Chicken Count Update"
          message: "Detected {{ trigger.event.data.count }} chickens"
          data:
            image: "/api/camera_proxy/camera.chicken_detection_camera"
```

### Lovelace Card Example

Display the count and image:

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: sensor.chicken_count
    name: Chickens in Coop
  - type: picture-entity
    entity: camera.chicken_detection_camera
    show_state: false
    show_name: false
  - type: button
    tap_action:
      action: call-service
      service: chicken_counter.count_chickens
      service_data:
        camera_entity: camera.chicken_coop
    name: Count Chickens Now
```

## Advanced Usage

### Scheduled Detection

Run detection every 5 minutes:

```yaml
automation:
  - alias: "Periodic Chicken Count"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    action:
      - service: chicken_counter.count_chickens
        data:
          camera_entity: camera.chicken_coop
```

### Alert on Count Change

Get notified when chickens leave or enter:

```yaml
automation:
  - alias: "Alert on Chicken Count Change"
    trigger:
      - platform: state
        entity_id: sensor.chicken_count
    condition:
      - condition: template
        value_template: "{{ trigger.from_state.state != 'unavailable' }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Chicken Count Changed"
          message: >
            Count changed from {{ trigger.from_state.state }} to {{ trigger.to_state.state }}
```

## Performance Considerations

- **CPU Only**: Detection may take 2-10 seconds per image on Raspberry Pi
- **Model Size**: Smaller models (yolov8n) are faster but less accurate
- **Image Resolution**: Lower resolution cameras process faster
- **Frequency**: Avoid running detection more than once per minute on low-powered devices

## Troubleshooting

### Model Not Loading
- Verify the model path is correct and accessible
- Check Home Assistant logs for error messages
- Ensure the model file is a valid YOLO format (.pt file)

### Poor Detection Accuracy
- Adjust the confidence threshold (lower = more detections, more false positives)
- Retrain your model with more chicken images
- Ensure good lighting in your camera view

### Slow Performance
- Use a smaller YOLO model (yolov8n instead of yolov8x)
- Reduce camera resolution
- Limit detection frequency

## Events

The integration fires `chicken_counter_detection_complete` events with:
- `count`: Number of chickens detected
- `camera_entity`: Camera entity used
- `timestamp`: When detection completed

Use these events to trigger automations!

## Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.11+
- Sufficient storage for YOLO model (~6-50MB depending on model size)

## License

MIT License - Feel free to modify and share!
