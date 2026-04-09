"""Module to clean audio clips"""

import logging
import os
import glob
from typing import Tuple

from audio_separator.separator import Separator
import onnxruntime as ort
import soundfile as sf
import numpy as np

# This model is a BS ReFormer model trained specifically to
# separate vocals from instrumental backgrounds.
SEPARATION_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"


def _log_onnx_providers() -> None:
    """Log available ONNX providers so runtime device choice is visible."""
    providers = ort.get_available_providers()
    logging.info("ONNX Runtime providers: %s", providers)
    if "CUDAExecutionProvider" not in providers:
        logging.warning(
            "CUDAExecutionProvider is unavailable; audio separation will run on CPU. "
            "Install a compatible onnxruntime-gpu build and verify CUDA libraries."
        )


def _resolve_stem_path(stem_file: str, output_dir: str) -> str:
    """Return the first existing path for a reported stem file."""
    candidates = [
        stem_file,
        os.path.join(output_dir, stem_file),
        os.path.join(output_dir, os.path.basename(stem_file)),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[1]


def _fallback_find_vocals(output_dir: str, input_filepath: str) -> str:
    """Find a likely vocals stem file if reported stem paths are stale or mismatched."""
    source_base = os.path.splitext(os.path.basename(input_filepath))[0]
    patterns = [
        os.path.join(output_dir, f"{source_base}*(Vocals)*.wav"),
        os.path.join(output_dir, "*(Vocals)*.wav"),
    ]

    candidates = []
    for pattern in patterns:
        candidates.extend(glob.glob(pattern))

    if not candidates:
        return None

    # Most recently modified vocals file is the best fallback guess.
    return max(candidates, key=os.path.getmtime)

def _prep_audio(input_filepath: str, output_dir: str) -> Tuple[str, int]:
    """Helper method to check if an audio file has more than 2 audio channels
    and if it does, to downmix those channels and create a processed temporary
    file. It also checks if a file is less than 10 seconds long and if it is,
    to add silence to the end of the file.

    Args:
        input_filepath (str): The input audio filepath

    Returns:
        str: The processed temporary filepath, or the regular filepath.
        int: The original length of the audio clip.
    """

    # Get audio data
    data, samplerate = sf.read(input_filepath)
    samples, channels = data.shape

    original_length = samples

    # Calcule clip duration
    duration = samples / samplerate

    processed = False

    # If input file has more than 2 audio channels
    if channels > 2:
        processed = True

        # Downmix the channels to 1 channel
        data = data.mean(axis=1)

        # Set channels to 1
        channels = 1

    # If input file is shorter than 10 seconds
    if duration < 10:

        # Calculate 10 seconds in samples
        target_samples = int(10 * samplerate)

        # Calculate the difference between target and source
        padding = target_samples - len(data)

        # If padding is needed
        if padding > 0:
            processed = True
            # If there is only one audio channel
            if channels == 1:
                # Generate required silence
                silence = np.zeros(padding)
            else:
                # Generate required silence
                silence = np.zeros((padding, channels))
            data = np.concatenate((data, silence))

    if processed is True:
        temporary_file = os.path.join(
            output_dir,
            f"temp_{os.path.basename(input_filepath)}"
        )

        # Write result to file
        sf.write(temporary_file, data, samplerate)

        # Return that temporary file
        return temporary_file, original_length

    # Else, return regular file and original length
    return input_filepath, original_length

def _get_vocals(input_filepath: str, output_dir: str) -> str:
    """Method to seperate input audio file into stems,
    take the vocal stem, and return the filepath of the result.

    Args:
        input_file (str): The input audio filepath
        output_dir (str): The output directory

    Returns:
        str: The result filepath
    """

    _log_onnx_providers()

    # Create Separator objects with logging level set to ERROR and output format to WAV
    separator = Separator(log_level=logging.ERROR, output_dir=output_dir, output_format="wav")

    # Load AI Model
    separator.load_model(SEPARATION_MODEL)

    # Separate input file into vocal stem and instrumental stem files
    stem_files = separator.separate(input_filepath)

    resolved_stems = [_resolve_stem_path(stem, output_dir) for stem in stem_files]
    vocals_source_path = None

    # Find the vocals stem among resolved paths.
    for stem_path in resolved_stems:
        if "(Vocals)" in os.path.basename(stem_path):
            vocals_source_path = stem_path
            break

    # Fallback: discover the newest vocals file in the output folder.
    if vocals_source_path is None or not os.path.exists(vocals_source_path):
        vocals_source_path = _fallback_find_vocals(output_dir, input_filepath)

    if vocals_source_path is None or not os.path.exists(vocals_source_path):
        logging.critical("There was no vocal file to return! stem_files=%s", stem_files)
        return None

    # Remove other stem files if they exist.
    for stem_path in resolved_stems:
        if stem_path != vocals_source_path and os.path.exists(stem_path):
            os.remove(stem_path)

    vocals_filepath = os.path.join(output_dir, "vocals_" + os.path.basename(input_filepath))
    if os.path.exists(vocals_filepath):
        os.remove(vocals_filepath)
    os.rename(vocals_source_path, vocals_filepath)
    return vocals_filepath

def process_file(input_filepath: str, output_dir: str):
    """Method to process a single audio file."""

    original_filename = os.path.basename(input_filepath)

    # Prepare audio file
    prepped_filepath, original_length = _prep_audio(input_filepath, output_dir)

    # Get Vocals from audio file
    vocals_filepath = _get_vocals(prepped_filepath, output_dir)
    if not vocals_filepath:
        raise FileNotFoundError(
            f"Vocal stem file was not found for input: {input_filepath}"
        )

    # Remove temporary processed file if it exists
    if input_filepath != prepped_filepath:
        os.remove(prepped_filepath)

    # show that the file is finished
    final_filepath = os.path.join(output_dir, "CLEAN_" + original_filename)
    os.rename(vocals_filepath, final_filepath)

    # Trim silence padding
    if original_length:
        data, sr = sf.read(final_filepath)
        sf.write(final_filepath, data[:original_length], sr)

def clean(base_dir: str):
    """The main method of this module."""

    input_dir = base_dir + "clips"
    output_dir = base_dir + "cleaned_clips"

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    logging.basicConfig(level=logging.INFO)

    files = os.listdir(input_dir)
    total = len(files)

    for i, filename in enumerate(files):
        print(f"{i}/{total} Processing {filename}")
        process_file(os.path.join(input_dir, filename), output_dir)
    print("Done!")