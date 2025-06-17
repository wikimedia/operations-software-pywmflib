"""Phabricator module tests."""

import logging
import re
from unittest import mock

import pytest

from wmflib import phabricator
from wmflib.tests import check_logs, get_fixture_path


@pytest.mark.parametrize("allow_empty_identifiers", (True, False))
def test_create_phabricator_ok(allow_empty_identifiers):
    """It should initialize the instance."""
    phab = phabricator.create_phabricator(
        get_fixture_path("phabricator", "valid.conf"), allow_empty_identifiers=allow_empty_identifiers
    )
    assert isinstance(phab, phabricator.Phabricator)


def test_create_phabricator_missing_section():
    """It should raise PhabricatorError if the specified section is missing in the bot config file."""
    with pytest.raises(phabricator.PhabricatorError, match="Unable to find section"):
        phabricator.create_phabricator(get_fixture_path("phabricator", "valid.conf"), section="nonexistent")


def test_create_phabricator_missing_option():
    """It should raise PhabricatorError if any of the mandatory option is missing in the bot config file."""
    with pytest.raises(phabricator.PhabricatorError, match="Unable to find all required options"):
        phabricator.create_phabricator(get_fixture_path("phabricator", "invalid.conf"))


@mock.patch("wmflib.phabricator.phabricator.Phabricator", side_effect=RuntimeError)
def test_init_client_raise(mocked_phabricator):
    """It should raise PhabricatorError if unable to instantiate the Phabricator client."""
    with pytest.raises(phabricator.PhabricatorError, match="Unable to instantiate Phabricator client"):
        phabricator.create_phabricator(get_fixture_path("phabricator", "valid.conf"))

    # Values from the phabricator/valid.conf fixture
    mocked_phabricator.assert_called_once_with(  # nosec
        host="https://phabricator.example.com/api/", username="phab-bot", token="api-12345"
    )


@pytest.mark.parametrize("allow_empty_identifiers", (True, False))
@pytest.mark.parametrize(
    "task_id",
    (
        "",
        "T1",
        "T12",
        "T123",
        "T1234",
        "T12345",
        "T999999",
    ),
)
def test_validate_task_id_ok(task_id, allow_empty_identifiers):
    """It should not raise if the task_id is empty or valid."""
    if not task_id and not allow_empty_identifiers:
        pytest.skip("Skipping ok test for empty string with allow_empty_identifiers=False")

    assert phabricator.validate_task_id(task_id, allow_empty_identifiers=allow_empty_identifiers) == task_id


@pytest.mark.parametrize("allow_empty_identifiers", (True, False))
@pytest.mark.parametrize(
    "task_id",
    (
        "",
        "-",
        "T1a",
        "123",
        "T1234567",
    ),
)
def test_validate_task_id_fail(task_id, allow_empty_identifiers):
    """It should raise a ValueError if the task_id is invalid."""
    if not task_id and allow_empty_identifiers:
        pytest.skip("Skipping fail test for empty string with allow_empty_identifiers=True")

    with pytest.raises(
        ValueError,
        match=re.escape(rf"Invalid Phabricator task ID, expected to match pattern 'T\d{{1,6}}$', got '{task_id}'"),
    ):
        phabricator.validate_task_id(task_id)


