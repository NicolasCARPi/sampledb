# coding: utf-8
"""

"""

import pytest
import sampledb
import sampledb.logic
import sampledb.models

from ..test_utils import flask_server, app, app_context

__author__ = 'Florian Rhiem <f.rhiem@fz-juelich.de>'


@pytest.fixture
def user1():
    user = sampledb.models.User(
        name="User",
        email="example1@fz-juelich.de",
        type=sampledb.models.UserType.PERSON)
    sampledb.db.session.add(user)
    sampledb.db.session.commit()
    return user


@pytest.fixture
def user2():
    user = sampledb.models.User(
        name="User",
        email="example2@fz-juelich.de",
        type=sampledb.models.UserType.PERSON)
    sampledb.db.session.add(user)
    sampledb.db.session.commit()
    return user


@pytest.fixture
def action():
    action = sampledb.logic.actions.create_action(
        action_type=sampledb.logic.actions.ActionType.SAMPLE_CREATION,
        name="",
        description="",
        schema={
            'title': 'Example Object',
            'type': 'object',
            'properties': {
            },
            'required': []
        }
    )
    return action


def test_get_user_log_entries(user1, user2, action):
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id)) == 0
    sampledb.logic.user_log.invite_user(user1.id, "example@fz-juelich.de")
    sampledb.logic.user_log.create_object(user1.id, 42)
    sampledb.logic.user_log.create_batch(user1.id, [42, 21])
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id)) == 3
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user1.id)) == 3
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user2.id)) == 0
    object = sampledb.logic.objects.create_object(action_id=action.id, data={}, user_id=user1.id)
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user1.id)) == 4
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user2.id)) == 0
    sampledb.logic.permissions.set_object_public(object_id=object.id, is_public=True)
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user1.id)) == 4
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user2.id)) == 1
    sampledb.logic.user_log.create_batch(user1.id, [object.id, 21])
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user1.id)) == 5
    assert len(sampledb.logic.user_log.get_user_log_entries(user1.id, as_user_id=user2.id)) == 2