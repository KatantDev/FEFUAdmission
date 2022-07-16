from tortoise import fields, Model


class User(Model):
    id = fields.BigIntField(pk=True)
    status = fields.TextField()
    snils = fields.TextField(null=True)
    check_agreement = fields.BooleanField()
    notifications = fields.BooleanField()

    selected_faculties: fields.ReverseRelation["SelectedFaculty"]

    def __int__(self):
        return self.id


class Faculty(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=8)
    name = fields.TextField()

    def __int__(self):
        return self.id


class SelectedFaculty(Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='selected_faculties')
    faculty = fields.ForeignKeyField('models.Faculty', related_name='selected_faculties')
    place = fields.IntField(null=True)

    def __int__(self):
        return self.id


class Agreement(Model):
    id = fields.IntField(pk=True)
    snils = fields.TextField()
    faculty = fields.ForeignKeyField('models.Faculty', related_name='agreemenets')
