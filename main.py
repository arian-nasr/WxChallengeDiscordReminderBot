import discord
import datetime
from discord.ext import tasks
import sqlite3
from sqlite3 import Error
from datetime import datetime
from os import getenv

client = discord.Client()


def create_database_connection(database_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param database_name: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(database_name)
    except Error as e:
        print(e)
    return conn


def query_database_for_reminders(current_time):
    """
    Query reminders by datetime
    :param current_time:
    :return:
    """
    conn = create_database_connection('reminders.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM reminders WHERE datetime=?", (current_time,))
    result = cur.fetchone()
    cur.execute("DELETE FROM reminders WHERE datetime=?", (current_time,))
    conn.commit()
    return result


@tasks.loop(seconds=20)
async def check_for_reminders():
    now = datetime.utcnow()
    current_time = f'{now.year},{now.month},{now.day},{now.hour},{now.minute}'
    reminders = query_database_for_reminders(current_time)
    if reminders:
        embed = discord.Embed(title="Link to submit forecast", url="https://www.wxchallenge.com/submit_forecast.php",
                              description="Don't forget to submit your forecast! You have 30 more minutes.",
                              color=0xff2600)
        embed.set_author(name="WxChallenge Reminder", url="https://www.wxchallenge.com/submit_forecast.php",
                         icon_url="https://www.wxchallenge.com/img/wxc_logo.png")
        channel = client.get_channel(841145714726010920)
        await channel.send(embed=embed)


@client.event
async def on_ready():
    check_for_reminders.start()


client.run(getenv('DISCORD_TOKEN'))
