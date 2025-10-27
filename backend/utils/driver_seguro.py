import os
import uuid
import shutil
import traceback
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


def criar_driver_seguro():
    """Cria um driver Chrome isolado e retorna driver + pasta de perfil."""
    os.makedirs("/app/tmp", exist_ok=True)
    user_data_dir = f"/app/tmp/chrome_{uuid.uuid4()}"
    os.makedirs(user_data_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver, user_data_dir


def capturar_estado_driver(driver, prefixo="erro"):
    """Salva HTML e screenshot do estado atual do driver."""
    os.makedirs("/app/debug", exist_ok=True)
    html_path = f"/app/debug/{prefixo}_{uuid.uuid4()}.html"
    screenshot_path = f"/app/debug/{prefixo}_{uuid.uuid4()}.png"

    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot(screenshot_path)
        print(f"📄 HTML salvo: {html_path}")
        print(f"🖼️ Screenshot salvo: {screenshot_path}")
    except WebDriverException as e:
        print("⚠️ Falha ao capturar estado do driver:", e)
