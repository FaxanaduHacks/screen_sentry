import cv2
import numpy as np
import mss
import platform
import pytesseract
import time
from screeninfo import get_monitors
import re

class ScreenSentry:
    """
    ScreenSentry is a class for capturing and redacting sensitive information
    from the screen.

    Attributes:
        None
    """

    @staticmethod
    def list_displays():
        """
        Lists available displays.

        Returns:
            list: A list of display monitors.
        """
        try:
            sys_platform = platform.system()
            if sys_platform == "Darwin" or sys_platform == "Linux":
                monitors = get_monitors()
                if not monitors:
                    print("No displays found.")
                    return None
                return monitors
            elif sys_platform == "Windows":
                import win32api
                monitors = []
                i = 0
                while True:
                    try:
                        monitor = win32api.EnumDisplayMonitors(None, None)[i]
                        monitors.append(monitor)
                        i += 1
                    except IndexError:
                        break
                return monitors if monitors else None
            else:
                print("Unsupported platform. Only macOS, Linux, and Windows are supported.")
                return None
        except Exception as e:
            print(f"An error occurred while listing displays: {str(e)}")
            return None

    @staticmethod
    def capture_screen(display_idx, words_to_detect, privacy_mode, capture_entire_display=True):
        """
        Captures the specified screen and redacts sensitive information if
        privacy mode is enabled.

        Args:
            display_idx (int): Index of the display to capture.
            words_to_detect (list): List of words to detect and redact.
            privacy_mode (bool): Flag indicating whether privacy mode is
            enabled.
            capture_entire_display (bool): Flag indicating whether to capture
            the entire display.

        Returns:
            None
        """
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[display_idx]

                region = {
                    "left": monitor["left"],
                    "top": monitor["top"],
                    "width": monitor["width"],
                    "height": monitor["height"] if capture_entire_display else monitor["height"] // 2
                }

                cv2.namedWindow("Captured Frame", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Captured Frame", 1280, 720)  # Set initial window size

                last_ocr_time = time.time()
                ocr_interval = 0.05  # Adjust based on performance

                while True:
                    frame = np.array(sct.grab(region))
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    if time.time() - last_ocr_time > ocr_interval:
                        last_ocr_time = time.time()
                        if privacy_mode:
                            word_boxes = ScreenSentry.perform_ocr_privacy_mode(gray, words_to_detect)
                        else:
                            word_boxes = ScreenSentry.perform_ocr(gray, words_to_detect)
                        ScreenSentry.redact_words(frame, word_boxes)

                    cv2.imshow("Captured Frame", frame)

                    key = cv2.waitKey(1)
                    if key in (ord('q'), 27):
                        break

                cv2.destroyAllWindows()
        except Exception as e:
            print(f"An error occurred while capturing the screen: {str(e)}")

    @staticmethod
    def perform_ocr(image, words_to_detect):
        """
        Performs OCR (Optical Character Recognition) to detect sensitive words.

        Args:
            image (numpy.ndarray): Image to perform OCR on.
            words_to_detect (list): List of words to detect and redact.

        Returns:
            list: Bounding boxes of detected words.
        """
        try:
            # Apply thresholding using OTSU's method:
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # Perform OCR on thresholded image:
            data = pytesseract.image_to_data(thresholded, output_type=pytesseract.Output.DICT)

            # Extract word bounding boxes for words in words_to_detect:
            word_boxes = []
            for i, text in enumerate(data['text']):
                # Filter out non-empty and low-confidence detections:
                if text.lower() in words_to_detect and int(data['conf'][i]) > 0:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    word_boxes.append((x, y, w, h))

            return word_boxes
        except Exception as e:
            print(f"An error occurred while performing OCR: {str(e)}")
            return []

    @staticmethod
    def perform_ocr_privacy_mode(image, patterns):
        """
        Performs OCR in privacy mode to detect sensitive patterns.

        Args:
            image (numpy.ndarray): Image to perform OCR on.
            patterns (list): List of regex patterns to detect and redact.

        Returns:
            list: Bounding boxes of detected patterns.
        """
        try:
            # Apply thresholding using OTSU's method:
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # Perform OCR on thresholded image:
            data = pytesseract.image_to_data(thresholded, output_type=pytesseract.Output.DICT)

            # Compile the patterns if they are strings
            compiled_patterns = [re.compile(pattern) if isinstance(pattern, str) else pattern for pattern in patterns]

            # Extract word bounding boxes for words in words_to_detect:
            word_boxes = []
            for i, text in enumerate(data['text']):
                # Filter out non-empty and low-confidence detections:
                if any(pattern.match(text) for pattern in compiled_patterns) and int(data['conf'][i]) > 0:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    word_boxes.append((x, y, w, h))

            return word_boxes
        except Exception as e:
            print(f"An error occurred while performing OCR in privacy mode: {str(e)}")
            return []

    @staticmethod
    def redact_words(image, word_boxes, padding=1):
        """
        Redacts sensitive words in the image with a slight padding.

        Args:
            image
        :param image: numpy.ndarray: Image containing the sensitive words.
        :param word_boxes: list: List of bounding boxes of detected sensitive
        words.
        :param padding: int: Padding size around each word bounding box.
        :return: None
        """
        for (x, y, w, h) in word_boxes:
            # Add padding to the word bounding box
            x -= padding
            y -= padding
            w += 2 * padding
            h += 2 * padding
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)

            # Add a slight delay to prevent flashing
            time.sleep(0.1)

    @staticmethod
    def generate_word_variations(words_to_redact):
        """
        Generate variations of words to redact.

        Args:
            words_to_redact (list): List of words to redact.

        Returns:
            list: List containing variations of the input words, including
                  lowercase, uppercase, capitalized, plural forms, and
                  variations with punctuation marks.
        """
        try:
            # Add default redacted words:
            words_to_redact.extend(['apple', 'banana', 'password'])

            # Generate word variations:
            word_variations = []
            for word in words_to_redact:
                # Add variations without punctuation or 's':
                word_variations.append(word.lower())
                word_variations.append(word.upper())
                word_variations.append(word.capitalize())

                # Add variations with punctuation marks:
                punctuation_marks = ['.', ',', '!', '?', '--', '-', "'"]
                for mark in punctuation_marks:
                    word_variations.append(word.lower() + mark)
                    word_variations.append(word.upper() + mark)
                    word_variations.append(word.capitalize() + mark)

                # Add variations with 's' for plural forms:
                plural_variations = [word.lower() + 's', word.upper() + 'S', word.capitalize() + 's']
                for plural in plural_variations:
                    word_variations.append(plural)

                # Add variations with punctuation marks for plural forms:
                for mark in punctuation_marks:
                    plural_with_mark = [word.lower() + 's' + mark, word.upper() + 'S' + mark, word.capitalize() + 's' + mark]
                    for plural in plural_with_mark:
                        word_variations.append(plural)


            return word_variations
        except Exception as e:
            print(f"An error occurred while generating word variations: {str(e)}")
            return []

    @staticmethod
    def generate_patterns():
        """
        Generates regex patterns for detecting sensitive information.

        Returns:
            tuple: Tuple containing phone number, social security number, and IP address patterns.
        """
        try:
            # Phone number patterns:
            phone_number_patterns = [
                r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # 123-456-7890, 123.456.7890, 123 456 7890
                r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b",    # (123) 456-7890, (123)4567890
            ]

            # Social security number patterns:
            ssn_patterns = [
                r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b",  # 123-45-6789, 123.45.6789, 123 45 6789
            ]

            # IP address patterns:
            ip_address_patterns = [
                r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # Matches IPv4 addresses (e.g., 192.168.1.1, 10.10.10.1)
                r"\b(?:\d{1,3}\.){3}\d{1,3}(?![\d.])\b",  # Matches IPv4 addresses not followed by a digit or dot
                r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",  # Matches IPv6 addresses
            ]

            return phone_number_patterns, ssn_patterns, ip_address_patterns
        except Exception as e:
            print(f"An error occurred while generating patterns: {str(e)}")
            return [], [], []

    @staticmethod
    def update_word_boxes(last_word_boxes, current_word_boxes):
        """
        Updates the state of detected word boxes.

        Args:
            last_word_boxes (list): List of word boxes detected in the previous frame.
            current_word_boxes (list): List of word boxes detected in the current frame.

        Returns:
            list: Updated list of word boxes.
        """
        updated_word_boxes = []
        # Iterate over the current word boxes and check if they match with the previous ones
        for box in current_word_boxes:
            # If the current box matches with any of the previous boxes, keep the previous one
            if not any(ScreenSentry.is_matching_box(box, prev_box) for prev_box in last_word_boxes):
                updated_word_boxes.append(box)
        # Extend the updated word boxes with the previous ones
        updated_word_boxes.extend(last_word_boxes)
        return updated_word_boxes

    @staticmethod
    def is_matching_box(box1, box2, threshold=10):
        """
        Checks if two bounding boxes match within a threshold.

        Args:
            box1 (tuple): Bounding box coordinates (x, y, w, h).
            box2 (tuple): Bounding box coordinates (x, y, w, h).
            threshold (int): Maximum threshold for matching.

        Returns:
            bool: True if the boxes match within the threshold, False otherwise.
        """
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        # Calculate the center coordinates of the boxes
        center1 = (x1 + w1 / 2, y1 + h1 / 2)
        center2 = (x2 + w2 / 2, y2 + h2 / 2)
        # Calculate the Euclidean distance between the centers
        distance = np.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)
        # Check if the distance is within the threshold
        return distance < threshold

if __name__ == "__main__":
    try:
        default_redacted_words = ['apple', 'banana', 'password']  # Default list of words to redact

        words_input = input("Enter a list of words to redact (separated by spaces), or press Enter to use default: ")
        words_to_redact = words_input.split() if words_input else default_redacted_words

        words_to_detect = ScreenSentry.generate_word_variations(words_to_redact)

        privacy_mode = input("Enable privacy mode ? (yes/no): ").lower() == "yes"

        if privacy_mode:
            phone_number_patterns, ssn_patterns, ip_address_patterns = ScreenSentry.generate_patterns()
            words_to_detect.extend(phone_number_patterns)
            words_to_detect.extend(ssn_patterns)
            words_to_detect.extend(ip_address_patterns)

        monitors = ScreenSentry.list_displays()
        if monitors is not None:
            print("Select a display to capture:")
            for i, monitor in enumerate(monitors, start=1):
                print(f"{i}: Display {i}")

            choice = input("Enter the number corresponding to the display you want to capture: ")

            try:
                choice = int(choice)
                if choice >= 1 and choice <= len(monitors):
                    ScreenSentry.capture_screen(choice, words_to_detect, privacy_mode)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

