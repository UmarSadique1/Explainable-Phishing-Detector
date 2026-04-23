import csv
from pathlib import Path

# Input file from UCI (no extension)
src = Path("data/SMSSpamCollection")

# Output CSV we'll train on
out = Path("data/sms_spam.csv")

if not src.exists():
    raise FileNotFoundError(
        f"Missing {src}. Make sure SMSSpamCollection is inside the data/ folder."
    )

rows = []
with src.open("r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Each line: label \t message
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue

        label, text = parts[0].strip(), parts[1].strip()
        y = 1 if label.lower() == "spam" else 0  # spam=1, ham=0
        rows.append((text, y))

out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["text", "label"])
    w.writerows(rows)

print(f"✅ Saved: {out} ({len(rows)} rows)")
