from peewee import *


class AgeCategories(Model):
    id = AutoField()
    from_age = IntegerField()
    to_age = IntegerField()

    class Meta:
        table_name = "age_category"
        database = SqliteDatabase('new_voice.db')


class Person(Model):
    id = AutoField()
    name = CharField()
    surname = CharField()
    sex = IntegerField()

    category_id = ForeignKeyField(AgeCategories, backref='persons')

    class Meta:
        database = SqliteDatabase('new_voice.db')


class Record(Model):
    id = AutoField(primary_key=True)
    person_id = ForeignKeyField(Person, backref='records')
    create_date = DateField()
    record = BlobField()
    info = TextField()
    F0 = FloatField()
    std_F = FloatField()
    Jloc = FloatField()
    Sloc = FloatField()
    MPT = FloatField()
    L = FloatField()

    class Meta:
        database = SqliteDatabase('new_voice.db')


class ReferenceValues(Model):
    category_id = ForeignKeyField(AgeCategories, backref='ref_values')
    sex = IntegerField(primary_key=True)

    F0 = FloatField()
    std_F = FloatField()
    Jloc = FloatField()
    Sloc = FloatField()
    MPT = FloatField()
    L = FloatField()

    class Meta:
        table_name = "reference_values"
        database = SqliteDatabase('new_voice.db')
