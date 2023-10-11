import cv2
import pyautogui
import mediapipe as mp
import math
import subprocess

pyautogui.FAILSAFE = False
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.3, min_tracking_confidence=0.3)

mp_drawing = mp.solutions.drawing_utils

# Initialize flag variables for finger state
index_finger_down = False
middle_finger_down = False
little_finger_up = True
little_finger_last_state = True  # True if little finger is up, False if it's down
scroll_active = False
current_volume = 50  # Starting volume level (adjust as needed)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            index_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            middle_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
            middle_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
            little_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x
            little_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y
            thumb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
            thumb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
            ring_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x
            ring_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y
            hand_angle = math.degrees(math.atan2(index_finger_y - middle_finger_y, index_finger_x - middle_finger_x))

            # Calculate the distance between two finger tips (e.g., middle finger and thumb)
            middle_thumb_distance = math.sqrt((middle_finger_x - thumb_x) ** 2 + (middle_finger_y - thumb_y) ** 2)
            ring_thumb_distance = math.sqrt((ring_finger_x - thumb_x) ** 2 + (ring_finger_y - thumb_y) ** 2)

            # Get the screen's resolution
            screen_width, screen_height = pyautogui.size()

            # Move the cursor to the calculated position
            cursor_x = int(index_finger_x * screen_width)
            cursor_y = int(index_finger_y * screen_height)
            pyautogui.moveTo(cursor_x, cursor_y)

            # Detect finger state changes for left and right clicks
            if middle_thumb_distance < 0.03:
                if not middle_finger_down:
                    # Perform right-click
                    pyautogui.click(button='right')
                    middle_finger_down = True
            else:
                middle_finger_down = False

            if ring_thumb_distance < 0.03:
                if not index_finger_down:
                    # Perform left-click
                    pyautogui.click(button='left')
                    index_finger_down = True
            else:
                index_finger_down = False

            # Volume control logic
            vol =1
            # Determine if the little finger is pointing up or down
            if little_finger_y < thumb_y:
                # Use the amixer command to increase the volume
                subprocess.call(['amixer', 'set', 'Master', str(vol) + '%+'])

            elif little_finger_y > thumb_y:
                # Use the amixer command to increase the volume
                subprocess.call(['amixer', 'set', 'Master', str(vol) + '%-'])
            
            # Detect when index and middle fingers are close together and pointing up for scrolling
            if math.sqrt((index_finger_x - middle_finger_x) ** 2 + (index_finger_y - middle_finger_y) ** 2) < 0.03 and hand_angle < 30:
                if not scroll_active:
                    # Perform scroll up when fingers are together and pointing up
                    pyautogui.scroll(1)  # Scroll up
                    scroll_active = True

            elif math.sqrt((index_finger_x - middle_finger_x) ** 2 + (index_finger_y - middle_finger_y) ** 2) < 0.03 and hand_angle > 150:
                if not scroll_down_active:
                    # Perform scroll down when fingers are together and pointing down
                    pyautogui.scroll(-1)  # Scroll down
                    scroll_down_active = True
                scroll_up_active = False
            else:
                scroll_up_active = False
                scroll_down_active = False
            
                        # Detect if all fingers are closed (make a fist)
            if index_finger_y > middle_finger_y and middle_finger_y > little_finger_y:
                is_fist = True
            else:
                is_fist = False

            # Take a screenshot when a fist is detected
            if is_fist and not screenshot_taken:
                subprocess.run(["scrot", "screenshot.png"])  # Use scrot to capture screenshot
                screenshot_taken = True
            elif not is_fist:
                screenshot_taken = False

    cv2.imshow("Hand Tracking", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
