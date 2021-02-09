import json
from pathlib import Path

from phiorm import exceptions
from . import model



class JSONModel(model.Model):
    pass

    # @classmethod
    # def _model_path(cls):
    #     return Path('.') / 'data'

    # @classmethod
    # def model_file(cls):
    #     try:
    #         return (
    #             f'{cls._model_path().absolute()}/'
    #             f'{cls.file}'
    #         )
    #     except AttributeError:
    #         raise AttributeError(
    #             'Models that inherit JSONModel must define a static '
    #             'field: "file" that contains the name json file '
    #             'to serialize and store the data. '
    #             'ex: "file = \'Person.json\'"'
    #         )

    # def save(self):
    #     if not self._model_path().exists():
    #         self._model_path().mkdir()
    #         with open(self.model_file(), 'w') as f:
    #             f.write('{}')

    #     all_lines = None
    #     with open(self.model_file(), 'r') as f:
    #         all_lines = f.read()

    #     _all = json.loads(all_lines or '{}')
    #     if str(self.pk()) not in _all:
    #         _all[str(self.pk())] = self.serialize()
    #     else:
    #         raise exceptions.ORMError(
    #             f'instance with pk: {self.pk()} already exists. '
    #             'Aborting...'
    #         )
    #     with open(self.model_file(), 'w') as f:
    #         f.write(json.dumps(_all))

    # @classmethod
    # def filter(cls, **kwargs):
    #     _all = None
    #     with open(cls.model_file(), 'r') as f:
    #         _all = f.read()

    #     if _all:
    #         _dict = json.loads(_all)
    #         filtered = []
    #         for entry in _dict:
    #             valid_keys = []
    #             for key in kwargs:
    #                 try:
    #                     value = _dict[entry][key]
    #                     valid_keys.append(bool(value == kwargs[key]))
    #                 except KeyError:
    #                     raise AttributeError(f'column: "{key}" not in model')
    #             if False not in valid_keys:
    #                 filtered.append(_dict[entry])
    #         return tuple(filtered)
    #     else:
    #         raise Exception('Database Empty!')
