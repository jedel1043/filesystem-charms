# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details

"""Unit tests for `lustre_ops.repository`."""

from subprocess import CalledProcessError
from unittest.mock import MagicMock

import pytest
from lustre_ops import repository
from lustre_ops.errors import RepositoryCodenameError, RepositorySyncError
from pytest_mock import MockerFixture


@pytest.fixture(scope="function", autouse=True)
def mock_os_release(mocker: MockerFixture) -> MagicMock:
    """Mock platform.freedesktop_os_release."""
    return mocker.patch.object(
        repository.platform,
        "freedesktop_os_release",
        return_value={"VERSION_CODENAME": "resolute"},
    )


@pytest.fixture(scope="function", autouse=True)
def mock_preferences(mocker: MockerFixture) -> MagicMock:
    """Mock the apt preferences file for the proposed pocket pin."""
    return mocker.patch.object(repository, "_LUSTRE_PROPOSED_PREFERENCES")


class TestSetupLustreRepository:
    """setup_lustre_repository() tests."""

    def test_success(self, mocker: MockerFixture, mock_preferences: MagicMock) -> None:
        """Proposed pocket is configured with a pin and the APT index refreshed."""
        mock_repo = mocker.patch.object(repository.apt, "DebianRepository")
        mock_mapping = mocker.patch.object(repository.apt, "RepositoryMapping").return_value
        mock_update = mocker.patch.object(repository.apt, "update")

        repository.setup_lustre_repository()

        mock_repo.assert_called_once_with(
            enabled=True,
            repotype="deb",
            uri=repository.LUSTRE_REPOSITORY_URI,
            release="resolute-proposed",
            groups=["main", "restricted", "universe", "multiverse"],
            filename="lustre-repo",
        )
        mock_preferences.write_text.assert_called_once_with(
            "Package: *\nPin: release a=resolute-proposed\nPin-Priority: 400\n"
        )
        mock_mapping.add.assert_called_once_with(mock_repo.return_value)
        mock_update.assert_called_once()

    def test_missing_version_codename(
        self, mocker: MockerFixture, mock_os_release: MagicMock
    ) -> None:
        """Failure to retrieve the OS codename raises error."""
        mock_os_release.return_value = {}
        mocker.patch.object(repository.apt, "DebianRepository")

        with pytest.raises(RepositoryCodenameError):
            repository.setup_lustre_repository()

    def test_preferences_error(
        self, mocker: MockerFixture, mock_preferences: MagicMock
    ) -> None:
        """Proposed pocket pin failure raises error."""
        mocker.patch.object(repository.apt, "DebianRepository")
        mock_preferences.write_text.side_effect = OSError("read-only file system")

        with pytest.raises(RepositorySyncError):
            repository.setup_lustre_repository()

    def test_repo_add_error(self, mocker: MockerFixture) -> None:
        """Repository add/update failure raises error."""
        mocker.patch.object(repository.apt, "DebianRepository")
        mock_mapping = mocker.patch.object(repository.apt, "RepositoryMapping").return_value
        mock_mapping.add.side_effect = CalledProcessError(1, "apt")

        with pytest.raises(RepositorySyncError):
            repository.setup_lustre_repository()

    def test_update_error(self, mocker: MockerFixture) -> None:
        """apt.update() failure raises error."""
        mocker.patch.object(repository.apt, "DebianRepository")
        mocker.patch.object(repository.apt, "RepositoryMapping")
        mocker.patch.object(
            repository.apt, "update", side_effect=CalledProcessError(1, "apt update")
        )

        with pytest.raises(RepositorySyncError):
            repository.setup_lustre_repository()
