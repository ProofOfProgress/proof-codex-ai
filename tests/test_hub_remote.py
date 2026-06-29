"""Tests for hub auto-connect helpers."""

from __future__ import annotations

import os
from unittest import mock

from shorts_bot import hub_remote


def test_secrets_configured_all_present():
    with mock.patch.dict(
        os.environ,
        {
            "HUB_SSH_HOST": "100.1.2.3",
            "HUB_SSH_USER": "isaac",
            "HUB_SSH_PRIVATE_KEY": "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----\n",
        },
        clear=False,
    ):
        assert hub_remote.secrets_configured() is True


def test_secrets_configured_missing_host():
    with mock.patch.dict(
        os.environ,
        {"HUB_SSH_USER": "isaac", "HUB_SSH_PRIVATE_KEY": "key"},
        clear=True,
    ):
        assert hub_remote.secrets_configured() is False


def test_tailscale_auth_accepts_talescale_typo():
    with mock.patch.dict(os.environ, {"TALESCALE_AUTH_KEY": "tskey-auth-test"}, clear=True):
        assert hub_remote.tailscale_auth_configured() is True


def test_tailscale_auth_prefers_correct_name():
    with mock.patch.dict(
        os.environ,
        {"TAILSCALE_AUTH_KEY": "tskey-auth-test", "TALESCALE_AUTH_KEY": "other"},
        clear=True,
    ):
        assert hub_remote.tailscale_auth_configured() is True


def test_ensure_connected_skips_without_secrets():
    with mock.patch.dict(os.environ, {}, clear=True):
        assert hub_remote.ensure_connected(quiet=True) is False
