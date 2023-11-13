# https://github.com/anbuhckr/dblite

import aiosqlite
from async_class import AsyncObject

class aioDbLite(AsyncObject):
    async def __ainit__(self, db_name):
        self.conn = await aiosqlite.connect(f'data/{db_name}')
        self.cursor = await self.conn.cursor()

    async def create(self, table_name, **kwargs):
        data = ', '.join(f"{k} {v}" for k, v in kwargs.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({data})"
        await self.cursor.execute(query)
        await self.conn.commit()

    async def add(self, table_name, **kwargs):
        col = ', '.join(list(kwargs.keys()))
        val = ', '.join('?' * len(list(kwargs.values())))
        query = f"INSERT INTO {table_name} ({col}) VALUES ({val})"
        await self.cursor.execute(query, tuple(list(kwargs.values())))
        await self.conn.commit()

    async def remove(self, table_name, **kwargs):
        condition = ' AND '.join(f"{k} = ?" for k, _ in kwargs.items())
        query = f"DELETE FROM {table_name} WHERE {condition}"
        await self.cursor.execute(query, tuple(list(kwargs.values())))
        await self.conn.commit()

    async def select(self, table_name, data, **kwargs):
        condition = ' AND '.join(f"{k} = ?" for k, _ in kwargs.items())
        query = f"SELECT {data} FROM {table_name} WHERE {condition}"
        data = await self.cursor.execute(query, tuple(list(kwargs.values())))
        return await data.fetchall()

    async def close(self):
        try:
            await self.conn.close()
        except ValueError:            
            pass

    async def __aenter__(self):
        return self

    async def __aexit__(self):
        await self.close()