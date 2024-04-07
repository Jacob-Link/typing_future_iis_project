import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from google.protobuf.json_format import MessageToDict
from mediapipe.python.solutions import drawing_utils


# pip install numpy pyautogui opencv-python mediapipe==0.10.9

def calc_dist_thumb_index(thumb, index_finger):
    thumb_np = np.array(thumb)
    index_np = np.array(index_finger)

    dist = np.linalg.norm(thumb_np - index_np)

    return dist


def calc_dist_two_landmark_points(point1, point2):
    p1 = np.array(point1)
    p2 = np.array(point2)
    dist = np.linalg.norm(p1 - p2)
    return dist


def calc_left_hand_fist_dist(hand):
    hand_coordinates = hand.landmark
    point_couples_indexes_to_calc_dist = [(4, 6), (8, 2), (12, 1), (16, 0)]

    point_couples_to_calc_dist = []
    for p1_index, p2_index in point_couples_indexes_to_calc_dist:
        p1 = (hand_coordinates[p1_index].x, hand_coordinates[p1_index].y)
        p2 = (hand_coordinates[p2_index].x, hand_coordinates[p2_index].y)
        point_couples_to_calc_dist.append((p1, p2))

    dists_list = [calc_dist_two_landmark_points(p1, p2) for p1, p2 in point_couples_to_calc_dist]
    sum_dist = sum(dists_list)
    # print(f">>> sum of dists chosen: {round(sum_dist, 4)}")
    return sum_dist


def scale_positions(x, y, x_scale=4.0, y_scale=2.0):
    # used to move mouse to all parts of screen from the center without needing to make extreme physical movements
    x_scaled = x_scale * (x - 0.5) + 0.5
    y_scaled = y_scale * (y - 0.5) + 0.5

    x_final = min(x_scaled, 1)
    y_final = min(y_scaled, 1)

    return x_final, y_final


def run_apple_vision_controller(right_handed: bool,
                                scale_x: float,
                                scale_y: float,
                                click_threshold: float,
                                release_click_lock_threshold: float):
    cam = cv2.VideoCapture(0)
    hand_detector = mp.solutions.hands.Hands()
    screen_w, screen_h = pyautogui.size()

    limit_to_one_click_flag = True
    count_clicks = 1
    while True:
        _, frame = cam.read()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hand_process = hand_detector.process(rgb_frame)
        hands_landmarks_points = hand_process.multi_hand_landmarks
        hand_right_left = hand_process.multi_handedness

        frame_h, frame_w, _ = frame.shape

        if hands_landmarks_points:
            # right hand used for mouse movement and left for clicking.

            points = hands_landmarks_points
            labels = [MessageToDict(i)['classification'][0]['label'] for i in hand_right_left]

            for index, hand in enumerate(points):  # we only want 1 hand to have the power
                # drawing_utils.draw_landmarks(frame, hand)
                if right_handed:
                    move_mouse = "Left"  # Right, mirror
                    click_mouse = "Right"  # Left, mirror
                else:
                    move_mouse = "Right"  # Right, mirror
                    click_mouse = "Left"  # Left, mirror

                if labels[index] == click_mouse:  # this is the left hand, due to mirror effect
                    landmarks = hand.landmark
                    for id, landmark in enumerate(landmarks):
                        if id == 8:
                            x = int(landmark.x * frame_w)
                            y = int(landmark.y * frame_h)

                            cv2.circle(img=frame, center=(x, y), radius=9, color=(0, 255, 0), thickness=-1)

                            index_x = x / frame_w
                            index_y = y / frame_h

                        if id == 4:
                            x = int(landmark.x * frame_w)
                            y = int(landmark.y * frame_h)

                            cv2.circle(img=frame, center=(x, y), radius=9, color=(0, 255, 0), thickness=-1)

                            thumb_x = x / frame_w
                            thumb_y = y / frame_h

                    thumb = (thumb_x, thumb_y)
                    index_finger = (index_x, index_y)

                    line_color = (255, 0, 0)
                    if not limit_to_one_click_flag:
                        line_color = (0, 0, 255)

                    cv2.line(frame,
                             (int(thumb[0] * frame_w), int(thumb[1] * frame_h)),
                             (int(index_finger[0] * frame_w), int(index_finger[1] * frame_h)),
                             line_color, 2)

                    dist = calc_dist_thumb_index(thumb, index_finger)

                    if dist < click_threshold and limit_to_one_click_flag:
                        print(f'>>> (CLICK {count_clicks:,}!) dist between fingers: {round(dist, 3)}')
                        count_clicks += 1
                        pyautogui.click()
                        # pyautogui.sleep(1)
                        limit_to_one_click_flag = False
                    elif (limit_to_one_click_flag is False) and (dist > release_click_lock_threshold):
                        print("--- Released lock on click")
                        limit_to_one_click_flag = True

                elif labels[index] == move_mouse:  # this is the right hand due to mirror effect
                    # follow the index finger to move the mouse
                    index_landmarks = hand.landmark[8]

                    x = int(index_landmarks.x * frame_w)
                    y = int(index_landmarks.y * frame_h)

                    cv2.circle(img=frame, center=(x, y), radius=4, color=(0, 0, 255), thickness=-1)
                    cv2.circle(img=frame, center=(x, y), radius=9, color=(255, 0, 0), thickness=2)

                    x_screen_landmark = x / frame_w
                    y_screen_landmark = y / frame_h

                    x_screen_landmark, y_screen_landmark = scale_positions(x=x_screen_landmark,
                                                                           y=y_screen_landmark,
                                                                           x_scale=scale_x,
                                                                           y_scale=scale_y)

                    screen_x = screen_w * (
                            1 - x_screen_landmark)  # mirror effect, we want  move right -> moves mouse right
                    screen_y = screen_h * y_screen_landmark

                    # pyautogui.moveTo(screen_x, screen_y)
                    pyautogui.moveTo(screen_x, screen_y, 0.1, pyautogui.easeInOutQuad)

        # print(f"{move_mouse_lock= }")

        frame = cv2.flip(frame, 1)
        cv2.imshow("APPLE VISION CONTROLLER", frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    # control the movement of the mouse with eyes and clicks with hand gesture
    run_apple_vision_controller(right_handed=True,
                                scale_x=2,
                                scale_y=1.5,
                                click_threshold=0.05,
                                release_click_lock_threshold=0.07)

# noteworthy in report:
# right index finger controls mouse movement
# left index and thumb controls mouse click
# right-handed and left-handed bool param
# small scale needed - therefore, the mouse movement is very stable and intuitive
