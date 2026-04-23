"""Unit tests for backend Pydantic request models.

Exercises the validation rules so API level invariants (like coupon
percent bounds) cannot regress silently.
"""
import pytest
from pydantic import ValidationError

from main import CouponCreateM, CouponValidateM, WebhookCreateM


class TestCouponCreate:
    def test_minimal_valid_coupon(self):
        c = CouponCreateM(code="WELCOME50", discount_pct=50)
        assert c.code == "WELCOME50"
        assert c.discount_pct == 50
        assert c.max_redemptions == -1
        assert c.valid_plans == []

    def test_rejects_discount_over_100(self):
        with pytest.raises(ValidationError):
            CouponCreateM(code="X", discount_pct=101)

    def test_rejects_discount_below_1(self):
        with pytest.raises(ValidationError):
            CouponCreateM(code="X", discount_pct=0)

    def test_rejects_negative_discount(self):
        with pytest.raises(ValidationError):
            CouponCreateM(code="X", discount_pct=-5)


class TestCouponValidate:
    def test_minimal(self):
        c = CouponValidateM(code="HELLO")
        assert c.code == "HELLO"
        assert c.plan == ""

    def test_with_plan(self):
        c = CouponValidateM(code="HELLO", plan="pro")
        assert c.plan == "pro"


class TestWebhookCreate:
    def test_requires_events_field(self):
        with pytest.raises(ValidationError):
            WebhookCreateM(url="https://example.com/hook")

    def test_valid(self):
        w = WebhookCreateM(
            url="https://example.com/hook",
            events=["user.created", "organization.created"],
        )
        assert len(w.events) == 2
