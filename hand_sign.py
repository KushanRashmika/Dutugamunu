import math
import cv2 as cv
import mediapipe as mp


class HandSign:
    FINGER_TIPS = (8, 12, 16, 20)
    FINGER_PIPS = (6, 10, 14, 18)

    # thumb, index, middle, ring, pinky (1 = extended)
    SIGNS = {
        "walk":      (1, 0, 0, 0, 0),
        "walk_jump": (1, 1, 0, 0, 0),
        "jump":      (0, 1, 0, 0, 0),
        "start":     (0, 0, 0, 0, 0),
        "exit":      (1, 1, 1, 0, 0),
    }

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0,
        )

    def recognition(self, frame):
        if frame is None:
            return None
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        return self.hands.process(rgb)

    @staticmethod
    def _dist(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def _finger_states(self, lm):
        # Thumb: tip is farther from the pinky base than the IP joint,
        # which works for either hand and doesn't depend on image scale.
        thumb = 1 if self._dist(lm[4], lm[17]) > self._dist(lm[3], lm[17]) else 0
        fingers = [thumb]
        for tip, pip in zip(self.FINGER_TIPS, self.FINGER_PIPS):
            fingers.append(1 if lm[tip].y < lm[pip].y else 0)  # smaller y = higher up
        return tuple(fingers)

    def play_sign(self, result):
        """Returns a sign name, 'unknown' if a hand is seen but not matched,
        or None if no hand is detected."""
        if result is None or not result.multi_hand_landmarks:
            return None

        lm = result.multi_hand_landmarks[0].landmark
        fingers = self._finger_states(lm)

        for name, pattern in self.SIGNS.items():
            if pattern == fingers:
                return name
        return "unknown"

    def mouse_pointer(self, result, width=1280, height=720):
        if result is None or not result.multi_hand_landmarks:
            return None
        tip = result.multi_hand_landmarks[0].landmark[8]
        return int(tip.x * width), int(tip.y * height)

    def close(self):
        self.hands.close()