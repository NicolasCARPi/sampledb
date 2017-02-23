# coding: utf-8
"""

"""

import datetime
import json

import pytest
import sqlalchemy as db

import sampledb
from sampledb.object_database import datatypes, where_filters
from sampledb.object_database.versioned_json_object_tables import VersionedJSONSerializableObjectTables

__author__ = 'Florian Rhiem <f.rhiem@fz-juelich.de>'


class Object(VersionedJSONSerializableObjectTables.VersionedJSONSerializableObject):
    pass


@pytest.fixture
def engine():
    sampledb_app = sampledb.create_app()
    db_url = sampledb_app.config['SQLALCHEMY_DATABASE_URI']
    engine = db.create_engine(
        db_url,
        echo=False,
        json_serializer=lambda obj: json.dumps(obj, cls=datatypes.JSONEncoder),
        json_deserializer=lambda obj: json.loads(obj, object_hook=datatypes.JSONEncoder.object_hook)
    )

    # fully empty the database first
    db.MetaData(reflect=True, bind=engine).drop_all()
    return engine


@pytest.fixture
def objects(engine):
    objects = VersionedJSONSerializableObjectTables(
        'objects', object_type=Object
    )
    objects.bind = engine

    # create the object tables
    objects.metadata.create_all(engine)
    return objects


def test_text_equals(objects):
    objects.create_object({'t': datatypes.Text("Beispiel")}, user_id=0)
    object1 = objects.create_object({'t': datatypes.Text("Example")}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.text_equals(data['t'], 'Example'))


def test_text_contains(objects):
    objects.create_object({'t': datatypes.Text("Beispiel")}, user_id=0)
    object1 = objects.create_object({'t': datatypes.Text("Example")}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.text_contains(data['t'], 'amp'))


def test_boolean_equals(objects):
    object1 = objects.create_object({'b': datatypes.Boolean(True)}, user_id=0)
    object2 = objects.create_object({'b': datatypes.Boolean(False)}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.boolean_equals(data['b'], True))
    assert [object2] == objects.get_current_objects(lambda data: where_filters.boolean_equals(data['b'], False))


def test_boolean_true(objects):
    object1 = objects.create_object({'b': datatypes.Boolean(True)}, user_id=0)
    objects.create_object({'b': datatypes.Boolean(False)}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.boolean_true(data['b']))


def test_boolean_false(objects):
    objects.create_object({'b': datatypes.Boolean(True)}, user_id=0)
    object1 = objects.create_object({'b': datatypes.Boolean(False)}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.boolean_false(data['b']))


def test_quantity_equals(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'kilometer')}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_equals(data['q'], datatypes.Quantity(100, 'centimeters')))


def test_quantity_less_than(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'kilometer')}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_less_than(data['q'], datatypes.Quantity(1.5, 'meters')))


def test_quantity_less_than_equals(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'kilometer')}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_less_than_equals(data['q'], datatypes.Quantity(1, 'meter')))


def test_quantity_greater_than(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'centimeter')}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_greater_than(data['q'], datatypes.Quantity(0.5, 'meters')))


def test_quantity_greater_than_equals(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'centimeter')}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_greater_than_equals(data['q'], datatypes.Quantity(1, 'meter')))


def test_quantity_between(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'centimeter')}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_between(data['q'], datatypes.Quantity(10, 'centimeters'), datatypes.Quantity(1, 'meter')))
    assert [] == objects.get_current_objects(lambda data: where_filters.quantity_between(data['q'], datatypes.Quantity(10, 'centimeters'), datatypes.Quantity(1, 'second')))


def test_quantity_between_excluding(objects):
    object1 = objects.create_object({'q': datatypes.Quantity(1, 'meter')}, user_id=0)
    objects.create_object({'q': datatypes.Quantity(1, 'centimeter')}, user_id=0)
    assert [] == objects.get_current_objects(lambda data: where_filters.quantity_between(data['q'], datatypes.Quantity(10, 'centimeters'), datatypes.Quantity(1, 'meter'), including=False))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.quantity_between(data['q'], datatypes.Quantity(10, 'centimeters'), datatypes.Quantity(1.1, 'meter'), including=False))


def test_datetime_equals(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    objects.create_object({'dt': datatypes.DateTime(utc_datetime - datetime.timedelta(days=1))}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_equals(data['dt'], datatypes.DateTime(utc_datetime)))


def test_datetime_less_than(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    assert [] == objects.get_current_objects(lambda data: where_filters.datetime_less_than(data['dt'], datatypes.DateTime(utc_datetime)))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_less_than(data['dt'], datatypes.DateTime(utc_datetime + datetime.timedelta(seconds=1))))


def test_datetime_less_than_equals(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_less_than_equals(data['dt'], datatypes.DateTime(utc_datetime)))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_less_than_equals(data['dt'], datatypes.DateTime(utc_datetime + datetime.timedelta(seconds=1))))


def test_datetime_greater_than(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    assert [] == objects.get_current_objects(lambda data: where_filters.datetime_greater_than(data['dt'], datatypes.DateTime(utc_datetime)))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_greater_than(data['dt'], datatypes.DateTime(utc_datetime - datetime.timedelta(seconds=1))))


def test_datetime_greater_than_equals(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_greater_than_equals(data['dt'], datatypes.DateTime(utc_datetime)))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_greater_than_equals(data['dt'], datatypes.DateTime(utc_datetime - datetime.timedelta(seconds=1))))


def test_datetime_between(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    objects.create_object({'dt': datatypes.DateTime(utc_datetime - datetime.timedelta(days=1))}, user_id=0)
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_between(data['dt'], datatypes.DateTime(utc_datetime - datetime.timedelta(seconds=1)), datatypes.DateTime(utc_datetime)))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_between(data['dt'], datatypes.DateTime(utc_datetime - datetime.timedelta(seconds=1)), datatypes.DateTime(utc_datetime + datetime.timedelta(seconds=1))))


def test_datetime_between_excluding(objects):
    utc_datetime = datetime.datetime.utcnow()
    object1 = objects.create_object({'dt': datatypes.DateTime(utc_datetime)}, user_id=0)
    objects.create_object({'dt': datatypes.DateTime(utc_datetime - datetime.timedelta(days=1))}, user_id=0)
    assert [] == objects.get_current_objects(lambda data: where_filters.datetime_between(data['dt'], datatypes.DateTime(utc_datetime - datetime.timedelta(seconds=1)), datatypes.DateTime(utc_datetime), including=False))
    assert [object1] == objects.get_current_objects(lambda data: where_filters.datetime_between(data['dt'], datatypes.DateTime(utc_datetime - datetime.timedelta(seconds=1)), datatypes.DateTime(utc_datetime + datetime.timedelta(seconds=1)), including=False))
