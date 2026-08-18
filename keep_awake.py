# keep_awake.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import sys

APP_URLS = [
    "https://gasto-publico-cl.streamlit.app/",
    "https://combustibles-cl.streamlit.app/",
]

WAKEUP_SELECTOR = '[data-testid^="wakeup-button"]'

def check_and_wake(url: str, page) -> None:
    print(f"Visitando: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)

    try:
        boton = page.locator(WAKEUP_SELECTOR)
        boton.wait_for(state="visible", timeout=8000)

        print("  → App dormida, haciendo clic para despertarla...")
        boton.click()

        # Esperamos a que el botón desaparezca (arrancó el proceso)
        boton.wait_for(state="hidden", timeout=60000)

        # Clave: esperamos a que la red se quede quieta, señal de que
        # la app terminó de cargar sus datos/dependencias, no solo
        # que arrancó el servidor.
        print("  → Esperando a que termine de cargar completamente...")
        page.wait_for_load_state("networkidle", timeout=90000)

        print("  → Listo, app completamente activa.")

    except PlaywrightTimeout:
        print("  → No apareció botón de despertar. App ya estaba activa.")
def main():
    fallas = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in APP_URLS:
            try:
                check_and_wake(url, page)
            except Exception as e:
                print(f"  → ERROR con {url}: {e}")
                fallas.append(url)

        browser.close()

    if fallas:
        print(f"\nFallaron {len(fallas)} apps: {fallas}")
        sys.exit(1)  # código de error, para que GitHub Actions marque el run en rojo

    print("\nTodas las apps revisadas correctamente.")


if __name__ == "__main__":
    main()