"""Test SystemControlDoc model functionality."""

# Standard Python Libraries
from datetime import timedelta
from unittest.mock import AsyncMock, patch

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
    """Test wait_for_completion when the document is not completed before the timeout."""
    document_id = "test_id"
    mock_doc = AsyncMock()
    mock_doc.completed = False

    with patch.object(SystemControlDoc, "get", return_value=mock_doc):
        with patch(
            "cyhy_db.models.system_control_doc.utcnow",
            side_effect=[utcnow(), utcnow() + timedelta(seconds=10)],
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
