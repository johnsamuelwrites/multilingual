#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Source reader with position tracking for the lexer."""


class SourceReader:
    """
    Wraps a source string with character-by-character reading
    and position tracking.
    """

    def __init__(self, source):
        """
        Initialize the reader.

        Parameters:
            source (str): The source code string
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def peek(self):
        """
        Look at the current character without consuming it.

        Returns:
            str: Current character, or empty string if at end
        """
        if self.is_at_end():
            return ""
        return self.source[self.pos]

    def peek_ahead(self, offset=1):
        """
        Look ahead by offset characters without consuming.

        Returns:
            str: Character at offset, or empty string if beyond end
        """
        idx = self.pos + offset
        if idx >= len(self.source):
            return ""
        return self.source[idx]

    def advance(self):
        """
        Consume and return the current character.

        Returns:
            str: The consumed character, or empty string if at end
        """
        if self.is_at_end():
            return ""
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def match(self, expected):
        """
        Consume the current character if it matches expected.

        Parameters:
            expected (str): The expected character

        Returns:
            bool: True if matched and consumed
        """
        if self.is_at_end() or self.source[self.pos] != expected:
            return False
        self.advance()
        return True

    def is_at_end(self):
        """
        Check if we've reached the end of the source.

        Returns:
            bool: True if at end
        """
        return self.pos >= len(self.source)
