from marshmallow import Schema, fields, ValidationError, pre_load


class PutSchema(Schema):
    id = fields.Int(dump_only=True)
    ime = fields.Str()
    poddeonica = fields.Str()
    sirina = fields.Int()
    duzina_poddeonice = fields.Int()
    broj_traka = fields.Int()


class OstecenjeSchema(Schema):
    id = fields.Int(dump_only=True)
    #put = fields.Nested(PutSchema)
    tip_ostecenja = fields.Str()
    PSI_broj = fields.Int()
    stacionaza = fields.Str()
    kostanje = fields.Int()

class NestedOstecenjeSchema (OstecenjeSchema):
    put_id = fields.Int(required=True)
    #put = fields.Nested(PutSchema())

class NestedPutSchema(PutSchema):
    ostecenja = fields.List(fields.Nested(OstecenjeSchema))




class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    user = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
