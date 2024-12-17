import tarfile
import os
from pathlib import Path


class ShellEmulator:
    def __init__(self, username, fs_archive):
        self.username = username
        self.fs_root = Path("/tmp/virtual_fs")
        self.current_dir = self.fs_root
        self._extract_fs(fs_archive)

    def _extract_fs(self, archive_path):
        if not tarfile.is_tarfile(archive_path):
            raise ValueError("Provided file is not a valid tar archive.")
        if self.fs_root.exists():
            self._cleanup_fs()
        self.fs_root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive_path, 'r') as tar:
            tar.extractall(path=self.fs_root)

    def _cleanup_fs(self):
        for item in self.fs_root.glob("**/*"):
            if item.is_file():
                item.unlink()
            else:
                os.rmdir(item)
        self.fs_root.rmdir()

    def prompt(self):
        return f"{self.username}@emulator:{self.current_dir.relative_to(self.fs_root)}$ "

    def ls(self):
        return "\n".join(os.listdir(self.current_dir))

    def cd(self, path):
        new_path = self.current_dir / path
        if new_path.exists() and new_path.is_dir():
            self.current_dir = new_path.resolve()
        else:
            raise FileNotFoundError(f"No such directory: {path}")

    def mkdir(self, path):
        new_dir = self.current_dir / path
        new_dir.mkdir(parents=True, exist_ok=True)

    def chmod(self, mode, path):
        target_path = self.current_dir / path
        if target_path.exists():
            target_path.chmod(int(mode, 8))
        else:
            raise FileNotFoundError(f"No such file or directory: {path}")

    def du(self):
        return sum(f.stat().st_size for f in self.current_dir.rglob('*') if f.is_file())

    def exit(self):
        self._cleanup_fs()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument(
        "--username",
        required=True,
        help="Username for the shell prompt"
        )
    parser.add_argument(
        "--fs",
        required=True,
        help="Path to the tar archive for the virtual filesystem"
        )

    args = parser.parse_args()

    emulator = ShellEmulator(username=args.username, fs_archive=args.fs)

    try:
        while True:
            command = input(emulator.prompt()).strip().split()
            if not command:
                continue
            cmd, *args = command
            if cmd == "ls":
                print(emulator.ls())
            elif cmd == "cd":
                emulator.cd(args[0])
            elif cmd == "mkdir":
                emulator.mkdir(args[0])
            elif cmd == "chmod":
                emulator.chmod(args[0], args[1])
            elif cmd == "du":
                print(emulator.du())
            elif cmd == "exit":
                emulator.exit()
                break
            else:
                print(f"Command not found: {cmd}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
