"""Exercise the production HTTP service with a real browser and a synthetic image."""
import os
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


with sync_playwright() as playwright, tempfile.TemporaryDirectory() as directory:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto(os.environ.get("WORKBENCH_URL", "http://127.0.0.1:8080"))
    expect(page.locator("#result")).to_be_visible()
    expect(page.locator("#resultInfo")).to_contain_text("% of pixels selected")
    for operation in ("threshold", "region", "noise", "smooth"):
        page.locator("#operation").select_option(operation)
        if operation == "region":
            page.locator("#source").click(position={"x": 12, "y": 12})
            assert int(page.locator("#x").input_value()) < 50
            page.get_by_role("spinbutton", name="Seed X").fill("160")
        page.get_by_role("button", name="Run filter").click()
        expect(page.get_by_role("status").filter(has_text="pixels processed")).to_be_visible()
        expect(page.locator("#result")).to_be_visible()

    with page.expect_download() as download:
        page.get_by_role("button", name="Export PNG").click()
    exported = Path(directory) / "roundtrip.png"
    download.value.save_as(exported)
    assert exported.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    page.locator("#file").set_input_files(exported)
    expect(page.locator("#filename")).to_contain_text("roundtrip.png")
    expect(page.get_by_role("button", name="Export PNG")).to_be_disabled()
    page.set_viewport_size({"width": 375, "height": 812})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.get_by_role("button", name="Run filter").click()
    expect(page.get_by_role("button", name="Export PNG")).to_be_enabled()
    browser.close()
