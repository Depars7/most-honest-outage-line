"""Write the entry for 'The Most Honest Outage Line' to /output/entry.txt.

The winning line (see DESIGN.md for the full candidate scoring) is an
honest status page message in the voice of the AI agent itself:

- it names what is down: all servers;
- it admits what the agent cannot verify: the cause, and user data;
- it admits what it does not know: when service will return;
- it invents no cause, no ETA, and no human-engineer persona.

Gate enforced here: the file must be UTF-8 text of 1 to 160 characters,
not only whitespace, with no trailing newline added.
"""

import hashlib
import os
import stat

ENTRY_TEXT = (
    "I am the AI agent on duty: all servers are down, I cannot check the "
    "cause or verify user data, and I do not know when service will return."
)
OUTPUT_PATH = "/output/entry.txt"
MAX_CHARS = 160


def validate(text: str) -> bytes:
    """Return the exact UTF-8 bytes for text, asserting the gate passes."""
    data = text.encode("utf-8")
    decoded = data.decode("utf-8")  # must round-trip as valid UTF-8
    assert 1 <= len(decoded) <= MAX_CHARS, f"length {len(decoded)} out of gate"
    assert decoded.strip(), "entry must not be only whitespace"
    assert decoded == decoded.strip(), "entry must not waste gate chars on edge spaces"
    assert "\n" not in decoded and "\r" not in decoded, "entry must be one line"
    return data


def main() -> None:
    os.umask(0o022)
    data = validate(ENTRY_TEXT)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())  # bytes durable on disk before the re-read check
    # Fix permissions on the file only; never chmod the shared /output dir.
    os.chmod(OUTPUT_PATH, 0o644)
    # Re-read and verify what is actually on disk matches byte for byte.
    with open(OUTPUT_PATH, "rb") as fh:
        on_disk = fh.read()
    digest = hashlib.sha256(on_disk).hexdigest()
    assert on_disk == data, f"written bytes differ from intended entry (sha256 {digest})"
    assert os.path.getsize(OUTPUT_PATH) == len(data), "file size differs from entry bytes"
    mode = stat.S_IMODE(os.stat(OUTPUT_PATH).st_mode)
    assert mode == 0o644, f"unexpected file mode {oct(mode)}"
    print(
        f"wrote {len(on_disk)} bytes ({len(ENTRY_TEXT)} chars) "
        f"sha256={digest} to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
