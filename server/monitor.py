import cv2
from ultralytics import solutions
import threading
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("URL"), os.getenv("KEY"))


def reset(self):
    self.classwise_counts = {}


solutions.ObjectCounter.reset = reset


class Monitor:
    def __init__(self, intersection_id, direction, T):
        self.intersection_id = intersection_id
        self.direction = direction  # 1 or 2
        self.T = T
        self.is_active = False

    def get_is_active(self):
        return self.is_active

    def start(self):
        self.is_active = True
        video_path = ".assets/test1.mp4" if self.direction == 1 else ".assets/test2.mp4"
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.count_specific_classes(
            video_path,
            "output_specific_classes.avi",
            "yolo11n.pt",
            [2, 3, 5, 7],
        )

    def count_specific_classes(
        self, video_path, output_video_path, model_path, classes_to_count
    ):
        cap = cv2.VideoCapture(video_path)
        assert cap.isOpened(), "Error reading video file"
        w, h, fps = (
            int(cap.get(x))
            for x in (
                cv2.CAP_PROP_FRAME_WIDTH,
                cv2.CAP_PROP_FRAME_HEIGHT,
                cv2.CAP_PROP_FPS,
            )
        )
        video_writer = cv2.VideoWriter(
            output_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
        )
        FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        line_points = [
            (0, FRAME_HEIGHT - 200),
            (FRAME_WIDTH, FRAME_HEIGHT - 200),
            (FRAME_WIDTH, FRAME_HEIGHT - 100),
            (0, FRAME_HEIGHT - 100),
        ]
        counter = solutions.ObjectCounter(
            show=True, region=line_points, model=model_path, classes=classes_to_count
        )

        def update():
            if not self.is_active:
                supabase.table("intersection").upsert(
                    {"id": self.intersection_id, "traffic1": 0, "traffic2": 0}
                ).execute()

                return

            traffic = 0

            if "car" in counter.classwise_counts:
                traffic += counter.classwise_counts["car"]["IN"] * 2

            if "motorcycle" in counter.classwise_counts:
                traffic += counter.classwise_counts["motorcycle"]["IN"] * 1

            if "bus" in counter.classwise_counts:
                traffic += counter.classwise_counts["bus"]["IN"] * 30

            if "truck" in counter.classwise_counts:
                traffic += counter.classwise_counts["truck"]["IN"] * 1

            traffic /= self.T
            print("[TRAFFIC]", traffic)

            if self.direction == 1:
                supabase.table("intersection").upsert(
                    {"id": self.intersection_id, "traffic1": traffic}
                ).execute()
            else:
                supabase.table("intersection").upsert(
                    {"id": self.intersection_id, "traffic2": traffic}
                ).execute()

            counter.reset()
            threading.Timer(self.T, update).start()

        threading.Timer(self.T, update).start()  # update every self.T seconds

        while cap.isOpened():
            success, im0 = cap.read()

            if not success:
                print(
                    "Video frame is empty or video processing has been successfully completed."
                )
                break

            im0 = counter.count(im0)
            video_writer.write(im0)

        cap.release()
        video_writer.release()
        cv2.destroyAllWindows()
        self.is_active = False