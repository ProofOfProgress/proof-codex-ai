"""Bubble wrap scheduler — account pick, subject rotation, tick flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.tiktok_shop.bubble_scheduler import (
    bubble_tick,
    pick_bubble_account,
    pick_bubble_subject,
    run_bubble_post_for_account,
)


def _bubble_account(**overrides: object) -> ShopAccount:
    base = {
        "id": "bubble_test",
        "label": "Test Bubble",
        "track": "bubble_safe",
        "phone_hub_slot": "phone_1",
        "daily_limit": 4,
        "enabled": True,
        "post_via": "zernio",
        "zernio_account_id": "zernio123",
    }
    base.update(overrides)
    return ShopAccount(**base)


def test_pick_bubble_subject_from_default_list():
    from shorts_bot.tiktok_shop.bubble_batch import DEFAULT_BUBBLE_SUBJECTS

    a = pick_bubble_subject("bubble_gspgsgsorip1")
    b = pick_bubble_subject("bubble_isaac")
    assert a in DEFAULT_BUBBLE_SUBJECTS
    assert b in DEFAULT_BUBBLE_SUBJECTS


@patch("shorts_bot.tiktok_shop.bubble_scheduler.bubble_accounts")
@patch("shorts_bot.tiktok_shop.bubble_scheduler.remaining_today", return_value=2)
@patch("shorts_bot.tiktok_shop.bubble_scheduler.posts_today", return_value=0)
@patch("shorts_bot.tiktok_shop.bubble_scheduler.seconds_until_next_post", return_value=0)
@patch("shorts_bot.tiktok_shop.bubble_scheduler.pending_hub_jobs_for", return_value=0)
def test_pick_bubble_account_lowest_posts_first(
    _pending,
    _wait,
    _posts,
    _remaining,
    mock_accounts,
):
    acct_a = _bubble_account(id="bubble_a", daily_limit=10)
    acct_b = _bubble_account(id="bubble_b", daily_limit=10)
    mock_accounts.return_value = [acct_a, acct_b]

    with patch("shorts_bot.tiktok_shop.bubble_scheduler.posts_today", side_effect=lambda aid: 1 if aid == "bubble_a" else 0):
        picked = pick_bubble_account()
    assert picked is not None
    assert picked.id == "bubble_b"


@patch("shorts_bot.tiktok_shop.bubble_scheduler.pick_bubble_account")
def test_bubble_tick_dry_run(mock_pick):
    mock_pick.return_value = _bubble_account()
    result = bubble_tick(confirm=False)
    assert result.action == "dry_run"
    assert "would post" in result.detail
    assert result.subject


@patch("shorts_bot.tiktok_shop.bubble_scheduler.run_bubble_post_for_account")
@patch("shorts_bot.tiktok_shop.bubble_scheduler.pick_bubble_account")
def test_bubble_tick_confirm_delegates(mock_pick, mock_run):
    acct = _bubble_account()
    mock_pick.return_value = acct
    mock_run.return_value = MagicMock(
        account_id=acct.id,
        action="posted",
        detail="ok",
        subject="frog",
        post_id="p1",
        hub_job_id="j1",
    )
    result = bubble_tick(confirm=True)
    assert result.action == "posted"
    mock_run.assert_called_once()


@patch("shorts_bot.tiktok_shop.bubble_scheduler.enqueue_job")
@patch("shorts_bot.tiktok_shop.bubble_scheduler.log_post")
@patch("shorts_bot.tiktok_shop.bubble_scheduler.post_bubble_wrap_carousel", return_value=(True, "ok", "post99"))
@patch("shorts_bot.tiktok_shop.bubble_scheduler.generate_bubble_wrap_slides")
@patch("shorts_bot.tiktok_shop.bubble_scheduler.pending_hub_jobs_for", return_value=0)
def test_run_bubble_post_success(mock_pending, mock_slides, mock_post, mock_log, mock_enqueue):
    slides = MagicMock(slide1="/tmp/s1.jpg", slide2="/tmp/s2.jpg")
    mock_slides.return_value = slides
    mock_enqueue.return_value = MagicMock(id="job42")

    acct = _bubble_account()
    result = run_bubble_post_for_account(acct, subject="frog")

    assert result.action == "posted"
    assert result.post_id == "post99"
    assert result.hub_job_id == "job42"
    mock_post.assert_called_once()
    mock_log.assert_called_once()
    mock_enqueue.assert_called_once()


@patch("shorts_bot.tiktok_shop.bubble_scheduler.pending_hub_jobs_for", return_value=2)
def test_run_bubble_post_skips_when_hub_backlog(mock_pending):
    acct = _bubble_account()
    result = run_bubble_post_for_account(acct, subject="frog")
    assert result.action == "skipped"
    assert "pending hub" in result.detail.lower()
