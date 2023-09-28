import sqlite3
import asyncio

class Database:
	def __init__(self, db_name='benny_base.db'):
		self.db_name = db_name
		self.conn = None
		self.cursor = None

	async def connect(self):
		try:
			self.conn = sqlite3.connect(self.db_name)
			self.cursor = self.conn.cursor()
		except sqlite3.Error as e:
			print(e)
		return self

	async def close(self):
		if self.conn:
			self.conn.close()
			self.conn = None
			self.cursor = None

	async def start_database(self):
		if not self.conn:
			await self.connect()
		query = '''
			CREATE TABLE IF NOT EXISTS benny_log(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp DATETIME UNIQUE DEFAULT (datetime('now', 'localtime')),
			time_in_seconds REAL NOT NULL
			);
			'''

		try:
			self.cursor.execute(query)
			self.conn.commit()
			await self.close()

		except sqlite3.Error as e:
			print(e)

	async def add_benny_log(self, time_in_seconds):
		if not self.conn:
			await self.connect()
		query = f'''
			INSERT INTO benny_log(time_in_seconds)
			VALUES ({time_in_seconds})
			'''

		try:
			self.cursor.execute(query)
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)


	async def get_benny_log(self):
		if not self.conn:
			await self.connect()
		query = '''
			SELECT timestamp, time_in_seconds FROM benny_log
			'''

		try:
			self.cursor.execute(query)
			rows = self.cursor.fetchall()
			return rows
		except sqlite3.Error as e:
			print(e)

	async def clear_benny_log(self):
		if not self.conn:
			await self.connect()

		try:
			self.cursor.execute('DELETE FROM benny_log')
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)
