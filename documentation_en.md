# Documentation - spectroPy_render - https://nid.morgandemus.fr/

## Table of Contents
1. Introduction
2. GNU/Linux & Windows & MacOS
3. Generation Parameters
4. User Guide
5. CLI
6. Technical References

---

## Introduction

This tool generates high-resolution spectrograms with a detailed interface to configure it exactly as you wish.
It uses FFmpeg (showspectrumpic filter) for the final export and librosa/matplotlib for the interactive preview.

### Differences between preview and export
- **Interactive preview**: Fast calculation (60 seconds by default), navigation across the spectrogram, real-time modification of the settings.
- **FFmpeg export**: Publication quality, full audio, all parameters applied.

---

## GNU/Linux & Windows & MacOS
Initially designed and conceived on a GNU/Linux (Debian) system, the advantage of the Python3 language is that it allows for cross-platform execution.
It is therefore very important to respect the program's dependencies in order to use it properly:

**What you need:**
- **Python3**: https://www.python.org/downloads/
- **FFmpeg**: https://www.ffmpeg.org/
- **PIP command**: `pip install PyQt6 matplotlib librosa sounddevice numpy scipy`

*(Note: On Linux, it will be necessary to add `libportaudio2` for audio and the `libxcb-*` libraries for display; the `run.sh` script takes care of this)*

---

## Generation Parameters (by default)

### Size
- **Format**: 1920x1080 (width x height)
- **Resolution overview**:
  - **Default**: 1920x1080
  - **Fine analysis**: 3840x2160 (allows you to distinguish fine harmonics and temporal micro-structures)
  - **Fast processing**: 1280x720

### Display Mode
- **Options**: `combined` | `separate`
  - `combined`: Overlays all audio channels (mono or stereo) into a single spectrogram.
  - `separate`: Displays each channel on a distinct line.

### Color Palette
- **Options**: `fiery` | `rainbow` | `intensity` | `magma` | `viridis` | `cool` | `plasma` | `green` | `blue`
- **Perceptual impact**:
  - `fiery`: Black -> Red -> Yellow -> White.
  - `magma`: Black -> Red -> Yellow -> White.
  - `viridis`: Purple -> Green -> Yellow.
  - `rainbow`: Rainbow.
  - `intensity`: Black -> White.
- *(dev) FFmpeg -> Matplotlib correspondence table*:
  - `fiery` -> `afmhot`
  - `magma` -> `magma`
  - `viridis` -> `viridis`
  - `rainbow` -> `rainbow`
  - `intensity` -> `gray`

### Intensity Scale
- **Options**: `log` | `lin` | `sqrt` | `cbrt`
  - `log` (decibels - **RECOMMENDED**):
    - Formula: `dB = 20 x log10(amplitude)`
    - Dynamic range: 120-150 dB typical
  - `lin` (linear):
    - Displays raw amplitude (useful for synthetic signal analysis and calibration)
  - `sqrt` (square root):
    - Moderate dynamic compression (useful in the case of very high peaks)
  - `cbrt` (cube root):
    - Strong dynamic compression (to simultaneously visualize very loud and very quiet sounds)

### Frequency Scale
- **Options**: `log` | `lin`
  - `log`: Y-axis in logarithmic scale.
  - `lin` (linear): Y-axis in linear scale.

