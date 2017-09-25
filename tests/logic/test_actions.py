# coding: utf-8
"""

"""

import pytest
import sampledb
from sampledb.logic import actions, errors, instruments, schemas

from ..test_utils import app_context

SCHEMA = {
        'title': 'Example Action',
        'type': 'object',
        'properties': {
            'example': {
                'title': 'Example Attribute',
                'type': 'text'
            }
        }
    }

def test_create_independent_action():
    assert len(actions.get_actions()) == 0
    action = actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA)
    assert action.name == "Example Action"
    assert action.description == ""
    assert action.schema == SCHEMA
    assert len(actions.get_actions()) == 1
    assert action == actions.get_action(action_id=action.id)


def test_create_instrument_action():
    instrument = instruments.create_instrument("Example Instrument", "Example Instrument Description")
    assert len(actions.get_actions()) == 0
    action = actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA, instrument_id=instrument.id)
    assert action.name == "Example Action"
    assert action.description == ""
    assert action.schema == SCHEMA
    assert len(actions.get_actions()) == 1
    assert action == actions.get_action(action_id=action.id)
    assert action.instrument == instrument


def test_create_missing_instrument_action():
    instrument = instruments.create_instrument("Example Instrument", "Example Instrument Description")
    assert len(actions.get_actions()) == 0
    with pytest.raises(errors.InstrumentDoesNotExistError):
        actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA, instrument_id=instrument.id+1)


def test_create_action_invalid_schema():
    schema = {
        'type': 'invalid'
    }
    with pytest.raises(errors.ValidationError):
        actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=schema)


def test_get_missing_action():
    assert len(actions.get_actions()) == 0
    action = actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA)
    with pytest.raises(errors.ActionDoesNotExistError):
        actions.get_action(action.id+1)


def test_update_action():
    action = actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA)
    actions.update_action(action_id=action.id, name="Test", description="desc", schema=SCHEMA)
    action = actions.get_action(action_id=action.id)
    assert action.name == "Test"
    assert action.description == "desc"
    assert action.schema == SCHEMA


def test_update_missing_action():
    action = actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA)
    with pytest.raises(errors.ActionDoesNotExistError):
        actions.update_action(action_id=action.id+1, name="Test", description="desc", schema=SCHEMA)


def test_get_actions():
    measurement_action = actions.create_action(sampledb.models.ActionType.MEASUREMENT, name="Example Action", description="", schema=SCHEMA)
    sample_action = actions.create_action(sampledb.models.ActionType.SAMPLE_CREATION, name="Example Action", description="", schema=SCHEMA)
    assert actions.get_actions() == [measurement_action, sample_action] or actions.get_actions() == [sample_action, measurement_action]
    assert actions.get_actions(sampledb.models.ActionType.SAMPLE_CREATION) == [sample_action]
    assert actions.get_actions(sampledb.models.ActionType.MEASUREMENT) == [measurement_action]