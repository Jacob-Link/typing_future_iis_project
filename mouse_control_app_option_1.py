import cv2
import mediapipe as mp
import pyautogui
import numpy as np


def calc_dist_thumb_index(thumb, index_finger):
    thumb_np = np.array(thumb)
    index_np = np.array(index_finger)

    dist = np.linalg.norm(thumb_np - index_np)

    return dist


def scale_positions(x, y, x_scale=4.0, y_scale=2.0):
    # used to move mouse to all parts of screen from the center without needing to make extreme physical movements
    x_scaled = x_scale * (x - 0.5) + 0.5
    y_scaled = y_scale * (y - 0.5) + 0.5

    x_final = min(x_scaled, 1)
    y_final = min(y_scaled, 1)

    return x_final, y_final


def run_apple_vision_controller(move_mouse_by: str,
                                scale_x: float,
                                scale_y: float,
                                click_threshold: float,
                                release_click_lock_threshold: float):
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
        hands_landmarks_points = hand_detector.process(rgb_frame).multi_hand_landmarks

        frame_h, frame_w, _ = frame.shape

        if face_landmark_points:
            landmarks = face_landmark_points[0].landmark

            if move_mouse_by == "avg_eyes":
                all_eyes_scaled = []
                for id, landmark in enumerate(landmarks[468:478]):  # both eyes with mid eye
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)

                    cv2.circle(frame, (x, y), 3, (0, 255, 0))
                    # print(x, y)
                    all_eyes_scaled.append((x, y))

                x_avg = int(sum([x[0] for x in all_eyes_scaled]) / len(all_eyes_scaled))
                y_avg = int(sum([x[1] for x in all_eyes_scaled]) / len(all_eyes_scaled))

                point_to_track = (x_avg, y_avg)
                cv2.circle(frame, point_to_track, 4, (0, 255, 0), -1)

                # move mouse by the point chosen
                x_screen_landmark = point_to_track[0] / frame_w
                y_screen_landmark = point_to_track[1] / frame_h

                screen_x = screen_w * (1 - x_screen_landmark)  # mirror effect, we want  move right -> moves mouse right
                screen_y = screen_h * y_screen_landmark

                pyautogui.moveTo(screen_x, screen_y)

            if move_mouse_by == "nose":
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
            for hand_num, hand in enumerate(hands_landmarks_points[::-1]):  # we only want 1 hand to have the power
                if hand_num:  # reversed to have the first hand that joined in index 0
                    break
                # drawing_utils.draw_landmarks(frame, hand)
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

                cv2.line(frame,
                         (int(thumb[0] * frame_w), int(thumb[1] * frame_h)),
                         (int(index_finger[0] * frame_w), int(index_finger[1] * frame_h)),
                         (255, 0, 0), 2)

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

        frame = cv2.flip(frame, 1)
        cv2.imshow("APPLE VISION CONTROLLER", frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    # control the movement of the mouse with eyes and clicks with hand gesture
    run_apple_vision_controller(move_mouse_by="nose",
                                scale_x=4.5,
                                scale_y=3,
                                click_threshold=0.05,
                                release_click_lock_threshold=0.07)

# noteworthy in report:
# --- mouse click by fingers dist
# 1. limit to 1 hand - the first detected
# 2. lock and release based on the dist, so that we won't get multiple mouse clicks in 1 finger click
# --- mouse movement
# 3. scale to get to all screen without moving from chair...
