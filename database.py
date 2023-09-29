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
			self.conn.execute('PRAGMA foreign_keys = ON;')
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
	                discord_id INTEGER NOT NULL,
	                timestamp DATETIME UNIQUE DEFAULT (datetime('now', 'localtime')),
	                time_in_seconds REAL NOT NULL,
	  		FOREIGN KEY (discord_id) REFERENCES benny_gamers(discord_id)
          		 );
			 '''
		query3 = '''
			  CREATE TABLE IF NOT EXISTS log_total(
		          id INTEGER PRIMARY KEY AUTOINCREMENT,
		          discord_id INTEGER UNIQUE NOT NULL,
		          timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
		          time_in_seconds REAL NOT NULL DEFAULT 0.0,
		          FOREIGN KEY (discord_id) REFERENCES benny_gamers(discord_id)
	  	   	  );
			 '''

		try:
			self.cursor.execute(query)
			self.cursor.execute(query2)
			self.cursor.execute(query3)

			self.conn.commit()
			await self.close()

		except sqlite3.Error as e:
			print(e)

	async def update_total_log(self, time_in_seconds, discord_id):
		if not self.conn:
			await self.connect()
		try:
			self.cursor.execute(f'SELECT time_in_seconds FROM log_total WHERE discord_id = {discord_id};')
			curr_time = self.cursor.fetchall()[0][0]
			total_time = time_in_seconds + curr_time
			self.cursor.execute(f'''
					    UPDATE log_total
					    SET timestamp = \'{datetime.now()}\', time_in_seconds = {total_time} 
					    WHERE discord_id={discord_id};
					    ''')
		except sqlite3.Error as e:
			print(e)

	async def add_benny_log(self, time_in_seconds, discord_id):
		if not self.conn:
			await self.connect()
		query = f'''
			INSERT INTO benny_log(discord_id, time_in_seconds)
			VALUES ({discord_id}, {time_in_seconds})
			'''

		try:
			self.cursor.execute(query)
			await self.update_total_log(time_in_seconds, discord_id)
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)

	async def get_benny_log(self, discord_id):
		if not self.conn:
			await self.connect()
		query = f'''
			SELECT timestamp, time_in_seconds
			FROM benny_log
			WHERE discord_id = {discord_id}
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

	async def get_total_time(self, discord_id):
		if not self.conn:
			await self.connect()

		query = f'SELECT timestamp, time_in_seconds FROM log_total WHERE discord_id = {discord_id};'
		try:
			self.cursor.execute(query)
			rows = self.cursor.fetchall()
			await self.close()
			return rows
		except sqlite3.Error as e:
			print(e)

	async def add_benny_gamer(self, discord_id, username):
		if not self.conn:
			await self.connect()
		query = f'INSERT INTO benny_gamers(discord_id, username) VALUES (?, ?);'
		try:
			self.cursor.execute(query, (discord_id, username))
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)

	async def add_gamer_to_total_log(self, discord_id):
		if not self.conn:
			await self.connect()

		query = f'''INSERT INTO log_total(discord_id)
			VALUES ({discord_id});
			'''
		try:
			self.cursor.execute(query)
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)

	async def is_gamer_in_db(self, discord_id):
		if not self.conn:
			await self.connect()
		query = f'SELECT * from benny_gamers WHERE discord_id={discord_id}'
		try:
			self.cursor.execute(query)
			r = self.cursor.fetchone()
			await self.close()
			if r:
				return True

		except sqlite3.Error as e:
			print(e)
		return False

	async def get_tracked_gamer(self):
		if not self.conn:
			await self.connect()
		query = 'SELECT discord_id from benny_gamers WHERE is_tracked = true'
		try:
			self.cursor.execute(query)
			r = self.cursor.fetchone()
			await self.close()
			if r:
				return r
		except sqlite3.Error as e:
			print(e)
		return None

	async def make_new_benny_target(self, new_id):
		if not self.conn:
			await self.connect()

		query = 'SELECT discord_id from benny_gamers WHERE is_tracked = true'
		try:
			self.cursor.execute(query)
			r = self.cursor.fetchone()
			if r:
				self.cursor.execute('''UPDATE benny_gamers
				                    SET is_tracked = false
				                    WHERE discord_id = ?;
				                    ''', r)
			self.cursor.execute(f'''
					    UPDATE benny_gamers
					    SET is_tracked = true
					    WHERE discord_id = {new_id};
					    ''')
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)

	async def clear_benny_target(self):
		if not self.conn:
			await self.connect()

		try:
			self.cursor.execute('''
			UPDATE benny_gamers 
			SET is_tracked = false 
			WHERE is_tracked = true;''')
			self.conn.commit()
			await self.close()
		except sqlite3.Error as e:
			print(e)

