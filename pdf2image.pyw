# pdf2image - wandelt PDF-Seiten in PNG-Bilder um.
#
# Bedienung:
#   - Doppelklick auf pdf2image.pyw: Dateiauswahl öffnet sich.
#   - PDFs (oder Ordner) auf pdf2image.pyw ziehen.
#   - Rechtsklick auf PDFs > Senden an > "pdf2image" (nach Einrichtung).
#
# Ergebnis: neben jeder PDF entsteht ein Ordner "<PDF-Name>_bilder"
# mit seite_1.png, seite_2.png usw. Vorhandene Bilder werden nicht
# überschrieben, sondern bekommen einen neuen Ordnernamen (_2, _3 ...).

import subprocess
import sys
from pathlib import Path

DPI = 300          # Auflösung; 150 reicht für Bildschirm, 300 für Druck
FORMAT = "png"     # "png" oder "jpg"

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    tk = None


def _root():
    """Unsichtbares Hauptfenster, immer im Vordergrund, damit Dialoge nicht hinter anderen Fenstern verschwinden."""
    r = tk.Tk()
    r.withdraw()
    r.attributes("-topmost", True)
    r.lift()
    r.focus_force()
    return r


def meldung(titel, text, fehler=False):
    """Zeigt ein Fenster, sonst Textausgabe."""
    print(f"{titel}: {text}")
    if tk:
        root = _root()
        (messagebox.showerror if fehler else messagebox.showinfo)(titel, text, parent=root)
        root.destroy()


def pymupdf_laden():
    """Lädt PyMuPDF und installiert es bei Bedarf einmalig."""
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        print("PyMuPDF fehlt, wird installiert ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pymupdf"])
        import pymupdf
        return pymupdf


def pdfs_sammeln(argumente):
    """Macht aus Dateien und Ordnern eine Liste von PDFs."""
    pdfs = []
    for a in argumente:
        p = Path(a)
        if p.is_dir():
            pdfs += sorted(p.glob("*.pdf")) + sorted(p.glob("*.PDF"))
        elif p.suffix.lower() == ".pdf" and p.exists():
            pdfs.append(p)
    return list(dict.fromkeys(pdfs))  # doppelte entfernen


def freier_ordner(basis):
    """Gibt einen Ordnernamen zurück, der noch nicht existiert."""
    ziel, n = basis, 2
    while ziel.exists():
        ziel = basis.with_name(f"{basis.name}_{n}")
        n += 1
    return ziel


def umwandeln(pymupdf, pdf):
    # strip(): Windows entfernt Leerzeichen am Ende von Ordnernamen
    ziel = freier_ordner(pdf.parent / f"{pdf.stem.strip()}_bilder")
    ziel.mkdir(parents=True)
    zoom = DPI / 72
    with pymupdf.open(pdf) as doc:
        for i, seite in enumerate(doc, start=1):
            pix = seite.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            pix.save(ziel / f"seite_{i}.{FORMAT}")
        return ziel, len(doc)


def main():
    argumente = sys.argv[1:]
    if not argumente and tk:
        root = _root()
        argumente = filedialog.askopenfilenames(parent=root,
            title="PDFs auswählen", filetypes=[("PDF-Dateien", "*.pdf")])
        root.destroy()

    pdfs = pdfs_sammeln(argumente)
    if not pdfs:
        meldung("pdf2image", "Keine PDF ausgewählt.")
        return

    pymupdf = pymupdf_laden()
    ok, fehler = [], []
    for pdf in pdfs:
        try:
            ziel, seiten = umwandeln(pymupdf, pdf)
            ok.append(f"{pdf.name}: {seiten} Seite(n) -> {ziel.name}")
        except Exception as e:
            fehler.append(f"{pdf.name}: {e}")

    text = "\n".join(ok)
    if fehler:
        text += "\n\nFehler:\n" + "\n".join(fehler)
    meldung("pdf2image", text or "Nichts umgewandelt.", fehler=bool(fehler))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # ohne Konsole sonst unsichtbar
        meldung("Fehler", repr(e), fehler=True)
