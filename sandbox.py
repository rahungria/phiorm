import phiorm.models as models

class Test(models.PostgresModel):
    fields = dict(
        id=models.IntField(primary_key=True),
        name=models.StrField(default='nome'),
    )

Test.filter(id=1, name='cavalo')
Test.filter(id=1, name='trem')
