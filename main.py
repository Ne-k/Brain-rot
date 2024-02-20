from datetime import datetime
import tkinter as tk
from tkinter import ttk
import cv2
import time
import requests

# Initialize the camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Your TBA API key (remember to keep this secure)
api_key = 'llLEkuNohw1CnhnVMWzJQnzq4fvBud65xCqtEsSBt5RqtwUGMFySJeoqS2YhsTI1'


def get_events(team_key, year) -> list:
    # Use the TBA API to get the team's events for the year
    response = requests.get(
        f'https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}',
        headers={'X-TBA-Auth-Key': api_key}
    )
    events = response.json()
    return events


def get_matches(team_key, event_key) -> list:
    # Use the TBA API to get the team's matches at the event
    response = requests.get(
        f'https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches',
        headers={'X-TBA-Auth-Key': api_key}
    )
    all_matches = response.json()

    team_matches = [match for match in all_matches if
                    team_key in (match['alliances']['blue']['team_keys'] + match['alliances']['red']['team_keys'])]
    return team_matches


def sort_all_matches(matches) -> list:
    # Sort matches by both time and match number
    sorted_matches = sorted(matches, key=lambda match: (match['time'], match['match_number']))
    return sorted_matches


def record_match() -> None:
    # Start recording
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    start_time = time.time()
    while time.time() - start_time < 120:  # Record for 2 minutes
        ret, frame = cap.read()
        if ret:
            out.write(frame)

    # Release everything after recording
    out.release()


def start_recording():
    # Get the current time
    current_time = datetime.now()

    # Retrieve the scheduled match time (you can customize this based on your event data)
    scheduled_match_time = datetime(year=2024, month=2, day=20, hour=14, minute=30)

    # Calculate the time difference in seconds
    time_difference = (scheduled_match_time - current_time).total_seconds()

    # Wait until the scheduled match time (unless overridden)
    if time_difference > 0:
        print(f"Waiting for {time_difference:.2f} seconds until the scheduled match time...")
        time.sleep(time_difference)

    # Start recording
    record_match()


def override_recording():
    # Start recording immediately
    record_match()


def main():
    root = tk.Tk()
    root.title("Robotics Event Recorder")

    # Create input field for team number
    team_label = tk.Label(root, text="Enter your team number:")
    team_label.pack()
    team_entry = tk.Entry(root)
    team_entry.pack()

    # Create button to select event
    select_button = tk.Button(root, text="Select Event", command=start_recording)
    select_button.pack()

    # Create button to override and record now
    override_button = tk.Button(root, text="Override and Record Now", command=override_recording)
    override_button.pack()

    root.mainloop()



if __name__ == "__main__":
    main()
