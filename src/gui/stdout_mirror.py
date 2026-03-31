from queue import Queue


class StdoutMirror:
    def __init__(self, original_stream, message_queue: Queue[str]) -> None:
        self._original_stream = original_stream
        self._message_queue = message_queue

    def write(self, text: str) -> int:
        if not text:
            return 0
        if self._original_stream is not None:
            self._original_stream.write(text)
            self._original_stream.flush()

        gui_text = text.replace("\r", "\n")
        self._message_queue.put(gui_text)
        return len(text)

    def flush(self) -> None:
        if self._original_stream is not None:
            self._original_stream.flush()

    def writable(self) -> bool:
        return True