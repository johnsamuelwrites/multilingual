#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 multimodal runtime.

Provides first-class value types for image, audio, video, and document
modalities, plus helpers for building multimodal prompts.

These types are usable directly in ``prompt`` and ``generate`` expressions:

    let caption = prompt @claude-sonnet: image_val + " — describe this image"
    let answer  = generate @claude-sonnet: [document_val, query] -> Invoice

Design
------
All multimodal values carry their raw bytes and a declared MIME type.
The AI runtime is responsible for encoding them correctly for each provider
(e.g. base64 data URLs for vision APIs).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class MultimodalValue:
    """Base class for all multimodal values."""

    data: bytes = field(default=b"", repr=False)
    mime_type: str = ""
    source_path: str = ""          # optional, for provenance
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_data_url(self) -> str:
        """Return a base64 data URL suitable for embedding in a JSON prompt."""
        b64 = base64.b64encode(self.data).decode("ascii")
        return f"data:{self.mime_type};base64,{b64}"

    def byte_size(self) -> int:
        """Return the number of bytes in this value's data."""
        return len(self.data)

    @classmethod
    def from_path(cls, path: str | Path, mime_type: str = "") -> "MultimodalValue":
        """Load a multimodal value from a file path."""
        p = Path(path)
        data = p.read_bytes()
        return cls(data=data, mime_type=mime_type, source_path=str(p))


# ---------------------------------------------------------------------------
# Image
# ---------------------------------------------------------------------------

@dataclass
class ImageValue(MultimodalValue):
    """First-class image value.  MIME type defaults to 'image/png'."""

    width: int = 0
    height: int = 0

    def __post_init__(self):
        if not self.mime_type:
            self.mime_type = "image/png"

    @classmethod
    def from_path(cls, path: str | Path, mime_type: str = "image/png") -> "ImageValue":
        p = Path(path)
        data = p.read_bytes()
        return cls(data=data, mime_type=mime_type, source_path=str(p))

    def __repr__(self) -> str:
        return (
            f"ImageValue(mime={self.mime_type!r}, "
            f"size={self.byte_size()}B, "
            f"source={self.source_path!r})"
        )


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

@dataclass
class AudioValue(MultimodalValue):
    """First-class audio value.  MIME type defaults to 'audio/wav'."""

    duration_seconds: float = 0.0
    sample_rate: int = 0

    def __post_init__(self):
        if not self.mime_type:
            self.mime_type = "audio/wav"

    @classmethod
    def from_path(cls, path: str | Path, mime_type: str = "audio/wav") -> "AudioValue":
        p = Path(path)
        data = p.read_bytes()
        return cls(data=data, mime_type=mime_type, source_path=str(p))

    def __repr__(self) -> str:
        return (
            f"AudioValue(mime={self.mime_type!r}, "
            f"size={self.byte_size()}B, "
            f"duration={self.duration_seconds:.1f}s)"
        )


# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------

@dataclass
class VideoValue(MultimodalValue):
    """First-class video value.  MIME type defaults to 'video/mp4'."""

    duration_seconds: float = 0.0
    frame_rate: float = 0.0
    width: int = 0
    height: int = 0

    def __post_init__(self):
        if not self.mime_type:
            self.mime_type = "video/mp4"

    @classmethod
    def from_path(cls, path: str | Path, mime_type: str = "video/mp4") -> "VideoValue":
        p = Path(path)
        data = p.read_bytes()
        return cls(data=data, mime_type=mime_type, source_path=str(p))

    def __repr__(self) -> str:
        return (
            f"VideoValue(mime={self.mime_type!r}, "
            f"size={self.byte_size()}B, "
            f"duration={self.duration_seconds:.1f}s)"
        )


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

@dataclass
class DocumentValue(MultimodalValue):
    """First-class document value (PDF, DOCX, etc.).

    MIME type defaults to 'application/pdf'.
    """

    page_count: int = 0
    title: str = ""

    def __post_init__(self):
        if not self.mime_type:
            self.mime_type = "application/pdf"

    @classmethod
    def from_path(
        cls, path: str | Path, mime_type: str = "application/pdf"
    ) -> "DocumentValue":
        p = Path(path)
        data = p.read_bytes()
        return cls(data=data, mime_type=mime_type, source_path=str(p))

    def __repr__(self) -> str:
        return (
            f"DocumentValue(mime={self.mime_type!r}, "
            f"size={self.byte_size()}B, "
            f"pages={self.page_count}, "
            f"title={self.title!r})"
        )


# ---------------------------------------------------------------------------
# MultimodalPrompt — assembles mixed-modality prompt content
# ---------------------------------------------------------------------------

@dataclass
class MultimodalPrompt:
    """A prompt that mixes text with multimodal values.

    Each part is either a plain string or a MultimodalValue.
    The runtime serialises the parts into the format expected by the provider.

    Usage::

        prompt = MultimodalPrompt()
        prompt.add_text("Describe this image:")
        prompt.add(image_val)
        result = AIRuntime.prompt(model, prompt.to_text_repr())
    """

    parts: list[str | MultimodalValue] = field(default_factory=list)

    def add(self, value: MultimodalValue) -> "MultimodalPrompt":
        """Append a multimodal value part and return self for chaining."""
        self.parts.append(value)
        return self

    def add_text(self, text: str) -> "MultimodalPrompt":
        """Append a plain text part and return self for chaining."""
        self.parts.append(text)
        return self

    def to_text_repr(self) -> str:
        """Return a plain-text representation (for providers that support text only)."""
        out = []
        for part in self.parts:
            if isinstance(part, str):
                out.append(part)
            elif isinstance(part, ImageValue):
                out.append(f"[Image: {part.source_path or part.mime_type}]")
            elif isinstance(part, AudioValue):
                dur = f"{part.duration_seconds:.1f}s " if part.duration_seconds else ""
                out.append(f"[Audio: {dur}{part.source_path or part.mime_type}]")
            elif isinstance(part, VideoValue):
                dur = f"{part.duration_seconds:.1f}s " if part.duration_seconds else ""
                out.append(f"[Video: {dur}{part.source_path or part.mime_type}]")
            elif isinstance(part, DocumentValue):
                title = f" '{part.title}'" if part.title else ""
                out.append(f"[Document{title}: {part.source_path or part.mime_type}]")
            else:
                out.append(repr(part))
        return "\n".join(out)

    def modality_summary(self) -> dict[str, int]:
        """Return a count of each modality type in this prompt."""
        counts: dict[str, int] = {"text": 0, "image": 0, "audio": 0, "video": 0, "document": 0}
        for part in self.parts:
            if isinstance(part, str):
                counts["text"] += 1
            elif isinstance(part, ImageValue):
                counts["image"] += 1
            elif isinstance(part, AudioValue):
                counts["audio"] += 1
            elif isinstance(part, VideoValue):
                counts["video"] += 1
            elif isinstance(part, DocumentValue):
                counts["document"] += 1
        return counts
