# Docker compose related scripts

This is a small collection of assorted scripts and bits I wrote for handling
tasks related to my `docker compose` setup.

I run most of my services via elaborate `docker-compose.yml` and imports
between each of them to make bringing my whole set of assorted homelab
services up as simple as starting the one compose project, which is
configured by a single `.env` stored in Vault.

I'm documenting this collection for my own sanity, and keeping it public for
anyone else's sanity.

## Python scripts

- `./compose-mnt-restrict.py`: starts and stops containers that depend on
 volumes over NFS mounts if they are not accessible.
  - I recommend also being sure you set `sudo chattr +i /mnt/path/to/yours`
   while unmounted to make them immutable so you can't let docker mount them
   directly and make a mess...ever.
