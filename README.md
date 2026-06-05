# FrameExtractor

A desktop utility to scrub through video files and extract frames losslessly in their original resolution.

## How it Works
The application provides a borderless dark-themed UI built with CustomTkinter. When a video file is loaded or dropped onto the interface, the OpenCV backend decodes the video frames, updates a preview widget in real-time as the slider moves, and saves the selected frame losslessly as a PNG using Pillow.

## Tech Stack
- **Languages/Frameworks:** Python, CustomTkinter
- **Services/Libraries:** OpenCV, Pillow, TkinterDnD2
- **Infrastructure:** Windows, Linux

## Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/ibodeth/FrameExtractor.git
   cd FrameExtractor
   ```
2. Install dependencies:
   ```bash
   pip install opencv-python customtkinter tkinterdnd2 Pillow
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## License
MIT
