from database import Database


# method to add gamer to db
async def add_gamer(member, client):
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


async def convert_time(time_in_seconds):
    time_in_seconds = int(time_in_seconds)
    time_in_minutes, time_in_hours, time_in_days = 0, 0, 0
    total_time_str = f'{time_in_seconds} seconds'

    if time_in_seconds >= 60:
        time_in_minutes = time_in_seconds // 60
        time_in_seconds = time_in_seconds % 60
        total_time_str = f'{time_in_minutes} minutes, {time_in_seconds} seconds'

    if time_in_minutes >= 60:
        time_in_hours = time_in_minutes // 60
        time_in_minutes = time_in_minutes % 60
        total_time_str = f'{time_in_hours} hours, {time_in_minutes} minutes, {time_in_seconds} seconds'

    if time_in_hours >= 24:
        time_in_days = time_in_hours // 24
        time_in_hours = time_in_hours % 24
        total_time_str = f'{time_in_days} days, {time_in_hours} hours, {time_in_minutes} minutes, {time_in_seconds} seconds'
    return total_time_str
