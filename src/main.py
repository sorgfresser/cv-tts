import os
from argparse import ArgumentParser
from pathlib import Path
from src.parse.clip import parse_clips, add_durations, clients_for_clips
from src.filters.resample import mp3_to_wav, remove_silence
from src.filters.duration import filter_clips, filter_clients
from src.filters.mos import get_mos_for_clients, filter_clients_mos
import logging
from tqdm import tqdm

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGLEVEL)


def verify_dir(directory: Path) -> None:
    if not directory.exists():
        raise FileNotFoundError(f"{directory} does not exist")
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")


def verify_file(file: Path) -> None:
    if not file.exists():
        raise FileNotFoundError(f"{file} does not exist")
    if not file.is_file():
        raise IsADirectoryError(f"{file} is not a file")


if __name__ == "__main__":
    parser = ArgumentParser(
        description='Filtering the commonvoice dataset similarly to "CAN WE USE COMMON VOICE TO TRAIN A MULTI-SPEAKER TTS SYSTEM?"'
    )
    parser.add_argument(
        "cv_dir",
        type=str,
        help="Directory containing the commonvoice dataset files, i.e. train.tsv, clip_durations.tsv and clips/",
    )
    parser.add_argument(
        "output_dir", type=str, help="Output directory for the filtered dataset"
    )
    parser.add_argument(
        "--mos_threshold",
        type=float,
        default=3.0,
        help="Minimum MOS for a speaker to be included in the dataset, should be between 1.0 and 4.0",
    )
    args = parser.parse_args()
    # Assert user input is valid
    cv_dir = Path(args.cv_dir)
    verify_dir(cv_dir)
    train_tsv = cv_dir / "train.tsv"
    verify_file(train_tsv)
    durations_tsv = cv_dir / "clip_durations.tsv"
    verify_file(durations_tsv)
    clip_dir = cv_dir / "clips"
    verify_dir(clip_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    output_clip_dir = output_dir / "clips"
    output_clip_dir.mkdir(exist_ok=True)
    logger.info("Directories verified")

    # Read clips
    with train_tsv.open("r") as f:
        train_lines = f.readlines()
    with durations_tsv.open("r") as f:
        duration_lines = f.readlines()
    train_lines.pop(0)
    duration_lines.pop(0)
    logger.info("Files read")
    clips = parse_clips(train_lines, clip_dir)
    logger.info("Clips parsed, found %s clips", len(clips))
    add_durations(duration_lines, clips)
    logger.info("Durations added")

    # Filter clips, resample and remove silence
    clips = filter_clips(clips)
    logger.info("Clips filtered, %s clips remaining", len(clips))

    logger.info("Converting clips to wav")
    wav_clips = {
        str(clip.filepath.absolute()): mp3_to_wav(clip, output_clip_dir)
        for clip in tqdm(clips.values())
    }
    logger.info("Removing silence from clips")
    for clip in tqdm(wav_clips.values()):
        remove_silence(clip)

    # Get speakers and filter them
    clients = clients_for_clips(list(wav_clips.values()))
    logger.info("Found %s speakers", len(clients))
    clients = filter_clients(clients)
    logger.info("Filtered to %s speakers", len(clients))

    # Get MOS for speakers and filter them based on MOS
    logger.info("Obtaining MOS for speakers")
    get_mos_for_clients(clients)
    logger.info("MOS for speakers finished")
    clients = filter_clients_mos(clients, args.mos_threshold)
    logger.info("Filtered to %s speakers based on MOS", len(clients))

    # Store the remaining clips in similar tsv files
    output_train_tsv = output_dir / "train.tsv"
    output_durations_tsv = output_dir / "clip_durations.tsv"
    logger.info(
        "Storing clip info in %s and %s", output_train_tsv, output_durations_tsv
    )
    with output_train_tsv.open("w") as train_f, output_durations_tsv.open(
        "w"
    ) as duration_f:
        train_f.write(
            "client_id\tpath\tsentence_id\tsentence\tsentence_domain\tup_votes\tdown_votes\tage\tgender\taccents\tvariant\tlocale\tsegment\tduration_ms\n"
        )
        duration_f.write("clip\tduration[ms]\n")
        for client in clients.values():
            for clip in client.clips:
                train_f.write(clip.to_tsv_train() + '\n')
                duration_f.write(clip.to_tsv_duration() + '\n')
    logger.info("Done")
