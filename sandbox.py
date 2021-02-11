from phiorm.models.query.psqlQ import psqlQ
import phiorm.models as models

class Test(models.PostgresModel):
    fields = dict(
        id=models.IntField(primary_key=True),
        name=models.StrField(default='nome'),
    )


q = psqlQ(hope=None)
q = ~q
q.evaluate()
q = ~q
q.evaluate()

q1 = psqlQ(hope=None, id=2, carlos='carlos')
q1.evaluate()
Test.filter()
Test.filter(id=1)
Test.filter(id=2, name='cavalo')
