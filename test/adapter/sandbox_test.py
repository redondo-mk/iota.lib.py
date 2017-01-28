# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota.adapter.sandbox import SandboxAdapter


class SandboxAdapterTestCase(TestCase):
  def test_regular_command(self):
    """
    Sending a non-sandbox command to the node.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_sandbox_command(self):
    """
    Sending a sandbox command to the node.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_regular_command_null_token(self):
    """
    Sending commands to a sandbox that doesn't require authorization.

    This is generally not recommended, but the sandbox node may use
    other methods to control access (e.g., listen only on loopback
    interface, use IP address whitelist, etc.).
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_error_token_wrong_type(self):
    """
    ``token`` is not a string.
    """
    with self.assertRaises(TypeError):
      # Nope; it has to be a unicode string.
      SandboxAdapter('https://localhost', b'not valid')

  def test_error_token_empty(self):
    """
    ``token`` is an empty string.
    """
    with self.assertRaises(ValueError):
      # If the node does not require authorization, use ``None``.
      SandboxAdapter('https://localhost', '')

  def test_error_poll_interval_null(self):
    """
    ``poll_interval`` is ``None``.

    The implications of allowing this are cool to think about...
    but not implemented yet.
    """
    with self.assertRaises(TypeError):
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', None)

  def test_error_poll_interval_wrong_type(self):
    """
    ``poll_interval`` is not an int or float.
    """
    with self.assertRaises(TypeError):
      # ``poll_interval`` must be an int.
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', 42.0)

  def test_error_poll_interval_too_small(self):
    """
    ``poll_interval`` is < 1.
    """
    with self.assertRaises(ValueError):
      SandboxAdapter('https://localhost', 'token', 0)
