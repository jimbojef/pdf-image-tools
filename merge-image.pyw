# merge-image - setzt mehrere Bilder zu einem Bild zusammen.
#
# Bedienung:
#   - Doppelklick auf merge-image.pyw: Dateiauswahl öffnet sich.
#   - Bilder (oder einen Ordner) auf merge-image.pyw ziehen.
#   - Rechtsklick auf Bilder > Senden an > "merge-image" (nach Einrichtung).
#
# Danach wird gefragt: untereinander (Ja) oder nebeneinander (Nein).
# Reihenfolge: natürlich nach Dateiname (seite_2 vor seite_10).
# Ergebnis: "zusammen.png" im Ordner des ersten Bildes. Gibt es die Datei
# schon, heißt die neue zusammen_2.png usw. Nichts wird überschrieben.

import re
import subprocess
import sys
from pathlib import Path

ENDUNGEN = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}

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
    print(f"{titel}: {text}")
    if tk:
        root = _root()
        (messagebox.showerror if fehler else messagebox.showinfo)(titel, text, parent=root)
        root.destroy()


def pillow_laden():
    """Lädt Pillow und installiert es bei Bedarf einmalig."""
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("Pillow fehlt, wird installiert ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pillow"])
        from PIL import Image
        return Image


def natuerlich(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def bilder_sammeln(argumente):
    dateien = []
    for a in argumente:
        p = Path(a)
        if p.is_dir():
            dateien += [x for x in p.iterdir() if x.suffix.lower() in ENDUNGEN
                        and not re.fullmatch(r"zusammen(_\d+)?\.png", x.name)]  # frühere Ergebnisse auslassen
        elif p.suffix.lower() in ENDUNGEN and p.exists():
            dateien.append(p)
    # doppelte entfernen, natürlich sortieren
    return sorted(dict.fromkeys(dateien), key=natuerlich)


def freier_name(ordner, name="zusammen", endung=".png"):
    ziel, n = ordner / f"{name}{endung}", 2
    while ziel.exists():
        ziel = ordner / f"{name}_{n}{endung}"
        n += 1
    return ziel


def zusammenfuegen(Image, dateien, vertikal=True):
    bilder = [Image.open(p).convert("RGB") for p in dateien]
    if vertikal:
        groesse = (max(b.width for b in bilder), sum(b.height for b in bilder))
    else:
        groesse = (sum(b.width for b in bilder), max(b.height for b in bilder))
    ergebnis = Image.new("RGB", groesse, "white")
    pos = 0
    for b in bilder:
        ergebnis.paste(b, (0, pos) if vertikal else (pos, 0))
        pos += b.height if vertikal else b.width
    ziel = freier_name(dateien[0].parent)
    ergebnis.save(ziel)
    return ziel


def main():
    argumente = sys.argv[1:]
    if not argumente and tk:
        root = _root()
        argumente = filedialog.askopenfilenames(parent=root,
            title="Bilder auswählen",
            filetypes=[("Bilder", " ".join("*" + e for e in sorted(ENDUNGEN)))])
        root.destroy()

    dateien = bilder_sammeln(argumente)
    if len(dateien) < 2:
        meldung("merge-image", "Bitte mindestens 2 Bilder auswählen.")
        return

    vertikal = True
    if tk:
        root = _root()
        antwort = messagebox.askyesnocancel(
            "merge-image",
            f"{len(dateien)} Bilder.\n\nJa = untereinander\nNein = nebeneinander",
            parent=root)
        root.destroy()
        if antwort is None:
            return
        vertikal = antwort

    Image = pillow_laden()
    try:
        ziel = zusammenfuegen(Image, dateien, vertikal)
        meldung("merge-image",
                f"Fertig: {len(dateien)} Bilder -> {ziel}\n\nReihenfolge:\n"
                + "\n".join(p.name for p in dateien[:20])
                + ("\n..." if len(dateien) > 20 else ""))
    except Exception as e:
        meldung("merge-image", str(e), fehler=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # ohne Konsole sonst unsichtbar
        meldung("Fehler", repr(e), fehler=True)
