from dataclasses import dataclass
from pathlib import Path
from itertools import repeat


@dataclass
class Clip:
    filepath: Path
    duration_ms: int
    client_id: str
    sentence: str
    sentence_id: str
    sentence_domain: str
    up_votes: int
    down_votes: int
    age: str
    gender: str
    accents: str
    variant: str
    locale: str
    segment: str
    mos: float = -1

    def __str__(self):
        return (
            f"{self.filepath}\t{self.duration_ms}ms\t{self.client_id}\t{self.sentence}"
        )

    def to_tsv_train(self):
        return f"{self.client_id}\t{self.filepath.name}\t{self.sentence_id}\t{self.sentence}\t{self.sentence_domain}\t{self.up_votes}\t{self.down_votes}\t{self.age}\t{self.gender}\t{self.accents}\t{self.variant}\t{self.locale}\t{self.segment}"

    def to_tsv_duration(self):
        return f"{self.filepath.name}\t{self.duration_ms}"


@dataclass
class Client:
    client_id: str
    clips: list[Clip]
    mos: float = -1

    def __str__(self):
        return f"{self.client_id}\t{len(self.clips)}"


def clients_for_clips(clips: list[Clip]) -> dict[str, Client]:
    clients = {}
    for clip in clips:
        client_id = clip.client_id
        if client_id not in clients:
            clients[client_id] = Client(client_id, [])
        clients[client_id].clips.append(clip)
    return clients


def parse_clip(line: str, reference_dir: Path | None = None) -> Clip:
    parts = line.split("\t")
    return Clip(
        Path(parts[1]) if reference_dir is None else reference_dir / parts[1],
        -1,
        parts[0],
        parts[3],
        parts[2],
        parts[4],
        int(parts[5]),
        int(parts[6]),
        parts[7],
        parts[8],
        parts[9],
        parts[10],
        parts[11],
        parts[12],
    )


def parse_clips(lines: list[str], reference_dir: Path | None = None) -> dict[str, Clip]:
    return {
        str(clip.filepath.absolute()): clip
        for clip in map(parse_clip, lines, repeat(reference_dir))
    }


def add_durations(lines: list[str], clips: dict[str, Clip]) -> None:
    for line in lines:
        parts = line.split("\t")
        filepath = Path(parts[0])
        if str(filepath.absolute()) in clips:
            clips[str(filepath.absolute())].duration_ms = int(parts[1])


if __name__ == "__main__":
    with open("cv-corpus-17.0-2024-03-15/am/train.tsv", "r") as f:
        lines = f.readlines()
        lines.pop(0)
    clips = parse_clips(lines)
    with open("cv-corpus-17.0-2024-03-15/am/clip_durations.tsv", "r") as f:
        lines = f.readlines()
        lines.pop(0)
    add_durations(lines, clips)
    for clip in clips.values():
        print(clip)

    clients = clients_for_clips(list(clips.values()))
    for client in clients.values():
        print(client)
