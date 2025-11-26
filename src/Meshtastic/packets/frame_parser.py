# frame_parser.py
def extract_frames(buffer: bytes, START1: int = 0x94, START2: int = 0xC3):
    frames = []
    working = bytearray(buffer)

    while len(working) >= 4:
        if working[0] != START1 or working[1] != START2:
            working = working[1:]
            continue

        frame_length = int.from_bytes(working[2:4], "big")
        total_length = 4 + frame_length

        if frame_length < 1 or frame_length > 4096 or len(working) < total_length:
            break

        frame = working[:total_length]
        frames.append(bytes(frame))
        working = working[total_length:]

    return {"frames": frames, "remainder": bytes(working)}