class TestPhabricator:
    """Test class for the Phabricator class."""

    @mock.patch("wmflib.phabricator.phabricator.Phabricator")
    def setup_method(self, _, mocked_phabricator):
        """Setup the test environment."""
        # pylint: disable=attribute-defined-outside-init
        self.mocked_phabricator_client = mocked_phabricator()
        self.phab = phabricator.Phabricator(self.mocked_phabricator_client, dry_run=False)
        self.phab_allow_empty = phabricator.Phabricator(
            self.mocked_phabricator_client, dry_run=False, allow_empty_identifiers=True
        )
        self.task_comment_transactions = [{"type": "comment", "value": "new message"}]

    @pytest.mark.parametrize("raises", (True, False))
    @pytest.mark.parametrize(
        "data, expected",
        (
            ([], False),
            ([{"id": 12345, "type": "TASK"}], True),
            ([{"id": 12345, "type": "TASK"}, {"id": 123456, "type": "TASK"}], False),
        ),
    )
    def test_task_accessible_ok(self, data, expected, raises):
        """It should return True if a task on Phabricator is accessible given the current token."""
        mocked_results = mock.MagicMock(phabricator.phabricator.Result)
        mocked_results.data = data
        self.mocked_phabricator_client.maniphest.search.return_value = mocked_results
        assert self.phab.task_accessible("T12345", raises=raises) is expected
        self.mocked_phabricator_client.maniphest.search.assert_called_once_with(constraints={"ids": [12345]})

    @pytest.mark.parametrize("raises", (True, False))
    def test_task_accessible_empty_ok(self, raises):
        """It should return False if the task ID is empty and allow_empty_identifiers=True."""
        assert not self.phab_allow_empty.task_accessible("", raises=raises)
        self.mocked_phabricator_client.maniphest.search.assert_not_called()

    @pytest.mark.parametrize("task_id", ("", "T12345"))
    def test_task_accessible_fail_raise(self, task_id):
        """It should raise a PhabricatorError if unable to verify if the task is accessible."""
        self.mocked_phabricator_client.maniphest.search.side_effect = RuntimeError("Error")
        with pytest.raises(
            phabricator.PhabricatorError, match=f"Unable to determine if the task '{task_id}' is accessible"
        ):
            self.phab.task_accessible(task_id)

        if task_id:
            self.mocked_phabricator_client.maniphest.search.assert_called_once_with(constraints={"ids": [12345]})
        else:
            self.mocked_phabricator_client.maniphest.search.assert_not_called()

    @pytest.mark.parametrize("task_id", ("", "T12345"))
    def test_task_accessible_fail_no_raise(self, task_id, caplog):
        """It should log an error message if unable to verify if the task is accessible if raises=False."""
        self.mocked_phabricator_client.maniphest.search.side_effect = RuntimeError("Error")
        with caplog.at_level(logging.ERROR):
            assert not self.phab.task_accessible(task_id, raises=False)

        if task_id:
            self.mocked_phabricator_client.maniphest.search.assert_called_once_with(constraints={"ids": [12345]})
            message = "Error"
        else:
            self.mocked_phabricator_client.maniphest.search.assert_not_called()
            message = "Empty task ID"

        check_logs(
            caplog,
            f"Unable to determine if the task '{task_id}' is accessible (raises=False): {message}",
            logging.ERROR,
        )

    @pytest.mark.parametrize("raises", (True, False))
    def test_task_comment_ok(self, raises):
        """It should update a task on Phabricator."""
        self.phab.task_comment("T12345", "new message", raises=raises)
        self.mocked_phabricator_client.maniphest.edit.assert_called_once_with(
            objectIdentifier="T12345", transactions=self.task_comment_transactions
        )

    @pytest.mark.parametrize("raises", (True, False))
    def test_task_comment_dry_run(self, raises):
        """It should not update a task on Phabricator when in DRY-RUN mode."""
        phab = phabricator.Phabricator(self.mocked_phabricator_client)
        phab.task_comment("T12345", "new message", raises=raises)
        assert not self.mocked_phabricator_client.maniphest.edit.called

    @pytest.mark.parametrize("raises", (True, False))
    def test_task_comment_empty_task(self, raises):
        """It should not update a task on Phabricator if the task ID is empty and allow_empty_identifiers=True."""
        self.phab_allow_empty.task_comment("", "new message", raises=raises)
        assert not self.mocked_phabricator_client.maniphest.edit.called

    @pytest.mark.parametrize("task_id", ("", "T12345"))
    def test_task_comment_fail_raise(self, task_id):
        """It should raise PhabricatorError if the update operation fails."""
        self.mocked_phabricator_client.maniphest.edit.side_effect = RuntimeError
        with pytest.raises(phabricator.PhabricatorError, match=f"Unable to update Phabricator task '{task_id}'"):
            self.phab.task_comment(task_id, "new message")

        if task_id:
            self.mocked_phabricator_client.maniphest.edit.assert_called_once_with(
                objectIdentifier="T12345", transactions=self.task_comment_transactions
            )
        else:
            self.mocked_phabricator_client.maniphest.edit.assert_not_called()

    @pytest.mark.parametrize("task_id", ("", "T12345"))
    def test_task_comment_fail_no_raise(self, task_id, caplog):
        """It should not raise PhabricatorError but log a message if the update operation fails with raises=False."""
        self.mocked_phabricator_client.maniphest.edit.side_effect = RuntimeError
        with caplog.at_level(logging.ERROR):
            self.phab.task_comment(task_id, "new message", raises=False)

        check_logs(caplog, f"Unable to update Phabricator task '{task_id}' (raises=False)", logging.ERROR)
        if task_id:
            self.mocked_phabricator_client.maniphest.edit.assert_called_once_with(
                objectIdentifier="T12345", transactions=self.task_comment_transactions
            )
        else:
            self.mocked_phabricator_client.maniphest.edit.assert_not_called()
