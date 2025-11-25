import lz4.block

def decompress(buffer: bytes) -> bytes | None:
    """
    Attempt to decompress an LZ4 payload.
    Returns the decompressed bytes or None if decompression fails.
    """
    try:
        # In Python's lz4.block, we don't need to preallocate an output buffer.
        return lz4.block.decompress(buffer)
    except Exception as err:
        print("[decompress] Failed to decompress LZ4 payload:", err)
        return None
