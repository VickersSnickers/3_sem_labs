import pandas as pd
import subprocess
from pathlib import Path
import re

INPUT = "input.xlsx"
OUTPUT = "cracked.xlsx"
HASHES_TXT = "hashes.txt"
HASHCAT_EXE = r"E:\ProgramFiles\hashcat-7.1.2\hashcat.exe"
MASK = "?d?d?d?d?d?d?d?d?d?d?d"

# читаем хэши из Excel
df = pd.read_excel(INPUT, dtype=str).fillna("")
hashes = [h.strip().lower() for h in df.iloc[:,0] if re.fullmatch(r"[0-9a-f]{32}", h.strip().lower())]

# сохраняем в txt
# with open(HASHES_TXT, "w") as f:
#     f.write("\n".join(hashes))

# получаем ID NVIDIA-устройств
device_ids = ["2"]

# запускаем hashcat
cmd = [
    HASHCAT_EXE,
    "-m", "0",              # MD5
    "-a", "3",              # маска
    "-o", str(OUTPUT), # выходной файл
    HASHES_TXT,
    MASK,
    "--opencl-device-types", "2"  # GPU только
]
subprocess.run(cmd, cwd=Path(HASHCAT_EXE).parent)

# читаем результат и сохраняем в Excel
cracked = pd.read_csv("cracked.txt", sep=":", header=None, names=["hash","password"])
cracked.to_excel(OUTPUT, index=False)
print(f"Saved cracked hashes to {OUTPUT}")
