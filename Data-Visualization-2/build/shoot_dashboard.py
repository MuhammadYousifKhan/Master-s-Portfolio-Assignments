import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8599"
FIG = Path(__file__).resolve().parents[1] / "figures"
FIG.mkdir(exist_ok=True)


def settle(page, seconds=4):
    page.wait_for_selector("text=EcoMove Mobility Decision Dashboard", timeout=60000)
    page.wait_for_selector(".js-plotly-plot", timeout=60000)
    time.sleep(seconds)


def shot(page, name):
    page.screenshot(path=str(FIG / name), full_page=True)


def open_tab(page, name):
    page.get_by_role("tab", name=name).click()
    time.sleep(6)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 1300})
    page.goto(URL)
    settle(page)
    shot(page, "dash_01_overview_route.png")
    for tab, name in [("Reliability", "dash_02_reliability.png"), ("Sustainability", "dash_03_sustainability.png"),
                      ("Accessibility", "dash_04_accessibility.png"), ("Investment", "dash_05_investment.png")]:
        open_tab(page, tab)
        shot(page, name)
    page.goto(URL + "/?mode=Bus&event=Yes")
    settle(page)
    open_tab(page, "Reliability")
    shot(page, "dash_06_filtered.png")
    browser.close()
