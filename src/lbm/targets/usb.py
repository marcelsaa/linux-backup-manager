import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class USBTargetInfo:
    found: bool
    label: str
    mountpoint: Path | None
    fsavail: str | None
    fsuse_percent: str | None
    writable: bool


class USBTarget:
    def __init__(self, label: str) -> None:
        self.label = label

    def probe(self) -> USBTargetInfo:
        result = subprocess.run(
            ["lsblk", "-J", "-f"],
            capture_output=True,
            text=True,
            check=True,
        )

        devices = json.loads(result.stdout)

        for device in devices["blockdevices"]:
            info = self._search(device)
            if info is not None:
                return info

        return USBTargetInfo(
            found=False,
            label=self.label,
            mountpoint=None,
            fsavail=None,
            fsuse_percent=None,
            writable=False,
        )

    def _search(self, node: dict) -> USBTargetInfo | None:
        if node.get("label") == self.label:
            mountpoints = node.get("mountpoints") or []
            mountpoint = Path(mountpoints[0]) if mountpoints else None

            writable = False
            if mountpoint is not None:
                writable = os.access(mountpoint, os.W_OK)

            return USBTargetInfo(
                found=True,
                label=self.label,
                mountpoint=mountpoint,
                fsavail=node.get("fsavail"),
                fsuse_percent=node.get("fsuse%"),
                writable=writable,
            )

        for child in node.get("children", []):
            result = self._search(child)
            if result is not None:
                return result

        return None