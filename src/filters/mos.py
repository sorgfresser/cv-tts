from wvmos import get_wvmos
from src.parse.clip import Clip, Client
import logging
from tqdm import tqdm

model = get_wvmos(cuda=True)

logger = logging.getLogger(__name__)


def get_mos(clip: Clip) -> None:
    """
    Get the MOS of a clip and store it in the clip object

    :param clip: The clip to get the MOS of
    :return: None
    """
    try:
        mos = model.calculate_one(clip.filepath)
    except RuntimeError as e:
        logger.error("Error calculating MOS for %s: %s", clip.filepath, e)
        raise e
    if mos < 0:
        logger.warning(
            f"MOS for {clip.filepath} is negative: {mos}, you may want to check the audio file."
        )
    clip.mos = mos


def get_mos_for_clients(clients: dict[str, Client]) -> None:
    """
    Get the MOS for all clips in all clients

    :param clients: The clients to get the MOS for
    :return: None
    """
    for client in tqdm(clients.values()):
        clip_idx = 0
        while clip_idx < len(client.clips):
            try:
                get_mos(client.clips[clip_idx])
            except RuntimeError:
                logger.error("Skipping clip %s", client.clips[clip_idx].filepath)
                del client.clips[clip_idx]
                continue
            clip_idx += 1

        if len(client.clips) == 0:
            logger.warning(
                "Speaker %s has no clips with MOS, setting MOS to 0", client.client_id
            )
            client.mos = 0
            continue

        client.mos = sum(clip.mos for clip in client.clips) / len(
            client.clips
        )  # mean mos for client


def filter_clients_mos(
    clients: dict[str, Client], mos_threshold: float
) -> dict[str, Client]:
    return {
        key: client for key, client in clients.items() if client.mos >= mos_threshold
    }
