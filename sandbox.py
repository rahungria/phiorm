import phiorm


class Test(phiorm.models.PostgresModel):
    fields = dict(
        id=phiorm.models.IntField(primary_key=True),
        name=phiorm.models.StrField(default='nome'),
    )