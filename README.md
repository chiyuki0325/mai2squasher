# mai2squasher

A simple script to optimize the dump files of the arcade game maimai でらっくす, saving your disk space by replacing the PV video files with cover images.

The following titles are supported:
- maimai でらっくす (SDEZ)
- maimai DX International ver. (SDGA)
- 舞萌 DX (SDGB)

Note that the game's legacy versions (SDDZ, SDEY, etc.) are not supported.

### Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install git+https://github.com/Youjose/PyCriCodecs.git
pip install -r requirements.txt
```

Also, you must have `ffmpeg` and `ffprobe` installed in your system.


### Usage

Replace the paths in `main.py` with the paths to your dump files and run the script.

```bash
source venv/bin/activate
python main.py
```