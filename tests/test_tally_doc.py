"""Test TallyDoc model functionality."""

# Standard Python Libraries
from datetime import datetime

# cisagov Libraries
from cyhy_db.models.tally_doc import Counts, TallyDoc


async def test_tally_doc_creation():
    """Test TallyDoc creation."""
    tally_doc = TallyDoc(id="TALLY-TEST-1")
    await tally_doc.insert()
    fetched_doc = await TallyDoc.get(tally_doc.id)
    assert fetched_doc is not None
    assert fetched_doc.id == "TALLY-TEST-1"
    assert fetched_doc.counts == Counts()
    assert isinstance(fetched_doc.last_change, datetime)


async def test_tally_doc_last_change():
    """Test TallyDoc last_change update."""
    tally_doc = TallyDoc(id="TALLY-TEST-2")
    await tally_doc.save()
    initial_last_change = tally_doc.last_change

    # Save TallyDoc again to force the last_change timestamp to update
    await tally_doc.save()
    assert tally_doc.last_change > initial_last_change
