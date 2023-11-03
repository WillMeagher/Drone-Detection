from ultralytics import YOLO

OUTPUT_DIR = "/app/src/training/outputs/"
data_file = "/app/src/training/database.yaml"

model = YOLO(OUTPUT_DIR + 'yolov8s.pt')

# use cosine learning rate decay
results = model.train(
    data=data_file,
    epochs=20,
    augment=True,
    project=OUTPUT_DIR,
    translate=0.1,  # image translation (+/- fraction)
    scale=0.2,  # image scale (+/- gain)
    shear=0.2,  # image shear (+/- deg) from -0.5 to 0.5
    mixup=0.1,  # image mixup (probability)
    dropout=0.3,
)