from src.parse.clip import Clip, Client

MAX_DURATION_MS = 16700  # 16.7 seconds, same as paper
MAX_SPEAKER_DURATION_MS = (
    36_000_000  # 10 hours, i.e. 10 * 60 * 60 * 1000 milliseconds, same as paper
)
MIN_SPEAKER_DURATION_MS = (
    1_200_000  # 20 minutes, i.e. 20 * 60 * 1000 milliseconds, same as paper
)


def longer_than(duration: int):
    return lambda x: x.duration_ms > duration


def filter_clips(clips: dict[str, Clip]) -> dict[str, Clip]:
    return {
        key: clip
        for key, clip in clips.items()
        if not longer_than(MAX_DURATION_MS)(clip)
    }


def client_duration(client: Client) -> int:
    return sum(clip.duration_ms for clip in client.clips)


def filter_clients(clients: dict[str, Client]) -> dict[str, Client]:
    clients = {
        key: client
        for key, client in clients.items()
        if MIN_SPEAKER_DURATION_MS < client_duration(client)
    }

    # Remove clips from clients if they exceed the maximum speaker duration
    for client in clients.values():
        client_dur = 0.0
        for clip in client.clips:
            if client_dur + clip.duration_ms > MAX_SPEAKER_DURATION_MS:
                client.clips = client.clips[: client.clips.index(clip)]
                break
            client_dur += clip.duration_ms
    return clients
