# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details

"""Lustre package repository setup."""

import platform
from pathlib import Path
from subprocess import CalledProcessError

from charmlibs import apt

from lustre_ops.constants import LUSTRE_REPOSITORY_URI
from lustre_ops.errors import RepositoryCodenameError, RepositorySyncError

_LUSTRE_REPO_FILENAME = "lustre-repo"
_LUSTRE_REPO_GROUPS = ["main", "restricted", "universe", "multiverse"]
_LUSTRE_PROPOSED_PREFERENCES = Path("/etc/apt/preferences.d/lustre-proposed.pref")

# Pin the proposed pocket below the release pocket so that only packages that are
# not available elsewhere, such as the Lustre packages, are installed from it.
_PROPOSED_PIN = """\
Package: *
Pin: release a={codename}-proposed
Pin-Priority: 400
"""


def setup_lustre_repository() -> None:
    """Configure the Lustre package repository. Idempotent.

    The Lustre packages are only published in the proposed pocket of the Ubuntu
    archive, so the pocket is enabled with a pin that prevents unrelated packages
    from being installed from it.

    Raises:
        RepositoryCodenameError: If the OS version codename cannot be determined.
        RepositorySyncError: If the repository cannot be added or refreshed.
    """
    try:
        codename = platform.freedesktop_os_release()["VERSION_CODENAME"]
    except KeyError as e:
        raise RepositoryCodenameError("Failed to determine OS version codename") from e

    repo = apt.DebianRepository(
        enabled=True,
        repotype="deb",
        uri=LUSTRE_REPOSITORY_URI,
        release=f"{codename}-proposed",
        groups=_LUSTRE_REPO_GROUPS,
        filename=_LUSTRE_REPO_FILENAME,
    )

    try:
        _LUSTRE_PROPOSED_PREFERENCES.write_text(_PROPOSED_PIN.format(codename=codename))
        apt.RepositoryMapping().add(repo)
        apt.update()
    except (CalledProcessError, OSError) as e:
        raise RepositorySyncError("Failed to add or refresh Lustre repository") from e
