#!/usr/bin/env python3

import os
import subprocess
import yaml
from pathlib import Path
import argparse


def is_mount_active(mount_point):
    return os.path.ismount(mount_point)


def get_containers_from_compose(compose_file):
    with open(compose_file, "r") as f:
        compose_data = yaml.safe_load(f)
        containers = []
    if "services" in compose_data:
        for service, config in compose_data["services"].items():
            # Ignore services that have "profiles" set
            if "profiles" in config:
                continue
            volumes = config.get("volumes", [])
            if any("NAS_" in vol for vol in volumes):
                containers.append(service)
    return containers


def main(command, dry_run, force):
    mount_point = "/mnt/nastea/download/"
    compose_dir = Path.home() / "code/docker-compose"
    compose_files = compose_dir.glob("**/*.yml")
    master_compose_file = compose_dir / "docker-compose.yml"
    all_containers = []
    for compose_file in compose_files:
        all_containers.extend(get_containers_from_compose(compose_file))

    if dry_run:
        print("Dry Run - Containers with NAS mount dependencies:")
        for container in set(all_containers):
            print(container)
        return

    if force:
        print("Force mode enabled. Stopping all containers involved.")

    match command:
        case "stop":
            if not is_mount_active(mount_point) or force:
                print("Stopping NAS dependent containers:")
                for container in all_containers:
                    print(f"Stopping container: {container}")
                    subprocess.run(
                        [
                            "docker",
                            "compose",
                            "-f",
                            str(master_compose_file),
                            "stop",
                            container,
                        ]
                    )
            else:
                print("NFS mount is active, no constainers stopped.")
        case "start":
            if is_mount_active(mount_point) or force:
                if force:
                    print(
                        "Force mode enabled. Starting all containers involved is a bad idea."
                    )
                    confirm = input(
                        "Are you sure you want to start all containers? (y/N) "
                    )
                    if confirm.lower() != "y":
                        print("Operation cancelled.")
                        exit(0)
                print("Starting NAS dependent containers:")
                for container in all_containers:
                    print(f"Stopping container: {container}")
                    subprocess.run(
                        [
                            "docker",
                            "compose",
                            "-f",
                            str(master_compose_file),
                            "start",
                            container,
                        ]
                    )
            else:
                print("NFS mount is not active, no constainers started.")
        case _:
            print("Error: Invalid command.")
            exit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Add required first positional argument of a command (supports start and stop)
    parser.add_argument(
        "command",
        choices=["start", "stop"],
        help="Choose a command to execute.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List involved containers without stopping them",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force stop of containers",
    )
    args = parser.parse_args()

    # Error if both --dry-run and --force are set
    if args.dry_run and args.force:
        print("Error: Cannot use --dry-run and --force at the same time.")
        exit(1)
    main(args.command, args.dry_run, args.force)
