import datetime
import time
import requests
import cv2

# Initialize the camera
cap = cv2.VideoCapture(0)

# Set the resolution to the highest possible
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Your TBA API key
api_key = 'llLEkuNohw1CnhnVMWzJQnzq4fvBud65xCqtEsSBt5RqtwUGMFySJeoqS2YhsTI1 '


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


def sort_matches(matches) -> list:
    # Define the order of competition levels
    comp_level_order = {'qm': 1, 'sf': 2, 'f': 3}

    # Sort the matches by competition level
    sorted_matches = sorted(matches, key=lambda match: comp_level_order.get(match['comp_level'], 0))

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


def sort_all_matches(matches: list) -> list:
    # get qm, sf, f matches by time from the morning to the evening
    sorted = []
    for match in matches:
        if match['comp_level'] == 'qm':
            sorted.append(match.sort(key=lambda x: x['time']))
        if match['comp_level'] == 'sf':
            sorted.append(match.sort(key=lambda x: x['time']))
        if match['comp_level'] == 'f':
            sorted.append(match.sort(key=lambda x: x['time']))

    return sorted


def main():
    team_key = 'frc' + input("Enter your team number: ")
    events = get_events(team_key, 2023)

    print("Select a competition:")
    for i, event in enumerate(events):
        print(f"{i + 1}. {event['name']}")
    event_index = int(input("Enter the number of your selected competition: ")) - 1
    event_key = events[event_index]['key']

    matches = get_matches(team_key, event_key)
    time_sorted = sort_all_matches(matches)

    for match in time_sorted:
        print(f"Competition Level: {match['comp_level']}, Match Number: {match['match_number']}, "
              f"Time: {datetime.datetime.fromtimestamp(match['time']).strftime('%I:%M %p')}")

    # while True:
    #     current_time = time.time()
    #     for match in matches:
    #         if match['comp_level'] == 'qm' and match['time'] <= current_time <= match['time'] + 120:
    #             record_match()


if __name__ == "__main__":
    main()
