from shorts_bot.browser.stealth import launch_stealth_context


def test_stealth_context_launches():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("about:blank")
        assert page.url.startswith("about:")
        ctx.close()
