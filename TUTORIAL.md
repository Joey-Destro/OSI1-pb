# UsirevAI Tutorial

Welcome to the UsirevAI application! This guide will walk you through setting up, running, building, and using this AI-powered medical transcription and anamnesis extraction tool.

## 1. Prerequisites

Before running the application, you need:
- **Python 3.10+** installed on your system.
- **FFmpeg** installed (required by `pydub` for audio conversion).
- A **Google Gemini API Key** (for extracting structured medical data).
- *(Optional but recommended)* A CUDA-compatible GPU for significantly faster Whisper model inference.

### Setting up the Environment
It is highly recommended to use a virtual environment.
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

Set your Gemini API key as an environment variable before running the app:
```bash
export GEMINI_API_KEY="your_api_key_here"  # On Windows: set GEMINI_API_KEY="your_api_key_here"
```

## 2. Running the App for Development

To run the application locally in development mode:
```bash
python main.py
```
This script will automatically start the FastAPI server using Uvicorn on `http://127.0.0.1:7860/` and attempt to open your default web browser to the application page.

*Note: The first time you run the application, it will download the Hugging Face Whisper model (`mikr/whisper-small-cs-cv11`), which may take a few minutes depending on your internet connection.*

## 3. Building the Standalone Executable

If you want to package the application so it can be easily distributed and run on a machine without installing Python or dependencies, you can use the provided build script.

Run the build script:
```bash
python build_installer.py
```

This script will:
1. Use `PyInstaller` to bundle the application into a standalone folder (located in `dist/UsirevAI`). We use a folder structure rather than a single file because extracting massive Machine Learning libraries (like PyTorch) from a single file takes a prohibitively long time upon every launch.
2. Archive the output directory into a portable `UsirevAI_LocalApp.zip` file.

You can then distribute the `.zip` file. The end user simply extracts it and runs the `UsirevAI` executable inside.

## 4. How to Use the Application

1. **Launch the app** (either via `python main.py` or by double-clicking the built executable).
2. The application will open in your web browser.
3. **Upload an audio file** of a doctor-patient conversation. Supported formats depend on your FFmpeg installation but generally include `.mp3`, `.wav`, `.m4a`, and `.webm`.
4. Choose the Gemini model you wish to use from the dropdown (e.g., `gemini-1.5-flash`).
5. Click "Process".
6. The app will first transcribe the audio locally using the Whisper model. Then, it sends the transcription to the Gemini API to intelligently divide the dialogue between "Lékař" (Doctor) and "Pacient" (Patient), and extract structured medical information into the Anamnéza fields.
7. The structured Anamnéza and formatted transcription will be displayed on the screen!
