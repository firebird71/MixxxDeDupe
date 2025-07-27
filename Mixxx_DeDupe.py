# Mixxx_DeDupe.py
# Created by Chris Smith & Grok
#
# MIT License
#
# Copyright (c) 2025 Chris Smith
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from mutagen.asf import ASF
from mutagen.aac import AAC
from mutagen.wave import WAVE
from mutagen.aiff import AIFF
import os
import sys
import argparse

# Function to get metadata (title, artist, album, path) from various audio files
def get_metadata(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.mp3':
            audio = MP3(file_path, ID3=ID3)
            return {
                'title': audio.get('TIT2', ['Unknown'])[0],
                'artist': audio.get('TPE1', ['Unknown'])[0],
                'album': audio.get('TALB', ['Unknown'])[0],
                'path': file_path
            }
        elif ext == '.flac':
            audio = FLAC(file_path)
            return {
                'title': audio.get('title', ['Unknown'])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'path': file_path
            }
        elif ext == '.ogg':
            audio = OggVorbis(file_path)
            return {
                'title': audio.get('title', ['Unknown'])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'path': file_path
            }
        elif ext in ('.m4a', '.mp4'):
            audio = MP4(file_path)
            return {
                'title': audio.get('©nam', ['Unknown'])[0],
                'artist': audio.get('©ART', ['Unknown'])[0],
                'album': audio.get('©alb', ['Unknown'])[0],
                'path': file_path
            }
        elif ext == '.wma':
            audio = ASF(file_path)
            return {
                'title': audio.get('Title', ['Unknown'])[0],
                'artist': audio.get('Author', ['Unknown'])[0],
                'album': audio.get('WM/AlbumTitle', ['Unknown'])[0],
                'path': file_path
            }
        elif ext == '.aac':
            audio = AAC(file_path)
            return {
                'title': audio.get('title', ['Unknown'])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'path': file_path
            }
        elif ext == '.wav':
            audio = WAVE(file_path)
            return {
                'title': audio.get('TIT2', ['Unknown'])[0],
                'artist': audio.get('TPE1', ['Unknown'])[0],
                'album': audio.get('TALB', ['Unknown'])[0],
                'path': file_path
            }
        elif ext in ('.aiff', '.aif'):
            audio = AIFF(file_path)
            return {
                'title': audio.get('TIT2', ['Unknown'])[0],
                'artist': audio.get('TPE1', ['Unknown'])[0],
                'album': audio.get('TALB', ['Unknown'])[0],
                'path': file_path
            }
        else:
            print(f"Unsupported file format: {file_path}")
            return None
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")
        return None

# Function to find duplicates in the M3U8 playlist and write to output
def find_duplicates_m3u8(m3u8_path, output_txt, include_info, search_format, group_size):
    # Dictionary to store tracks, keyed by (title, artist)
    tracks = {}
    base_dir = os.path.expanduser("~/Media Drive/Music")
    file_count = 0
    total_files = sum(1 for line in open(m3u8_path, 'r', encoding='utf-8') if line.strip() and not line.startswith('#'))
    
    # Read the M3U8 file line by line
    with open(m3u8_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip comments and empty lines
                if not os.path.isabs(line):  # Handle relative paths
                    line = os.path.join(base_dir, line)
                file_path = os.path.normpath(line)
                if os.path.exists(file_path):
                    metadata = get_metadata(file_path)
                    if metadata:
                        key = (metadata['title'].lower(), metadata['artist'].lower())
                        if key not in tracks:
                            tracks[key] = []
                        tracks[key].append(metadata)
                else:
                    print(f"File not found: {file_path}")
                file_count += 1
                if file_count % 100 == 0:  # Show progress every 100 files
                    print(f"Processed {file_count}/{total_files} files...")
    
    # Collect duplicate titles
    duplicate_titles = [
        f'"{title}"' if ' ' in title else title
        for title, artist in tracks
        if len(tracks[(title, artist)]) > 1
    ]
    
    # Only write output file if duplicates are found
    if duplicate_titles:
        with open(output_txt, 'w', encoding='utf-8') as f:
            if include_info:
                # Write artist, title, album, and path for duplicates (overrides -s and -n)
                for key, track_list in tracks.items():
                    if len(track_list) > 1:
                        f.write(f"Duplicate: {key[1]} - {key[0]}\n")
                        for track in track_list:
                            f.write(f"  - Album: {track['album']}, Path: {track['path']}\n")
                        f.write("\n")
            else:
                if search_format:
                    # Output all titles in a single line for -s
                    f.write(f"tracks:{' | '.join([''] + duplicate_titles)}\n")
                else:
                    # Default: group titles in chunks of group_size
                    for i in range(0, len(duplicate_titles), group_size):
                        f.write(f"tracks:{' | '.join([''] + duplicate_titles[i:i + group_size])}\n\n")
        return True
    return False

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Find duplicate songs in a Mixxx M3U8 playlist across all tagged audio formats")
    parser.add_argument("m3u8_path", help="Input M3U8 playlist file (must have .m3u8 extension)")
    parser.add_argument("output_txt", nargs='?', default="deduped_tracks.txt", help="Output text file for duplicates (default: deduped_tracks.txt)")
    parser.add_argument("-i", "--include-info", action="store_true", help="Include album and path info (disables grouping, -s, and -n)")
    parser.add_argument("-s", "--search-format", action="store_true", help="Output duplicate titles in a single | -separated line with 'tracks:' prefix and | before each title")
    parser.add_argument("-n", "--group-size", type=int, default=10, help="Number of titles per group in default output (1-50, default: 10)")
    args = parser.parse_args()

    # Check if input file has .m3u8 extension
    if not args.m3u8_path.lower().endswith('.m3u8'):
        print("Error: Input file must be an .m3u8 playlist")
        sys.exit(1)

    # Validate group_size
    if args.group_size < 1 or args.group_size > 50:
        print("Error: Group size must be between 1 and 50")
        sys.exit(1)

    m3u8_path = os.path.expanduser(args.m3u8_path)
    output_txt = os.path.expanduser(args.output_txt)
    
    # Check if input playlist exists
    if not os.path.exists(m3u8_path):
        print(f"Input playlist {m3u8_path} does not exist")
        sys.exit(1)
    
    # Run duplicate detection with specified options
    duplicates_found = find_duplicates_m3u8(m3u8_path, output_txt, args.include_info, args.search_format, args.group_size)
    
    # Print warning if -i is used
    if args.include_info and duplicates_found:
        print("Grouping flags disabled for Info output")
    
    # Print appropriate final message
    if duplicates_found:
        print(f"Duplicate tracks written to {output_txt}")
    else:
        print("No duplicate tracks found")
