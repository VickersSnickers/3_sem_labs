import pandas as pd
import subprocess
from pathlib import Path
import re

# пути
BASE_DIR = Path(__file__).parent
HASHCAT_EXE = Path(r"E:\ProgramFiles\hashcat-7.1.2\hashcat.exe")

INPUT = BASE_DIR / "data/data_вар. 1.xlsx"
HASHES_TXT = BASE_DIR / "hashes.txt"
OUTPUT_TXT = BASE_DIR / "cracked.txt"
OUTPUT_XLSX = BASE_DIR / "cracked.xlsx"

MASK = "?d?d?d?d?d?d?d?d?d?d?d"

# читаем хэши
df = pd.read_excel(INPUT, dtype=str).fillna("")
hashes = [h.strip().lower() for h in df.iloc[:, 0] if re.fullmatch(r"[0-9a-f]{32}", h.strip().lower())]

# сохраняем в txt
with open(HASHES_TXT, "w") as f:
    f.write("\n".join(hashes))

# команды hashcat
cmd = [
    str(HASHCAT_EXE),
    "-m", "0",
    "-a", "3",
    "-o", str(OUTPUT_TXT),
    "--show",
    "-O",
    str(HASHES_TXT),
    MASK
]

# запускаем hashcat (рабочая директория — та же, где Python-скрипт)
subprocess.run(cmd, cwd=Path(HASHCAT_EXE).parent)

# читаем результаты
if OUTPUT_TXT.exists():
    cracked = pd.read_csv(OUTPUT_TXT, sep=":", header=None, names=["hash", "password"])
    cracked.to_excel(OUTPUT_XLSX, index=False)
    print(f"✅ Saved cracked hashes to {OUTPUT_XLSX}")
else:
    print("⚠️ Hashcat did not produce an output file.")
