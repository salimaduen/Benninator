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
server_id = int(os.getenv('SERVER_ID'))
the_benny_target: discord.Member
time_before: datetime

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


async def calculate_time():
    global time_before, the_benny_target, channel_id
    t = (datetime.now() - time_before).total_seconds()
    await Database().add_benny_log(time_in_seconds=t, discord_id=the_benny_target.id)
    time_before = None
    print(t)
    msg = f'TEST TEST \n<@{benny_id}> spent {t:.3} seconds muted'
    await client.get_channel(channel_id).send(msg)


@client.event
async def on_voice_state_update(member, before, after):
    global time_before
    global the_benny_target
    if the_benny_target:
        if not before.channel and member.id == the_benny_target.id:
            print('JOINED VOICE CHAT')
            if member.voice.self_deaf:
                time_before = datetime.now()

        if the_benny_target and member.id == benny_id:
            if before.channel and not after.channel:
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

    global the_benny_target, channel_id, server_id
    if message.author == client.user:
        return

    # TODO add method for showing leaderboards

    if message.content.startswith("$benny_target"):
        msg = message.content.split(' ')
        if len(msg) == 2 and len(msg[1]) == 21:
            curr_id = await get_discord_id(msg[1])
            member = client.get_guild(server_id).get_member(int(curr_id))
            if member:
                await add_gamer(member)
                await Database().make_new_benny_target(member.id)
                the_benny_target = member
                msg = f'The new target is <@{the_benny_target.id}>!'
                await client.get_channel(channel_id).send(msg)

    if message.content.startswith("$benny_who"):
        msg = ''
        if the_benny_target:
            msg = ''.join(['The current target is ', the_benny_target.name])
        else:
            msg = ''.join(['There is currently no target'])
        await client.get_channel(channel_id).send(msg)

    if message.content.startswith("$benny_clear"):
        msg = ''
        if the_benny_target:
            await Database().clear_benny_target()
            the_benny_target = None
            msg = ''.join(['The target has been cleared!'])
        else:
            msg = ''.join(['There was no target to clear!'])
        await client.get_channel(channel_id).send(msg)

    if message.content.startswith("$benny_help"):
        msg = '''
		List of commands:
	$benny_log - Prints the ten most recent benny logs
	$benny_total - Prints the total benny deafened time
	$benny_code - Prints the info for the source code
	$benny_clear - Clears the current target
	$benny_who - Prints the current target if any
	$benny_target - select a target by @
		      '''
        await client.get_channel(channel_id).send(msg)

    if message.content.startswith("$benny_log"):
        rows = await Database().get_benny_log(the_benny_target.id)
        if rows:
            final_rows = [f'THE TEN MOST RECENT LOGS FOR <@{the_benny_target.id}>:']
            for row in rows:
                curr = ''.join([row[0], ' | ', f'{str(row[1]):.4}', ' SECONDS'])
                final_rows.append(curr)

            f = '\n'.join(final_rows)
        else:
            f = 'No logs available at this moment'
        await client.get_channel(channel_id).send(f)

    if message.content.startswith("$benny_total"):
        t = await Database().get_total_time(the_benny_target.id)
        if t:
            t, total = t[0]
            msg = f'As of {t} <@{the_benny_target.id}> has been deafened for a total of {total:.3} seconds'
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

    global the_benny_target, voice_channels, server_id, time_before
    tracked_gamer = (await Database().get_tracked_gamer())
    if tracked_gamer:
        tracked_gamer = tracked_gamer[0]
        the_benny_target = client.get_guild(server_id).get_member(tracked_gamer)
        if the_benny_target.voice.self_deaf:
            time_before = datetime.now()
    else:
        the_benny_target = None


client.run(os.getenv('BOT_ID'))