### Windowing (FFT - Window Function)
- **Options**: `hann` | `blackman` | `hamming` | `rect` | `bartlett` | `flattop` | `welch` | `nuttall`
- **Concept**: Reduces spectral leakage during the Fourier transform. (https://en.wikipedia.org/wiki/Fourier_transform)
  - `hann` (**RECOMMENDED**):
    - Optimal resolution/leakage compromise.
    - Main lobe width: average.
    - Side lobe attenuation: -31 dB.
  - `blackman`:
    - Best leakage attenuation (-58 dB).
    - To isolate pure notes and very close harmonics, but with slightly reduced frequency resolution.
  - `hamming`:
    - Similar to Hann but with a lower first side lobe.
  - `rect` (rectangular):
    - No window (rectangular box).
    - Maximum resolution but significant leakage (to be avoided unless you specifically need it).
  - `flattop`:
    - Very precise amplitude measurement.

### Advanced FFT Parameters (hardcoded):
- `n_fft = 2048`: FFT size (frequency resolution)
- `hop_length = 512`: Window overlap (temporal resolution)
- Ratio: 75% overlap (standard)

### Gain
- **Format**: 1.0 to 100.0 (multiplier)
- **Warning!**: Gain does not amplify the signal-to-noise ratio; it amplifies everything (signal + noise).

### Min/Max Frequency (Hz)
- **Format**: 0 (auto) or value in Hz
- **Min frequency**:
  - Example: 1000 Hz to ignore wind, infrasound, and low-frequency background noise.
  - Example: 500 Hz to focus on passerines.
- **Max frequency**:
  - Example: 12000 Hz for the typical band of passerines (0.5-12 kHz).
  - Example: 8000 Hz to filter out ultrasounds (bats, insects).
- Frequency bands by species: https://nid.morgandemus.fr/articles/ornitho_frequency_table.html

### Dynamic Range (dB)
- **Format**: 10 to 200 dBFS
- **dBFS** (decibels Full Scale): 0 dBFS = maximum digital level (saturation).

### Display Legend
- **Options**: Yes | No
  - **Yes**: Displays time (seconds) and frequency (Hz) axes. Displays the color bar with dB scale.
  - **No**: Image without annotations.

---

## User Guide

### Example of basic use
1. **Loading**: Your audio file (WAV, FLAC, MP3, OGG).
2. **Quick preview**: The first 60 seconds are displayed (configurable depending on your computer's resources).
3. **Setting parameters**:
   - Palette: `fiery` or `magma`
   - Frequency scale: `log`
   - Intensity scale: `log`
   - Dynamic range: 120-150 dB
   - Windowing: `hann` or `blackman`
4. **Listening**: Click on Play to listen to the audio.
5. **Export**: Click on "Generate final image".

### Examples by analysis type

**Complex songs (thrushes, blackbirds, warblers)**
- Size: 1920x1080
- Palette: `intensity`
- Frequency scale: `log`
- Dynamic range: 120-150 dB
- Windowing: `hann`
- Min frequency: 500 Hz
- Max frequency: 12000 Hz

**High-pitched songs (goldcrests, tits)**
- Frequency scale: `log`
- Min frequency: 2000 Hz
- Max frequency: 12000 Hz
- Palette: `intensity` (best contrast for high frequencies)

**Low-pitched songs (bitterns, owls, water hens)**
- Frequency scale: `log`
- Min frequency: 50 Hz
- Max frequency: 4000 Hz
- Dynamic range: 150 dB (often quiet sounds)

**Soundscapes (ecoacoustics)**
- Mode: `separate` (if stereo)
- Palette: `magma` (perceptually uniform)
- Dynamic range: 150-180 dB
- Intensity scale: `log`
- Size: 3840x2160

**Fine harmonics (spectral analysis)**
- Windowing: `blackman` (best separation)
- Size: 3840x2160
- Frequency scale: `lin` (if harmonics are equidistant)
- Palette: `intensity` (precise grayscale levels)

### Pitfalls to avoid
- **Dynamic range too low (< 80 dB)**: Loss of information on quiet songs.
- **Linear frequency scale**: Impossible to see bass and treble simultaneously.
- **Rectangular windowing**: Significant spectral leakage, visual artifacts.
- **Excessive gain (> 10)**: Saturation of the spectrogram, loss of detail.
- **No legend**: Purely aesthetic image.

---

## Automation in Command Line (CLI) (for developers)

### Basic syntax
`python spectroPy_render.py --input file.wav --output output.png [OPTIONS]`
also possible with:
`python spectroPy_render.py -i file.wav -o output.png [OPTIONS]`

### Examples
**Example 1: Fast generation (default parameters)**
`python spectroPy_render.py -i bird.wav -o spectrogram.png`

**Example 2: Optimal bioacoustic configuration**
`python spectroPy_render.py -i blackbird_song.wav -o blackbird_spectrogram.png --size 1920x1080 --color intensity --scale log --fscale log --win-func hann --drange 150 --start 500 --stop 12000 --legend`

**Example 3: High-frequency analysis**
`python spectroPy_render.py -i goldcrest.wav -o goldcrest_HF.png --color viridis --fscale log --start 4000 --stop 12000 --drange 120`

**Example 4: Ecoacoustics**
`python spectroPy_render.py -i soundscape.wav -o soundscape_4K.png --size 3840x2160 --mode separate --color magma --drange 180 --win-func blackman`

**Example 5: Batch processing (bash)**
```bash
#!/bin/bash
# Mass generation script
for file in ./recordings/*.wav; do
    base_name=$(basename "$file" .wav)
    python spectroPy_render.py -i "$file" -o "./spectrograms/${base_name}.png" --color intensity --fscale log --drange 150 --legend
    echo "Creation: ${base_name}.png"
done

**Example 6: Complete pipeline with native FFmpeg**
ffmpeg -i input.wav -af "highpass=f=500, lowpass=f=12000" -f wav - | ffmpeg -i - -lavfi "showspectrumpic=size=1920x1080:color=fiery:scale=log:fscale=log:drange=150" -y output.png

### All available CLI options

Mandatory options:
-i, --input TEXT          Input audio file (WAV, FLAC, MP3, OGG)
-o, --output TEXT         Output image file (PNG)

Size options:
--size TEXT               Resolution (default: 1920x1080)
  Ex: 1280x720, 3840x2160

Display options:
--mode TEXT               combined | separate (default: combined)
--color TEXT              fiery | rainbow | intensity | magma | viridis | cool | plasma | green | blue (default: fiery)

Scale options:
--scale TEXT              log | lin | sqrt | cbrt (default: log)
--fscale TEXT             log | lin (default: log)

Processing options:
--win-func TEXT           hann | blackman | hamming | rect | bartlett | flattop | welch | nuttall (default: hann)
--gain FLOAT              Amplification 0.1-100.0 (default: 1.0)

Frequency options:
--start INTEGER           Min frequency in Hz, 0=auto (default: 0)
--stop INTEGER            Max frequency in Hz, 0=auto (default: 0)

Quality options:
--drange INTEGER          Dynamic range 10-200 dB (default: 120)

Annotation options:
--legend                  Display the legend (default: active)
--no-legend               Hide the legend

Help:
--help                    Display this help and exit

## Technical References

### Official documentation
- **FFmpeg showspectrumpic**: https://ffmpeg.org/ffmpeg-filters.html#showspectrumpic
- **CloudACM - FFmpeg Tutorial**: https://www.cloudacm.com/?p=3105
- **librosa**: https://librosa.org/doc/latest/
- **Matplotlib**: https://matplotlib.org/stable/contents.html

### Bioacoustic resources
- **Cornell Lab of Ornithology**: https://www.birds.cornell.edu/
- **Xeno-canto** (bird song database): https://xeno-canto.org/

### Additional technical specifications

**Input formats:**
- WAV (PCM, float32)
- FLAC (lossless)
- MP3 (MPEG-1/2 Layer 3)
- OGG Vorbis
- AIFF
- M4A/AAC

**Output specifications:**
- **Format**: PNG (24-bit RGB)
- **Max resolution**: Limited by RAM memory
- **Color space**: sRGB
