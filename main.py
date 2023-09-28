from database import Database
from datetime import datetime
from dotenv import load_dotenv
import discord
import time
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

load_dotenv()

benny_id = os.getenv('TARGET_ID')
the_benny = False
is_benny_deaf = False
time_before = 0

voice_channels = []

async def is_benny_in_vc():
	global voice_channels, benny_id
	for channel in voice_channels:
		for member in channel.members:
			if member.id == benny_id:
				return True
	return False


async def calculate_time():
	global time_before, benny_id
	t = (datetime.now() - time_before).total_seconds()
	time_before = 0
	print(t)
	msg = f'TEST TEST \n<@{benny_id}> spent {t:.3} seconds muted'
	await client.get_channel(1156435514967212084).send(msg)


@client.event
async def on_voice_state_update(member, before, after):
	global time_before
	global the_benny, benny_id, is_benny_deaf
	if not the_benny and member.id == benny_id:
		the_benny = True
		print('JOINED VOICE CHAT')
		if member.voice.self_mute:
			time_before = datetime.now()

	if the_benny and member.id == benny_id:
		if not await is_benny_in_vc():
			the_benny = False
			print('LEFT VOICE CHAT')
			if before.self_mute and not after.self_mute:
				await calculate_time()
		else:
			if not before.self_mute and after.self_mute:
				print('MUTED')
				time_before = datetime.now()
			if before.self_mute and not after.self_mute:
				print('UNMUTED')
				await calculate_time()

@client.event
async def on_message(message):
	if message.author == client.user:
        	return

	if message.content.startswith("$benny_log"):
		rows = await Database().get_benny_log()
		final_rows = []
		for row in rows:
			curr = ''.join([row[0], ' | ', str(row[1]), ' SECONDS'])
			final_rows.append(curr)
		f = '\n'.join(final_rows)
		await client.get_channel(1156435514967212084).send(f)


@client.event
async def on_ready():
	print(f"THE BENNINATOR HAS STARTED")
	channels = client.get_all_channels()
	global the_benny, benny_id, the_benny_state, voice_channels, time_before
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
			if m.voice.self_mute:
				time_before = datetime.now()
				is_benny_deaf = True
			break


client.run(os.getenv('SERVER_ID'))
