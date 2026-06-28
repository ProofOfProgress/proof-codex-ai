def test_format_scout_report_empty():
    from shorts_bot.tiktok_shop.scout_report import format_scout_report

    out = format_scout_report([], preset="middle_core")
    assert "No products" in out


def test_format_scout_report_row():
    from shorts_bot.tiktok_shop.scout_report import format_scout_report

    out = format_scout_report(
        [
            {
                "product_id": "123",
                "product_name": "Test Widget",
                "score": 72,
                "commission_usd": 5.5,
                "commission_rate": 0.2,
                "price": 27.5,
                "gmv_period": 12000,
                "creators": 45,
                "videos": 8,
            }
        ],
        preset="middle_core",
    )
    assert "Test Widget" in out
    assert "123" in out
    assert "FastMoss" in out
