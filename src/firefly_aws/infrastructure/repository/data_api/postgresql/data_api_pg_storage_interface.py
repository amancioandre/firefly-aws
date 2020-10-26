from __future__ import annotations

from typing import Type

import firefly as ff
from firefly.infrastructure.repository.rdb_repository import Column, Index

from ..data_api_storage_interface import DataApiStorageInterface


class DataApiPgStorageInterface(DataApiStorageInterface):
    _sql_prefix = 'pg'

    def _get_table_indexes(self, entity: Type[ff.Entity]):
        schema, table = self._fqtn(entity).split('.')
        result = self._execute(*self._generate_query(entity, f'{self._sql_prefix}/get_indexes.sql', {
            'schema': schema,
            'table': table
        }))
        indexes = {}
        if result:
            for row in result:
                name = row['indexname']
                if name.endswith('_pkey'):
                    continue
                column = ''
                indexes[name] = Index(name=name, columns=[column], unique=('UNIQUE' in row['indexdef']))

        return indexes.values()

    def _get_table_columns(self, entity: Type[ff.Entity]):
        schema, table = self._fqtn(entity).split('.')
        result = self._execute(*self._generate_query(entity, f'{self._sql_prefix}/get_columns.sql', {
            'schema': schema,
            'table': table
        }))
        ret = []
        if result:
            for row in result:
                ret.append(Column(name=row['column_name'], type=row['data_type']))
        return ret

    @staticmethod
    def _substr(start: int, n: int):
        return f'SUBSTR(document::text, {start}, {n}) as document'

    @staticmethod
    def _cast_json():
        return '::json'

    @staticmethod
    def _cast_uuid():
        return '::uuid'
