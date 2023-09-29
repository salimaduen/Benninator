from database import Database
from datetime import datetime
from dotenv import load_dotenv
import discord
import time
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

load_dotenv()

benny_id = int(os.getenv('TARGET_ID'))
channel_id = int(os.getenv('CHANNEL_ID'))
the_benny_target = Target()
time_before = 0

voice_channels = []

# method to add gamer to db
async def add_gamer(member):
	if member == client.user:
		return
	curr_id = str(member.id)
	curr_name = member.name
	db = Database()
	if not await db.is_gamer_in_db(curr_id):
		await db.add_benny_gamer(curr_id, curr_name)
		await db.add_gamer_to_total_log(curr_id)


async def get_discord_id(string):
	id_string = ''
	for c in string:
		if c.isdigit():
			id_string = ''.join([id_string, c])
	return id_string


async def is_benny_in_vc():
	global voice_channels, benny_id
	for channel in voice_channels:
		for member in channel.members:
			if member.id == benny_id:
				return True
	return False


async def calculate_time():
	global time_before, benny_id, channel_id
	t = (datetime.now() - time_before).total_seconds()
	await Database().add_benny_log(t)
	time_before = 0
	print(t)
	msg = f'TEST TEST \n<@{benny_id}> spent {t:.3} seconds muted'
	await client.get_channel(channel_id).send(msg)


@client.event
async def on_voice_state_update(member, before, after):
	global time_before
	global the_benny, benny_id
	if not the_benny and member.id == benny_id:
		the_benny = True
		print('JOINED VOICE CHAT')
		if member.voice.self_deaf:
			time_before = datetime.now()

	if the_benny and member.id == benny_id:
		if not await is_benny_in_vc():
			the_benny = False
			print('LEFT VOICE CHAT')
			if before.self_deaf and not after.self_deaf:
				await calculate_time()
		else:
			if not before.self_deaf and after.self_deaf:
				print('DEAFENED')
				time_before = datetime.now()
			if before.self_deaf and not after.self_deaf:
				print('UNDEAFENED')
				await calculate_time()

@client.event
async def on_message(message):
	print(message.content[2:-1])
	global channel_id
	if message.author == client.user:
        	return


	# add method to target user
	if message.content.startswith("$benny_target"):
		msg = message.content.split(' ')
		if len(msg) == 2 and len(msg[1]) == 21:
			curr_id = await get_discord_id(msg[1])
			user = client.get_user(curr_id)
			print(curr_id)
			if user:
				pass
				#await add_gamer(user)


	if message.content.startswith("$benny_help"):
		msg = '''
		List of commands:
		$benny_log - Prints the ten most recent benny logs
		$benny_total - Prints the total benny deafened time
		$benny_code - Prints the info for the source code
		      '''
		await client.get_channel(channel_id).send(msg)

	if message.content.startswith("$benny_log"):
		rows = await Database().get_benny_log()
		if rows:
			final_rows = ['THE TEN MOST RECENT LOGS:']
			for row in rows:
				curr = ''.join([row[0], ' | ', f'{str(row[1]):.4}', ' SECONDS'])
				final_rows.append(curr)

			f = '\n'.join(final_rows)
		else:
			f = 'No logs available at this moment'
		await client.get_channel(channel_id).send(f)

	if message.content.startswith("$benny_total"):
		t = await Database().get_total_time()
		if t:
			t, total = t[0]
			msg = f'As of {t} <@{message.author.id}> has been deafened for a total of {total:.4} seconds'
		else:
			msg = 'No total time available at this moment'
		await client.get_channel(channel_id).send(msg)

	if message.content.startswith("$benny_code"):
		msg = f'''The benninator is an open source project.
		If you want to contribute just get the code from {os.getenv('GITHUB')}
			  '''
		await client.get_channel(channel_id).send(msg)


@client.event
async def on_ready():
	print(f"THE BENNINATOR HAS STARTED")

	channels = client.get_all_channels()
	global the_benny, benny_id, voice_channels, time_before
	m = None
	for channel in channels:
		if channel.type.name == 'voice':
			voice_channels.append(channel)
			for member in channel.members:
				if member.id == benny_id:
					the_benny = True
					m = member
					break
		if the_benny:
			print(m)
			if m.voice.self_deaf:
				time_before = datetime.now()
			break


client.run(os.getenv('SERVER_ID'))
