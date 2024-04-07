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


def run_apple_vision_controller(scale_x: float,
                                scale_y: float,
                                click_threshold: float,
                                release_click_lock_threshold: float,
                                fist_palm_threshold: float):
    move_mouse_lock = True
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    hand_detector = mp.solutions.hands.Hands()
    screen_w, screen_h = pyautogui.size()

    limit_to_one_click_flag = True
    count_clicks = 1
    while True:
        _, frame = cam.read()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_landmark_points = face_mesh.process(rgb_frame).multi_face_landmarks

        hand_process = hand_detector.process(rgb_frame)
        hands_landmarks_points = hand_process.multi_hand_landmarks
        hand_right_left = hand_process.multi_handedness

        frame_h, frame_w, _ = frame.shape

        if face_landmark_points and (not move_mouse_lock):
            landmarks = face_landmark_points[0].landmark

            landmarks = [landmarks[1], landmarks[45], landmarks[5], landmarks[275]]  # nose tip

            nose_points = []
            for point in landmarks:
                x = int(point.x * frame_w)
                y = int(point.y * frame_h)

                cv2.circle(frame, (x, y), 3, (0, 255, 0))

                nose_points.append((x, y))

            x_avg = int(sum([x[0] for x in nose_points]) / len(nose_points))
            y_avg = int(sum([x[1] for x in nose_points]) / len(nose_points))

            cv2.circle(frame, (x_avg, y_avg), 4, (255, 0, 0), -1)

            x_screen_landmark = x_avg / frame_w
            y_screen_landmark = y_avg / frame_h

            x_screen_landmark, y_screen_landmark = scale_positions(x=x_screen_landmark,
                                                                   y=y_screen_landmark,
                                                                   x_scale=scale_x,
                                                                   y_scale=scale_y)

            screen_x = screen_w * (1 - x_screen_landmark)  # mirror effect, we want  move right -> moves mouse right
            screen_y = screen_h * y_screen_landmark

            # pyautogui.moveTo(screen_x, screen_y)
            pyautogui.moveTo(screen_x, screen_y, 0.1, pyautogui.easeInOutQuad)

        if hands_landmarks_points:

            # right hand used for mouse click and left for start and stop movement of mouse.

            points = hands_landmarks_points
            labels = [MessageToDict(i)['classification'][0]['label'] for i in hand_right_left]

            for index, hand in enumerate(points):  # we only want 1 hand to have the power
                # drawing_utils.draw_landmarks(frame, hand)
                if (labels[index] == "Left"):  # this is the right hand, due tot mirror effect
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

                elif labels[index] == "Right":  # this is the left hand due to mirror effect
                    # check if there is a "Closed_Fist" or "Open_Palm" for locking the mouse movement
                    # drawing_utils.draw_landmarks(frame, hand)
                    point_couples_indexes_to_calc_dist = [(4, 6), (8, 2), (12, 1), (16, 0)]

                    # plot the distance used for the fist and palm calculation
                    line_color = (255, 0, 0)
                    if move_mouse_lock:
                        line_color = (0, 0, 255)

                    # plot lines for vis purposes - red lines when the lock is active
                    for p1_index, p2_index in point_couples_indexes_to_calc_dist:
                        p1 = hand.landmark[p1_index]
                        p2 = hand.landmark[p2_index]

                        p1_plot = int(p1.x * frame_w), int(p1.y * frame_h)
                        p2_plot = int(p2.x * frame_w), int(p2.y * frame_h)

                        cv2.circle(img=frame, center=p1_plot, radius=9, color=(0, 255, 0), thickness=-1)
                        cv2.circle(img=frame, center=p2_plot, radius=9, color=(0, 255, 0), thickness=-1)

                        cv2.line(frame, (p1_plot), (p2_plot), line_color, 2)

                    fist_palm_dist = calc_left_hand_fist_dist(hand, point_couples_indexes_to_calc_dist)
                    if fist_palm_dist < fist_palm_threshold:
                        move_mouse_lock = True
                    else:
                        move_mouse_lock = False

        # print(f"{move_mouse_lock= }")

        frame = cv2.flip(frame, 1)
        cv2.imshow("APPLE VISION CONTROLLER", frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    # control the movement of the mouse with eyes and clicks with hand gesture
    run_apple_vision_controller(scale_x=4.5,
                                scale_y=3,
                                click_threshold=0.05,
                                release_click_lock_threshold=0.07,
                                fist_palm_threshold=0.75)

# noteworthy in report:
# right hand click by dist
# left hand fist - prevents the mouse from moving until the palm is shown
# mouse moves by point on nose
