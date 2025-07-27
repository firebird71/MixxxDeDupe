# MixxxDeDupe

A set of tools to identify and manage duplicate tracks in Mixxx M3U8 playlists, including a command-line script (`Mixxx_DeDupe.py`) and a graphical user interface (`Mixxx_DeDupe_GUI.py`). Designed primarily for Linux users, these tools support various tagged audio formats and are optimized for managing large music libraries.

<img width="400" height="528" alt="Mixxx DeDupe GUI" src="https://github.com/user-attachments/assets/34a0522a-a4b8-466c-a9e1-96b53296a6f7" />

## Overview

- **Mixxx_DeDupe.py**: A command-line Python script to detect duplicate tracks in M3U8 playlists based on metadata (title, artist) across formats like MP3, FLAC, OGG, M4A, WMA, AAC, WAV, and AIFF. The default output begins with `tracks:` followed by duplicate titles, designed for direct pasting into Mixxx's Search function. Tracks are sorted by title within Mixxx to enhance usability, reflecting how people typically organize and search their playlists.
- **Mixxx_DeDupe_GUI.py**: A GUI wrapper for `Mixxx_DeDupe.py`, providing a user-friendly interface with real-time output, file browsing, and customizable options, built with `tkinter`.

Both tools are tailored for Linux environments like Linux Mint, with file paths (e.g., `~/Media Drive/Music/Playlists`) and desktop integration optimized for this platform.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/firebird71/MixxxDeDupe.git
   cd MixxxDeDupe
   ```

2. **Install Dependencies**:
   - Ensure Python 3.6+ is installed.
   - Install the required package:
     ```bash
     pip3 install mutagen
     ```

3. **Make Scripts Executable** (Linux):
   ```bash
   chmod +x Mixxx_DeDupe.py Mixxx_DeDupe_GUI.py
   ```

4. **Optional Desktop Launcher** (Linux):
   - Create a `.desktop` file in `~/.local/share/applications/`:
     ```ini
     [Desktop Entry]
     Name=Mixxx DeDupe GUI
     Exec=/usr/bin/env python3 /home/<youruser>/MixxxDeDupe/Mixxx_DeDupe_GUI.py
     Type=Application
     Terminal=false
     Categories=Audio;Utility;
     ```
   - Replace `<youruser>` with your username and make it executable:
     ```bash
     chmod +x ~/.local/share/applications/Mixxx_DeDupe_GUI.desktop
     ```

## Usage

### Mixxx_DeDupe.py (Command-Line)
- **Run the Script**:
  ```bash
  ./Mixxx_DeDupe.py <m3u8_path> [output_txt] [options]
  ```
- **Arguments**:
  - `<m3u8_path>`: Path to the M3U8 playlist file (required, must end with `.m3u8`).
  - `[output_txt]`: Output file path (optional, defaults to `deduped_tracks.txt`).
- **Options**:
  - `-i, --include-info`: Include album and path info for duplicates (disables `-s` and `-n`).
  - `-s, --search-format`: Output duplicate titles in a single `tracks:| ...` line.
  - `-n <number>, --group-size <number>`: Group titles in chunks (1–50, default 10).
- **Examples**:
  - Default output (groups of 10):
    ```bash
    ./Mixxx_DeDupe.py "Auto PL - Rock.m3u8"
    ```
  - With custom output file:
    ```bash
    ./Mixxx_DeDupe.py "Auto PL - Rock.m3u8" custom_deduped.txt
    ```
  - With detailed info:
    ```bash
    ./Mixxx_DeDupe.py -i "Auto PL - Rock.m3u8"
    ```
  - With single-line output:
    ```bash
    ./Mixxx_DeDupe.py -s "Auto PL - Rock.m3u8"
    ```
  - With custom group size:
    ```bash
    ./Mixxx_DeDupe.py -n15 "Auto PL - Rock.m3u8"
    ```
- **Notes**: No output file is created if no duplicates are found. Run with `-h` for help.

### Mixxx_DeDupe_GUI.py (Graphical Interface)
1. **Launch the GUI**:
   - Double-click `Mixxx_DeDupe_GUI.py` (if executable) or use the desktop launcher.
   - Alternatively, run from the terminal:
     ```bash
     ./Mixxx_DeDupe_GUI.py
     ```

2. **Basic Operation**:
   - **Select M3U8 Playlist**: Click "Browse" to choose a `.m3u8` file or enter the path.
   - **Set Output File**: Defaults to `deduped_tracks.txt`; use "Browse" to change it.
   - **Options**:
     - Check `Include album and path info (-i)` for detailed output (disables `-s` and `-n`).
     - Check `Single-line output (-s)` for a `tracks:| ...` format.
     - Check `Group titles (-n)` to enable a spinbox (1–50, default 10) for grouping.
   - Click **Run DeDupe** to process the playlist.
   - View real-time output (e.g., `Processed 100/4736 files...`) in the scrollable text area.
   - The **Open Output File** button enables only if duplicates are found and the file exists.

3. **Notes**:
   - The window size is fixed at a minimum of 600x700 pixels to ensure all elements are visible.
   - The GUI relies on `Mixxx_DeDupe.py` and must be in the same directory.

## Dependencies

- **Python 3.6+**
- **mutagen**: For reading audio metadata (`pip3 install mutagen`)
- **tkinter**: Included with standard Python installations (no extra installation needed)

## Designed for Linux

This project is primarily designed and tested on Linux distributions, such as Linux Mint. The default file path (`~/Media Drive/Music/Playlists`) and `.desktop` launcher are Linux-specific. While it may work on other platforms with adjustments (e.g., Windows with `.pyw` or macOS with `py2app`), Linux optimization is the focus. Contributions to enhance cross-platform support are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Created by Chris Smith & Grok (xAI).
- Thanks to the open-source community for tools like `mutagen` and `tkinter`.
