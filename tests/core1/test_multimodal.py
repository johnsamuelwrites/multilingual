#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multimodal value type tests."""
# pylint: disable=missing-class-docstring

import pytest

from multilingualprogramming.runtime.multimodal_runtime import (
    AudioValue,
    DocumentValue,
    ImageValue,
    MultimodalPrompt,
    MultimodalValue,
    VideoValue,
)
from multilingualprogramming.runtime.ai_types import GenerateResult


# ===========================================================================
# ImageValue
# ===========================================================================

class TestImageValue:
    def test_default_mime(self):
        img = ImageValue(data=b"\x89PNG", source_path="test.png")
        assert img.mime_type == "image/png"

    def test_custom_mime(self):
        img = ImageValue(data=b"...", mime_type="image/jpeg")
        assert img.mime_type == "image/jpeg"

    def test_byte_size(self):
        img = ImageValue(data=b"abcdef")
        assert img.byte_size() == 6

    def test_data_url(self):
        img = ImageValue(data=b"PNG", mime_type="image/png")
        url = img.to_data_url()
        assert url.startswith("data:image/png;base64,")

    def test_repr_contains_mime(self):
        img = ImageValue(data=b"x", source_path="photo.jpg", mime_type="image/jpeg")
        assert "image/jpeg" in repr(img)


# ===========================================================================
# AudioValue
# ===========================================================================

class TestAudioValue:
    def test_default_mime(self):
        audio = AudioValue(data=b"RIFF")
        assert audio.mime_type == "audio/wav"

    def test_duration(self):
        audio = AudioValue(data=b"x", duration_seconds=3.5)
        assert audio.duration_seconds == 3.5

    def test_data_url(self):
        audio = AudioValue(data=b"WAV")
        url = audio.to_data_url()
        assert url.startswith("data:audio/wav;base64,")


# ===========================================================================
# VideoValue
# ===========================================================================

class TestVideoValue:
    def test_default_mime(self):
        video = VideoValue(data=b"MP4")
        assert video.mime_type == "video/mp4"

    def test_dimensions(self):
        video = VideoValue(data=b"x", width=1920, height=1080)
        assert video.width == 1920
        assert video.height == 1080


# ===========================================================================
# DocumentValue
# ===========================================================================

class TestDocumentValue:
    def test_default_mime(self):
        doc = DocumentValue(data=b"%PDF")
        assert doc.mime_type == "application/pdf"

    def test_title(self):
        doc = DocumentValue(data=b"%PDF", title="Annual Report")
        assert doc.title == "Annual Report"

    def test_repr_contains_title(self):
        doc = DocumentValue(data=b"x", title="Report")
        assert "Report" in repr(doc)


# ===========================================================================
# MultimodalPrompt
# ===========================================================================

class TestMultimodalPrompt:
    def test_add_text(self):
        p = MultimodalPrompt()
        p.add_text("Describe this:")
        assert p.to_text_repr() == "Describe this:"

    def test_add_image(self):
        p = MultimodalPrompt()
        p.add_text("What is in this image?")
        p.add(ImageValue(data=b"PNG", source_path="test.png"))
        text = p.to_text_repr()
        assert "Image" in text

    def test_add_document(self):
        p = MultimodalPrompt()
        p.add(DocumentValue(data=b"%PDF", title="Report"))
        text = p.to_text_repr()
        assert "Document" in text
        assert "Report" in text

    def test_modality_summary(self):
        p = MultimodalPrompt()
        p.add_text("hello")
        p.add(ImageValue(data=b"x"))
        p.add(ImageValue(data=b"y"))
        p.add(AudioValue(data=b"z"))
        summary = p.modality_summary()
        assert summary["text"] == 1
        assert summary["image"] == 2
        assert summary["audio"] == 1
        assert summary["video"] == 0

    def test_chaining(self):
        p = MultimodalPrompt()
        result = p.add_text("Step 1").add(ImageValue(data=b"x")).add_text("Step 2")
        assert result is p
        assert len(p.parts) == 3


# ===========================================================================
# GenerateResult
# ===========================================================================

class TestGenerateResult:
    def test_ok_when_value_present(self):
        r = GenerateResult(raw="42", value=42, declared_type="int")
        assert r.ok is True

    def test_not_ok_when_parse_error(self):
        r = GenerateResult(raw="bad", parse_error="could not parse", declared_type="int")
        assert r.ok is False

    def test_not_ok_when_no_value(self):
        r = GenerateResult(raw="", value=None)
        assert r.ok is False
