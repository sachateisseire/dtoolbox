import asyncio
import os
from playwright.async_api import async_playwright


class RecibosService:
    def __init__(self):
        self.download_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_path, exist_ok=True)

        self.ready = False

    def set_ready(self):
        self.ready = True

    async def run(self, year, month_from, month_to, log_callback):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            await page.goto("https://badesdeadentro.gob.ar/")

            log_callback("🔐 Logueate manualmente en el navegador...")
            log_callback("👉 Luego presioná 'Continuar' en la app")

            # Esperar confirmación desde UI
            while not self.ready:
                await asyncio.sleep(1)

            log_callback("🔎 Buscando recibos...")

            try:
                await page.wait_for_selector("button.descargar-recibo", timeout=15000)
            except:
                log_callback("❌ No se encontraron botones")
                return

            buttons = await page.query_selector_all("button.descargar-recibo")
            log_callback(f"📄 Encontrados {len(buttons)} recibos")

            for i, btn in enumerate(buttons):
                try:
                    log_callback(f"⬇️ Descargando recibo {i}...")

                    async with page.expect_download(timeout=15000) as download_info:
                        await btn.click()

                    download = await download_info.value

                    # nombre sugerido por el server
                    filename = download.suggested_filename or f"recibo_{i}.pdf"

                    # asegurar extensión
                    if not filename.endswith(".pdf"):
                        filename = f"recibo_{i}.pdf"

                    path = os.path.join(self.download_path, filename)

                    # guardar archivo
                    await download.save_as(path)

                    # 🔥 VALIDACIÓN REAL DEL PDF
                    is_valid_pdf = False
                    try:
                        with open(path, "rb") as f:
                            header = f.read(4)
                            if header == b"%PDF":
                                is_valid_pdf = True
                    except:
                        pass

                    # 🔁 REINTENTO SI FALLA
                    if not is_valid_pdf:
                        log_callback("⚠️ Archivo inválido, reintentando...")

                        url = download.url

                        if url:
                            try:
                                response = await context.request.get(url)
                                body = await response.body()

                                with open(path, "wb") as f:
                                    f.write(body)

                                # validar nuevamente
                                with open(path, "rb") as f:
                                    header = f.read(4)
                                    if header == b"%PDF":
                                        log_callback("🔁 Re-descargado correctamente")
                                    else:
                                        log_callback("❌ Sigue inválido")

                            except Exception as e:
                                log_callback(f"❌ Error reintentando: {str(e)}")

                    log_callback(f"✅ Guardado: {filename}")

                    await asyncio.sleep(1)

                except Exception as e:
                    log_callback(f"❌ Error en {i}: {str(e)}")

            log_callback("🎉 Descarga completa")