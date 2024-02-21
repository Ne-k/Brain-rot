import time

import cv2
import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime
import win32com.client

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

def record_match(camera_index) -> None:
    # Initialize the camera
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

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
    cap.release()

def get_camera_names():
    wmi = win32com.client.GetObject ("winmgmts:")
    cameras = wmi.ExecQuery ("SELECT * FROM Win32_PnPEntity WHERE PNPClass='Camera' OR PNPClass='ImagingDevice' OR Name LIKE '%camera%' OR Name LIKE '%webcam%' OR Name LIKE '%imaging%'")

    camera_names = []
    for camera in cameras:
        camera_names.append(camera.Name)

    return camera_names

def main():
    year = 2023
    def submit_team_number():
        # Get the team number from the entry field and prepend 'frc'
        team_number[0] = 'frc' + team_entry.get()

        # Get the events for the team
        events = get_events(team_number[0], year)  # You need to define year

        # Update the combobox with the events
        event_combobox["values"] = [event['name'] for event in events]

    root = tk.Tk()
    root.title("Robotics Event Recorder")
    root.geometry("800x600")  # Set the size of the window

    # Create input field for team number
    team_label = tk.Label(root, text="Enter your team number:")
    team_label.pack()
    team_entry = tk.Entry(root)
    team_entry.pack()

    # Create button to submit team number
    submit_button = tk.Button(root, text="Submit", command=submit_team_number)
    submit_button.pack()

    # Create a label for the event combobox
    event_label = tk.Label(root, text="Select your event:")
    event_label.pack()

    # Create a combobox to display the events
    event_combobox = ttk.Combobox(root)
    event_combobox.pack()

    # Create a label for the camera combobox
    camera_label = tk.Label(root, text="Select your camera:")
    camera_label.pack()

    # Create a combobox to display the cameras
    camera_combobox = ttk.Combobox(root)
    camera_combobox.pack()

    # Create a text box to display the console output
    text_box = tk.Text(root)
    text_box.pack()

    # Define team_number as a list
    team_number = [None]

    # Update the combobox with the camera list
    camera_combobox["values"] = get_camera_names()

    def select_event(event):
        # Get the selected event
        selected_event = event_combobox.get()

        # Find the event key for the selected event
        events = get_events(team_number[0], year)  # You need to define year
        for event in events:
            if event['name'] == selected_event:
                event_key = event['key']
                break

        # Get the matches for the team at the selected event
        matches = get_matches(team_number[0], event_key)
        sorted_matches = sort_all_matches(matches)

        # Print the sorted matches to the console
        for match in sorted_matches:
            print(match)

    # Bind the combobox to the select_event function
    event_combobox.bind("<<ComboboxSelected>>", select_event)

    root.mainloop()

if __name__ == "__main__":
    main()
