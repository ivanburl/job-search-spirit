"""Exercise installed libraries and MCP handshakes without reading user documents."""

import asyncio
import io
import sys


def probe_cv():
    import pdfplumber
    import pypdfium2
    # Minimal independent PDF fixture, avoiding a reportlab runtime dependency.
    stream = b"BT /F1 12 Tf 20 50 Td (Job Search Spirit) Tj ET"
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    with pdfplumber.open(io.BytesIO(pdf)) as document:
        if "Job Search Spirit" not in document.pages[0].extract_text():
            raise RuntimeError("PDF text extraction check failed")
    with pypdfium2.PdfDocument(bytes(pdf)) as document:
        page = document[0]
        bitmap = page.render(scale=1)
        try:
            if bitmap.width <= 0 or bitmap.height <= 0:
                raise RuntimeError("PDF rendering check failed")
        finally:
            bitmap.close()
            page.close()


def probe_browser():
    from playwright.sync_api import sync_playwright
    from patchright.sync_api import sync_playwright as sync_patchright
    for engine in (sync_playwright, sync_patchright):
        with engine() as driver:
            browser = driver.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_content("<title>Job Search Spirit</title>")
                if page.title() != "Job Search Spirit":
                    raise RuntimeError("Browser check failed")
            finally:
                browser.close()


async def probe_mcp(command, args):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import os
    async with asyncio.timeout(60):
        async with stdio_client(StdioServerParameters(command=command, args=args, env=dict(os.environ))) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.list_tools()
                if not result.tools:
                    raise RuntimeError("MCP server exposed no tools")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "cv":
        probe_cv()
    elif mode == "browser":
        probe_browser()
    elif mode == "mcp":
        asyncio.run(probe_mcp(sys.argv[2], sys.argv[3:]))
    else:
        raise SystemExit("Unknown probe")
