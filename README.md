# OpenYTMP3Downloader

OpenYTMP3Downloader is a Python-based, fully open-source desktop application designed to download YouTube content in MP3 format. It aims to provide a modern and user-friendly graphical interface (GUI) instead of complex command-line tools.

## Why Open Source?

This project is built on the principles of transparency and community-driven development. The entire source code is open for inspection, modification, and improvement. We welcome any contributions through Pull Requests and bug reports via Issues.

## Key Features

-   Simplicity: Start downloading with just a URL—no complex configurations required.
    
-   High Quality: Leverages the `yt-dlp` library to ensure the highest possible audio quality.
    
-   Flexibility: Includes `cookies.txt` support to access age-restricted or region-locked videos.
    
-   Developer Friendly: Clean code structure with a modular file organization.
    

## Quick Start

1.  Install Dependencies:
    
    Bash
    
    ```
    pip install -r requirement.txt
    ```
    
2.  Run the Application:
    
    Bash
    
    ```
    python main.py
    ```
    

> Note: `ffmpeg` must be installed on your system and added to your PATH for audio conversion.

## Project Structure

-   `main.py`: The entry point of the application.
    
-   `downloader.py`: Core download logic and audio processing.
    
-   `ui.py` & `widgets.py`: Modern UI components and user interaction handlers.
    
-   `utils.py`: Utility functions and file management.
    

## Contributing

As an open-source project, your contributions are highly appreciated:

1.  Fork the repository.
    
2.  Add your feature or fix.
    
3.  Submit a Pull Request.
    

Disclaimer: This tool is intended for personal use and educational purposes only.