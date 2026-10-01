"""Generate demo QR codes pointing at the local trace pages."""

from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "server" / "static" / "qr"
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://127.0.0.1:8760"

CODES = {
    "GT-A01-8F3K2M": "精纺羊毛大衣",
    "GT-A02-5R9W1P": "真丝印花连衣裙",
    "GT-B01-7N4Q6X": "精梳棉衬衫",
}


def main() -> None:
    for code in CODES:
        url = f"{BASE}/t/{code}"
        img = qrcode.make(url, box_size=8, border=2)
        path = OUT / f"{code}.png"
        img.save(path)
        print(f"wrote {path} -> {url}")


if __name__ == "__main__":
    main()
