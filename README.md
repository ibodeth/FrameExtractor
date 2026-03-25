🎞️ FrameExtractor (formerly LastFrameDropper)

FrameExtractor is a minimalist desktop tool that allows you to scrub through videos and extract any exact frame losslessly.
Built for AI video generation workflows where frame continuity and precise selection are critical.

📸 Preview

Drag a video → scrub through the timeline → preview the exact frame → save it losslessly in original resolution.

🚀 What It Does

Drag & drop a video file anywhere on the app

Interactive Slider: Scrub through the entire video frame-by-frame

Real-time Preview: See exactly what you are extracting with a built-in viewer

Saves the selected frame as a PNG with no re-encoding

Keeps original resolution and aspect ratio perfectly intact

<img src="app.png" width="200" >


🧠 AI Video Use Cases

Designed for:

Video continuation & looping (Runway, Pika, Luma, SVD)

Frame-to-frame consistency and keyframe selection

Image-to-video / video-to-video pipelines

Typical flow:

Generate a video

Open it in FrameExtractor and scrub to the perfect frame

Extract and save the exact frame

Feed that frame back into the AI model as a starting point or reference

This reduces visual jumps and keeps camera, lighting, and composition completely consistent.

✨ Features

Global drag & drop interface

Real-time video frame preview

Smooth timeline scrubbing slider

Lossless PNG frame extraction

Original resolution preserved

Fast (OpenCV + PIL backend)

Borderless, dark-themed modern UI

🛠 Tech Stack

Python 3

OpenCV

Pillow (PIL)

CustomTkinter

TkinterDnD2

📦 Installation


```bash
# Clone the repository
git clone https://github.com/ibodeth/FrameExtractor.git

# Go to project directory
cd FrameExtractor
```


▶️ Run


```bash
python main.py
```


Drop a video file into the window, use the slider to find your desired frame, and click "Save Selected Frame".

🧑‍💻 Developer

İbrahim Nuryağınlı

📄 License

MIT License
