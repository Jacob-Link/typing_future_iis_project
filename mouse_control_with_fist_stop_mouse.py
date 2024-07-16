import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from google.protobuf.json_format import MessageToDict
from mediapipe.python.solutions import drawing_utils


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


def calc_left_hand_fist_dist(hand, point_couples_indexes_to_calc_dist):
    hand_coordinates = hand.landmark

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


def plot_nose_points(face_landmark_points, frame, frame_w, frame_h):
    landmarks = face_landmark_points[0].landmark
    landmarks = [landmarks[1], landmarks[45], landmarks[5], landmarks[275]]  # relevant nose data

    nose_points = []
    for point in landmarks:
        x = int(point.x * frame_w)
        y = int(point.y * frame_h)

        cv2.circle(frame, (x, y), 3, (0, 255, 0))

        nose_points.append((x, y))

    return nose_points


def plot_nose_center(nose_points, frame):
    x_avg = int(sum([x[0] for x in nose_points]) / len(nose_points))
    y_avg = int(sum([x[1] for x in nose_points]) / len(nose_points))

    cv2.circle(frame, (x_avg, y_avg), 4, (255, 0, 0), -1)
    return x_avg, y_avg


def get_screen_xy_after_scale(x_screen_landmark_scaled: float,
                              y_screen_landmark_scaled: float,
                              screen_w: int,
                              screen_h: int):
    screen_x = screen_w * (1 - x_screen_landmark_scaled)  # due to mirror effect
    screen_y = screen_h * y_screen_landmark_scaled

    return screen_x, screen_y


def get_thumb_and_index_position(hand, frame, frame_w, frame_h):
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
    return thumb, index_finger


def plot_thumb_index_line(thumb, index_finger, frame, frame_w, frame_h, one_click_lock):
    line_color = (255, 0, 0)
    if one_click_lock:
        line_color = (0, 0, 255)  # red, cannot click

    cv2.line(frame,
             (int(thumb[0] * frame_w), int(thumb[1] * frame_h)),
             (int(index_finger[0] * frame_w), int(index_finger[1] * frame_h)),
             line_color, 2)


def plot_left_hand_relevant_lines(hand, point_couples_indexes_to_calc_dist, frame, frame_w, frame_h, move_mouse_lock):
    line_color = (255, 0, 0)
    if move_mouse_lock:
        line_color = (0, 0, 255)  # red

    # plot lines for vis purposes - red lines when the lock is active
    for p1_index, p2_index in point_couples_indexes_to_calc_dist:
        p1 = hand.landmark[p1_index]
        p2 = hand.landmark[p2_index]

        p1_plot = int(p1.x * frame_w), int(p1.y * frame_h)
        p2_plot = int(p2.x * frame_w), int(p2.y * frame_h)

        cv2.circle(img=frame, center=p1_plot, radius=9, color=(0, 255, 0), thickness=-1)
        cv2.circle(img=frame, center=p2_plot, radius=9, color=(0, 255, 0), thickness=-1)

        cv2.line(frame, p1_plot, p2_plot, line_color, 2)


def run_apple_vision_controller(scale_x_param: float,
                                scale_y_param: float,
                                click_threshold: float,
                                release_click_lock_threshold: float,
                                fist_palm_threshold: float):
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    hand_detector = mp.solutions.hands.Hands()
    screen_w, screen_h = pyautogui.size()  # monitor resolution

    move_mouse_lock = True
    one_click_lock = False
    count_clicks = 1
    while True:
        _, frame = cam.read()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_landmark_points = face_mesh.process(rgb_frame).multi_face_landmarks

        hand_process = hand_detector.process(rgb_frame)
        hands_landmarks_points = hand_process.multi_hand_landmarks
        hand_right_left = hand_process.multi_handedness

        frame_h, frame_w, _ = frame.shape  # webcam resolution

        # control the movement of the mouse on the screen
        if face_landmark_points and not move_mouse_lock:
            nose_points = plot_nose_points(face_landmark_points, frame, frame_w, frame_h)
            x_avg, y_avg = plot_nose_center(nose_points, frame)

            x_screen_landmark_scaled, y_screen_landmark_scaled = scale_positions(x=(x_avg / frame_w),
                                                                                 y=(y_avg / frame_h),
                                                                                 x_scale=scale_x_param,
                                                                                 y_scale=scale_y_param)

            screen_x, screen_y = get_screen_xy_after_scale(x_screen_landmark_scaled,
                                                           y_screen_landmark_scaled,
                                                           screen_w,
                                                           screen_h)

            # move mouse to desired location on screen
            pyautogui.moveTo(screen_x, screen_y, 0.1, pyautogui.easeInOutQuad)

        # control the clicks with right hand and the move_mouse_lock with left hand
        if hands_landmarks_points:
            points = hands_landmarks_points
            labels = [MessageToDict(i)['classification'][0]['label'] for i in hand_right_left]

            for index, hand in enumerate(points):  # we only want 1 hand to have the power
                if (labels[index] == "Left"):  # this is the RIGHT hand, due to mirror effect
                    thumb, index_finger = get_thumb_and_index_position(hand, frame, frame_w, frame_h)
                    plot_thumb_index_line(thumb, index_finger, frame, frame_w, frame_h, one_click_lock)
                    dist = calc_dist_thumb_index(thumb, index_finger)

                    if dist < click_threshold and not one_click_lock:
                        print(f'>>> (CLICK {count_clicks:,}!) dist between fingers: {round(dist, 3)}')
                        count_clicks += 1
                        pyautogui.click()
                        one_click_lock = True
                    elif one_click_lock and (dist > release_click_lock_threshold):
                        print("--- Released lock on click")
                        one_click_lock = False

                elif labels[index] == "Right":  # this is the LEFT hand due to mirror effect
                    # check if there is a "Closed_Fist" or "Open_Palm" for locking the mouse movement
                    point_couples_indexes_to_calc_dist = [(4, 6), (8, 2), (12, 1), (16, 0)]

                    fist_palm_dist = calc_left_hand_fist_dist(hand, point_couples_indexes_to_calc_dist)

                    if fist_palm_dist < fist_palm_threshold:
                        move_mouse_lock = True
                    else:
                        move_mouse_lock = False

                    plot_left_hand_relevant_lines(hand, point_couples_indexes_to_calc_dist, frame, frame_w, frame_h,
                                                  move_mouse_lock)

        frame = cv2.flip(frame, 1)
        cv2.imshow("APPLE VISION CONTROLLER", frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    # control the movement of the mouse with nose, left mouse click with right hand (click thumb and index),
    # added lock on mouse movement using left hand (open fist to allow movement)
    run_apple_vision_controller(scale_x_param=4.5,
                                scale_y_param=3,
                                click_threshold=0.05,
                                release_click_lock_threshold=0.07,
                                fist_palm_threshold=0.75)

# noteworthy in report:
# right hand click by dist
# left hand fist - prevents the mouse from moving until the palm is shown
# mouse moves by point on nose
