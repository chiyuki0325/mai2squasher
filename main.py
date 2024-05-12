from pathlib import Path
from xml.dom import minidom
import subprocess
import math
import shutil
import msg
import UnityPy
from wannacri import usm
from PyCriCodecs import acb

# mai2squasher by chiyuki0325

# ----------------------------------
MAI2_A000_DIR = Path('/home/chiyuki/SDGB/Package/Sinmai_Data/StreamingAssets/A000')
MAI2_OPTION_DIR = Path('/home/chiyuki/SDGB/Package/option')

# Temporary directory for extracting files,
# must be empty, writable and have ~20MB of free space.
TMP_DIR = Path('/tmp/mai2squasher')

# CriWare encryption key of the game.
MAI2_CRIWARE_KEY = 9170825592834449000
# ----------------------------------

# Check if the paths are valid.
if not MAI2_A000_DIR.exists() or not (MAI2_A000_DIR / "music").exists():
    msg.error(f"Invalid path: {MAI2_A000_DIR} (not found or missing music directory).")
    exit(1)
TMP_DIR.mkdir(exist_ok=True, parents=True)

msg.ask(f"Are you sure to remove all the PV files from {MAI2_A000_DIR.parent.parent.parent}? (y/n)")
if input().lower() != "y":
    msg.error("Operation cancelled.")
    exit(1)

msg.msg("Converting PV files...")
counter = 0
original_size = 0
new_size = 0


def process_dir(mai2_resource_dir):
    global counter, original_size, new_size
    for music_xml in (mai2_resource_dir / "music").glob("*/*.xml"):
        document = minidom.parse(music_xml.open('r')).documentElement

        movie_id = document.getElementsByTagName('artistName')[0].getElementsByTagName('id')[0].firstChild.nodeValue
        movie_id = movie_id.zfill(6)
        movie_path = mai2_resource_dir / "MovieData" / f"{movie_id}.dat"
        if not movie_path.exists():
            movie_path = MAI2_A000_DIR / "MovieData" / f"{movie_id}.dat"
        jacket_path = mai2_resource_dir / "AssetBundleImages" / "jacket" / f"ui_jacket_{movie_id}.ab"
        if not jacket_path.exists():
            jacket_path = MAI2_A000_DIR / "AssetBundleImages" / "jacket" / f"ui_jacket_{movie_id}.ab"

        if movie_path.exists() and jacket_path.exists() and movie_path.stat().st_size > 1048576:
            original_size += movie_path.stat().st_size

            # Show progress
            song_name = document.getElementsByTagName('name')[0].getElementsByTagName('str')[0].firstChild.nodeValue
            song_artist = document.getElementsByTagName('artistName')[0].getElementsByTagName('str')[
                0].firstChild.nodeValue
            msg.msg2(f"{song_name} by {song_artist} (#{movie_id})")

            # Extract song cover
            jacket_output_path = TMP_DIR / f"{movie_id}.png"
            unity = UnityPy.load(open(jacket_path, 'rb'))
            for obj in unity.objects:
                if obj.type.name == 'Sprite':
                    obj.read().image.save(jacket_output_path)

            if not jacket_output_path.exists():
                msg.error(f"Failed to extract cover image for {song_name} by {song_artist} (#{movie_id}).")

            # Extract song sound data and get duration
            acb_path = mai2_resource_dir / "SoundData" / f"music{movie_id}.acb"
            if not acb_path.exists():
                acb_path = MAI2_A000_DIR / "SoundData" / f"music{movie_id}.acb"
            acb_output_dir = TMP_DIR / f"{movie_id}_acb"
            acb_output_dir.mkdir(exist_ok=True)
            acb.ACB(str(acb_path)).extract(
                dirname=str(acb_output_dir),
                decode=False
            )
            duration = 0
            for hca_file in acb_output_dir.glob("*.hca"):
                duration = math.ceil(float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                     "default=noprint_wrappers=1:nokey=1", str(hca_file)],
                    stdout=subprocess.PIPE
                ).stdout.decode()))
                hca_file.unlink()
                break
            acb_output_dir.rmdir()

            # Convert the cover image to vp9 video
            ivf_output_path = TMP_DIR / f"{movie_id}.ivf"
            subprocess.run(
                [
                    "ffmpeg",
                    "-r", "1",
                    "-loop", "1",
                    "-i", str(jacket_output_path),
                    "-c:v", "libvpx-vp9",
                    "-t", str(duration),
                    "-pix_fmt", "yuv420p",
                    "-vf", "scale=1080:1080,scale=out_color_matrix=smpte170m,format=yuv420p",
                    "-colorspace", "smpte170m",
                    "-r", "1",
                    "-row-mt", "1",
                    "-tile-rows", "2",
                    "-tile-columns", "2",
                    str(ivf_output_path)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            jacket_output_path.unlink()

            # Encrypt the vp9 video to usm
            usm_output_path = TMP_DIR / f"{movie_id}.dat"
            usm_stream = usm.Usm(
                videos=[usm.Vp9(filepath=str(ivf_output_path))],
                key=MAI2_CRIWARE_KEY
            )

            with open(usm_output_path, 'wb') as f:
                for packet in usm_stream.stream(mode=usm.OpMode.ENCRYPT):
                    f.write(packet)
            ivf_output_path.unlink()
            new_size += usm_output_path.stat().st_size

            # Replace the original movie file
            movie_path.unlink()
            shutil.move(usm_output_path, movie_path)

            counter += 1


process_dir(MAI2_A000_DIR)
for option_dir in MAI2_OPTION_DIR.glob("*"):
    process_dir(option_dir)

original_mb = (original_size / 1024 / 1024).__round__(2)
new_mb = (new_size / 1024 / 1024).__round__(2)

msg.msg(
    f"Removed {counter} PV files, {original_mb}MB -> {new_mb}MB (saved {(original_mb - new_mb).__round__(2)}MB)."
)
TMP_DIR.rmdir()
