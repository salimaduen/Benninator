from datetime import datetime
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
			CREATE TABLE IF NOT EXISTS benny_gamers(
             		discord_id INTEGER PRIMARY KEY,
             		username VARCHAR(50) UNIQUE NOT NULL,
             		is_tracked TINYINT NOT NULL DEFAULT FALSE
             		);
			'''

		query2 = '''
			CREATE TABLE IF NOT EXISTS benny_log(
	                id INTEGER PRIMARY KEY AUTOINCREMENT,
	                disord_id INTEGER,
	                timestamp DATETIME UNIQUE DEFAULT (datetime('now', 'localtime')),
	                time_in_seconds REAL NOT NULL,
	  		FOREIGN KEY (disord_id) REFERENCES benny_gamers(discord_id)
          		 );
			 '''
		query3 = '''
			  CREATE TABLE IF NOT EXISTS log_total(
		          id INTEGER PRIMARY KEY AUTOINCREMENT,
		          discord_id INTEGER,
		          timestamp DATETIME UNIQUE DEFAULT (datetime('now', 'localtime')),
		          time_in_seconds REAL NOT NULL,
		          FOREIGN KEY (discord_id) REFERENCES benny_gamers(discord_id)
	  	   	  );
			 '''
		query4 = '''
			 INSERT INTO log_total(id, time_in_seconds)
			 VALUES (1, 0.0);
			 '''

		try:
			self.cursor.execute(query)
			self.cursor.execute(query2)
			self.cursor.execute(query3)

			self.cursor.execute('SELECT * FROM log_total')
			if len(self.cursor.fetchall()) <= 0:
				self.cursor.execute(query4)
			self.conn.commit()
			await self.close()

		except sqlite3.Error as e:
			print(e)


	async def update_total_log(self, time_in_seconds):
		if not self.conn:
			await self.connect()
		try:
			self.cursor.execute('SELECT time_in_seconds FROM log_total WHERE id = 1;')
			curr_time = self.cursor.fetchall()[0][0]
			total_time = time_in_seconds + curr_time
			self.cursor.execute(f'''
					    UPDATE log_total
					    SET timestamp = \'{datetime.now()}\', time_in_seconds = {total_time} 
					    WHERE id=1;
					    ''')
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

		await self.update_total_log(time_in_seconds)

	async def get_benny_log(self):
		if not self.conn:
			await self.connect()
		query = '''
			SELECT timestamp, time_in_seconds
			FROM benny_log
			ORDER BY timestamp DESC
			LIMIT 10;
			'''

		try:
			self.cursor.execute(query)
			rows = self.cursor.fetchall()
			await self.close()
			return rows
		except sqlite3.Error as e:
			print(e)

	async def clear_benny_log(self):
		if not self.conn:
			await self.connect()

		try:
			self.cursor.execute('DELETE FROM benny_log')
			self.cursor.execute('DELETE FROM log_total')
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)

	async def get_total_time(self):
		if not self.conn:
			await self.connect()

		query = 'SELECT timestamp, time_in_seconds FROM log_total WHERE id = 1;'
		try:
			self.cursor.execute(query)
			rows = self.cursor.fetchall()
			await self.close()
			return rows
		except sqlite3.Error as e:
			print(e)
