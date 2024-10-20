import os
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("URL"), os.getenv("KEY"))

STATES = [["G", "R"], ["R", "R"], ["R", "G"], ["R", "R"]]
T = 10  # t1 + t2

class TrafficLights:
    def __init__(self, intersection_id):
        self.intersection_id = intersection_id
        self.stage = 0
        self.durations = [5, 1, 5, 1]  # GR RR RG RR
        self.is_active = False

    def start(self):
        # setup
        supabase.table("intersection").upsert(
            {
                "id": self.intersection_id,
                "traffic_light1": 'G',
                "traffic_light2": 'R',
            }
        ).execute()
        time.sleep(3)
        self.is_active = True

        while self.is_active:
            tmp = self.durations[:]

            for duration in tmp:
                time.sleep(duration)
                self.stage = (self.stage + 1) % 4
                self.update_lights()

                if self.stage == 3:
                    self.update_durations()

    def update_lights(self):
        supabase.table("intersection").upsert(
            {
                "id": self.intersection_id,
                "traffic_light1": STATES[self.stage][0],
                "traffic_light2": STATES[self.stage][1],
            }
        ).execute()

    def update_durations(self):
        res = (
            supabase.table("intersection")
            .select("*")
            .eq("id", self.intersection_id)
            .execute()
        )
        traffic1 = res.data[0]["traffic1"]
        traffic2 = res.data[0]["traffic2"]
        traffic1 = max(traffic1, 1)
        traffic2 = max(traffic2, 1)
        t1 = T * traffic1 / (traffic1 + traffic2)
        t2 = T - t1
        self.durations[0] = t1
        self.durations[2] = t2
        print("T1 & T2", t1, t2)
