# rsync.py

import subprocess
import os
import time

class RsyncBackup:
    def __init__(self, ssh_config, source, backup_path=None, delete=False):
        self.ssh_user = ssh_config["username"]
        self.ssh_host = ssh_config["host"]
        self.ssh_port = ssh_config["port"]
        self.ssh_key = ssh_config.get("key_path")
        self.source_path = source
        self.delete = delete
        self.destination_path = backup_path or f"./backup_{self.ssh_host}_{self.ssh_port}_{self.source_path.strip('/').replace('/', '_')}"
        os.makedirs(self.destination_path, exist_ok=True)

    def run_restore_loop(self, stop_event):
        rsync_command = [
            "rsync", "-azv",
            "--progress",
            "-e", f"ssh -p {self.ssh_port}"
        ]
        if self.delete:
            rsync_command.append("--delete")
        if self.ssh_key:
            rsync_command[-1] += f" -i {self.ssh_key}"

        rsync_command.append(f"{self.ssh_user}@{self.ssh_host}:{self.source_path}/")
        rsync_command.append(self.destination_path)

        print(f"\n[+] Syncing from '{self.ssh_user}@{self.ssh_host}:{self.source_path}' to local '{self.destination_path}'...\n")

        while not stop_event.is_set():
            try:
                subprocess.run(rsync_command, check=True)
                print("[✔] Sync complete. Waiting for next check...\n")
            except subprocess.CalledProcessError as e:
                print(f"[❌] Error in rsync: {e}")

            time.sleep(5)
