"""Test SystemControlDoc model functionality."""

# Standard Python Libraries
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

# Third-Party Libraries
import pytest

# cisagov Libraries
from cyhy_db.models.system_control_doc import SystemControlDoc
from cyhy_db.utils import utcnow


async def test_wait_for_completion_completed():
    """Test wait_for_completion when the document is completed."""
    document_id = "test_id"
    mock_doc = AsyncMock()
    mock_doc.completed = True

    with patch.object(SystemControlDoc, "get", return_value=mock_doc):
        result = await SystemControlDoc.wait_for_completion(document_id)
        assert result is True


async def test_wait_for_completion_timeout():
    """Test wait_for_completion when document is not completed before the timeout."""
    document_id = "test_id"
    mock_doc = AsyncMock()
    mock_doc.completed = False

    with patch.object(SystemControlDoc, "get", return_value=mock_doc):
        with patch(
            "cyhy_db.models.system_control_doc.monotonic",
            side_effect=[0, 10],
        ):
            result = await SystemControlDoc.wait_for_completion(document_id, timeout=5)
            assert result is False


async def test_wait_for_completion_no_timeout():
    """Test wait_for_completion when a timeout is not set."""
    document_id = "test_id"
    mock_doc = AsyncMock()
    mock_doc.completed = False

    async def side_effect(*args, **kwargs):
        if side_effect.call_count == 2:
            mock_doc.completed = True
        side_effect.call_count += 1
        return mock_doc

    side_effect.call_count = 0

    with patch.object(SystemControlDoc, "get", side_effect=side_effect):
        result = await SystemControlDoc.wait_for_completion(document_id)
        assert result is True


@pytest.mark.parametrize(
    "timeout,expected_sleeps", [(0, []), (-1, []), (1, [1]), (5, [5]), (6, [5, 1])]
)
@pytest.mark.parametrize("missing", [False, True])
async def test_polling_respects_timeout(timeout, expected_sleeps, missing):
    """Bound polling sleeps and treat zero as an immediate completion check."""
    elapsed = 0
    sleeps = []
    start = utcnow()
    document = None if missing else SimpleNamespace(completed=False)

    async def sleep(delay):
        nonlocal elapsed
        assert len(sleeps) < len(expected_sleeps), "Slept after the timeout expired"
        assert delay == expected_sleeps[len(sleeps)]
        sleeps.append(delay)
        elapsed += delay

    with (
        patch.object(SystemControlDoc, "get", return_value=document) as get,
        patch("cyhy_db.models.system_control_doc.asyncio.sleep", side_effect=sleep),
        patch(
            "cyhy_db.models.system_control_doc.monotonic",
            side_effect=lambda: elapsed,
            create=True,
        ),
        patch(
            "cyhy_db.models.system_control_doc.utcnow",
            side_effect=lambda: start + timedelta(seconds=elapsed),
        ),
    ):
        assert (
            await SystemControlDoc.wait_for_completion("test_id", timeout=timeout)
            is False
        )

    assert sleeps == expected_sleeps
    assert get.await_count == len(expected_sleeps) + 1


async def test_completed_document_with_zero_timeout():
    """A zero timeout still recognizes an already-completed document."""
    with (
        patch.object(
            SystemControlDoc, "get", return_value=SimpleNamespace(completed=True)
        ),
        patch("cyhy_db.models.system_control_doc.asyncio.sleep") as sleep,
    ):
        assert await SystemControlDoc.wait_for_completion("test_id", timeout=0) is True
    sleep.assert_not_awaited()
