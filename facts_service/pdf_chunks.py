from io import BytesIO

from pypdf import PdfReader

MAX_PDF_BYTES = 50 * 1024 * 1024
MAX_CHUNKS = 200
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def split_text(text: str) -> list[str]:
    cleaned = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not cleaned:
        return []
    if len(cleaned) <= CHUNK_SIZE:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + CHUNK_SIZE, length)
        if end < length:
            window = cleaned[start:end]
            break_at = -1
            for separator in ("\n\n", "\n", " "):
                index = window.rfind(separator)
                if index > CHUNK_OVERLAP:
                    break_at = index
                    break
            if break_at != -1:
                end = start + break_at
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        next_start = end - CHUNK_OVERLAP
        if next_start <= start:
            next_start = end
        start = next_start
    return chunks


def extract_chunks(data: bytes) -> list[tuple[int, str]]:
    reader = PdfReader(BytesIO(data))
    chunks: list[tuple[int, str]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        for piece in split_text(page.extract_text() or ""):
            chunks.append((page_number, piece))
            if len(chunks) > MAX_CHUNKS:
                return chunks
    return chunks
