import os
import zlib

def main():
    exe_path = r"d:\git\遊戲中文化\LOOM\from steam\Loom.exe"
    out_dir = r"d:\git\遊戲中文化\LOOM\from steam\LOOM"
    out_path = os.path.join(out_dir, "000.LFL")

    offset = 187248
    size = 8307
    expected_crc = 0x3ef3e225

    print(f"Opening {exe_path}...")
    if not os.path.exists(exe_path):
        print(f"Error: {exe_path} does not exist.")
        return

    with open(exe_path, "rb") as f:
        f.seek(offset)
        data = f.read(size)

    crc = zlib.crc32(data) & 0xffffffff
    print(f"Calculated CRC32: {crc:08x} (Expected: {expected_crc:08x})")

    if crc == expected_crc:
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "wb") as f_out:
            f_out.write(data)
        print(f"Successfully extracted 000.LFL to {out_path}!")
    else:
        print("Error: CRC32 mismatch. This Loom.exe might be a different version.")

if __name__ == "__main__":
    main()
