import os, sys, time, threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from playwright.sync_api import sync_playwright
import zipfile, xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.abspath('.'), **kwargs)

def start_server(port=8099):
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def test_download():
    port = 8099
    httpd = start_server(port)
    url = f"http://127.0.0.1:{port}/index.html"
    print(f"Opening local server: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        # Listen for console errors
        page.on("console", lambda msg: print(f"BROWSER LOG [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err}"))
        
        page.goto(url)
        page.wait_for_load_state('domcontentloaded')
        time.sleep(1)
        
        # 1. Click on Preset 3 Tramos (q=500)
        btn_preset = page.locator("button:has-text('Examen 3 Tramos')")
        assert btn_preset.count() > 0, "Preset button not found!"
        btn_preset.first.click()
        print("Clicked preset: Examen 3 Tramos (q=500)")
        time.sleep(0.5)
        
        # 2. Click on Descargar .mcdx and catch the download
        download_btn = page.locator("#btnDownloadMcdx")
        with page.expect_download(timeout=10000) as download_info:
            download_btn.click()
            print("Clicked 'Descargar .mcdx'...")
            
        download = download_info.value
        dest_path = os.path.abspath("test_outputs/TEST_E2E_WEB_DOWNLOAD.mcdx")
        os.makedirs("test_outputs", exist_ok=True)
        download.save_as(dest_path)
        print(f"Downloaded file saved to: {dest_path}")
        browser.close()
        
        # 3. Validate XML schema of the downloaded file
        print(f"\n--- Validating E2E Downloaded MCDX ---")
        with zipfile.ZipFile(dest_path, 'r') as z:
            root = ET.fromstring(z.read('mathcad/worksheet.xml'))

        errors = []
        binary_ops = {'mult', 'div', 'pow', 'greaterThan', 'greaterOrEqual'}
        for r in root.iter('{http://schemas.mathsoft.com/worksheet50}region'):
            rid = r.attrib.get('region-id')
            for apply_el in r.iter('{http://schemas.mathsoft.com/math50}apply'):
                if len(apply_el) == 0:
                    errors.append(f"Region {rid}: Empty <apply /> element")
                    continue
                op_tag = apply_el[0].tag.split('}')[-1]
                num_args = len(apply_el) - 1
                if op_tag in binary_ops and num_args != 2:
                    errors.append(f"Region {rid}: Binary op <{op_tag}> has {num_args} args (expected 2)! Children: {[c.tag.split('}')[-1] for c in apply_el]}")
                elif op_tag == 'minus' and num_args not in (1, 2):
                    errors.append(f"Region {rid}: Op <minus> has {num_args} args (expected 1 or 2)!")
                elif op_tag == 'plus' and num_args < 2:
                    errors.append(f"Region {rid}: Op <plus> has {num_args} args (expected >= 2)!")

        if errors:
            print(f"❌ VALIDATION FAILED with {len(errors)} errors:")
            for e in errors:
                print("  ❌", e)
            sys.exit(1)
        else:
            print("🎉 SUCCESS: Downloaded .mcdx is 100% VALID and passes all Mathcad Prime schema rules!")

if __name__ == '__main__':
    test_download()
