# screen_sentry

This program is a Python script named `screen_sentry.py` designed for capturing and redacting a list of user provided sensitive information from the screen in real-time. It utilizes several libraries such as OpenCV, MSS (Multiple Screen Capture), and Pytesseract for optical character recognition (OCR). This program has a `privacy mode` that, when enabled, redacts social security numbers, phone numbers and IP addresses automatically. I have another regex for redacting URL's, but I'm still putting the finishing touches on it.

The purpose of this script is to redact sensitive information, enabling the user to only share one window instead of the entire screen on their video conferencing application of choice (e.g. MS Teams, Discord, Zoom, Google Meet etc.).

Note: it is sluggish, I do not use graphic acceleration. The plan is to make this an OBS plugin so we can have a virtual camera interface to just share that automatically redacts the sensitive information.

The main functionalities of the ScreenSentry class include:

- Listing available displays.
- Capturing the specified screen and redacting sensitive information if privacy mode is enabled.
- Performing OCR (Optical Character Recognition) to detect sensitive words or patterns.
- Redacting user provided sensitive words in the captured image.
- Generating variations of words to redact.
- Generating regex patterns for detecting sensitive information such as phone numbers, social security numbers, and IP addresses.

The script also contains a command-line interface for user interaction. Upon execution, it prompts the user to enter a list of words to redact, enables privacy mode, and selects the display to capture. It then continuously captures the screen, performs OCR, and redacts sensitive information until the user exits the program.

Additionally, the script includes error handling mechanisms to gracefully handle exceptions that may occur during execution.

Overall, ScreenSentry provides a convenient and customizable solution for capturing and redacting sensitive information from the screen, suitable for various privacy and security applications.

## Installation

To use this program, you need to install the following Python modules via pip:

```bash
pip install numpy opencv-python mss pytesseract screeninfo
```

Note: don't forget to install tesseract on your system in order for the pytesseract library to function.

To install tesseract on macOS, you can install the package with Homebrew:

```bash
brew install tesseract
```

Note: Homebrew installation isn't covered in this documentation.

## Usage

1. Run the script.
2. Enter a list of words to redact when prompted, separated by spaces. Press Enter without customizations to use the default list.

## Features

ScreenSentry offers the following features:

- Capture and redact sensitive information from the screen in real-time.
- Ability to specify custom words or patterns to redact.
- Privacy mode for automatic redaction of common sensitive patterns (e.g. SSN, Phone, URL, IP Addresses etc.).
- Cross-platform compatibility (macOS, Linux, and Windows).

## Parameters

The program takes the following parameters:

- `display_idx`: Index of the display to capture.
- `words_to_detect`: List of words or patterns to detect and redact.
- `privacy_mode`: Flag indicating whether privacy mode is enabled.
- `capture_entire_display`: Flag indicating whether to capture the entire display.

## Customization

Feel free to modify the program according to your requirements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Liability Clause

This software is provided "as is," without warranty of any kind, express or implied. In no event shall the author be liable for any claim, damages, or other liability arising from the use or distribution of this software. The user assumes all responsibility for the use of this software and acknowledges that any reliance on it is at their own risk. By downloading or using this software, the user agrees to these terms.

## Acknowledgments

This program utilizes the OpenCV library for computer vision tasks. Credits to the OpenCV community for their contributions.

The development of this application benefited from the assistance of language models, including GPT-3.5 and GPT-4, provided by OpenAI. The author acknowledges the valuable contributions made by these language models in generating design ideas and providing insights during the development process.
