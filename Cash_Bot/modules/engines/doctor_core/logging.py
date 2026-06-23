import time


def log_doctor(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[Doctor {ts}] {msg}")
