#    AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
#    Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)

#    AlphaGameBot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    AlphaGameBot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.

import discord
from discord.ext import commands
import os
import nltk
import logging
import logging.config
import agb.cogwheel
import sys
from dotenv import load_dotenv
from aiohttp import client_exceptions
import datetime
import argparse
import mysql.connector
# system
import agb.system.commandError
import agb.system.message
# commands
import agb.userstats
import agb.utility
import agb.xkcd
import agb.memes
import agb.jokes
import agb.jojo
import agb.rps
import agb.minecraft
import agb.google
import agb.moderation
import agb.fun
import agb.botinfo

import agb.rssFeedCog
import agb.suntsu 
import agb.myersbriggs
import agb.wikipedia
import agb.mathematics
import agb.dog
import agb.cat
# import agb.hyrule
# - - - - - - - - - - - - - - - - - - - - - - -
# if you wanna set custom logging configs i guess
# this is in .gitignore and .dockerignore because
# not everyone needs it, and if they do, it will
# be automatically loaded. :) --Damien 12.22.23
# TODO: Add base logging.cfg for people to copy
logging.config.fileConfig("logging.ini")
#logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.all()

SAY_EXCEPTIONS = [
    1180023544042770533, # The Nerds with No Life
    1179187852601479230  # AlphaGameDeveloper
]
OWNER = os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690)

global cogw, listener
cogw = logging.getLogger("cogwheel")
listener = logging.getLogger("listener")
#if os.getenv("DEBUG") != None:
#    logging.basicConfig(level=logging.DEBUG)
#else:
#    logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="?", intents=intents)

# parsing command line arguments
if __name__ == "__main__":
    d = datetime.date.today()
    parser = argparse.ArgumentParser(
        prog="AlphaGameBot Discord Bot",
        description="A Discord Bot that's free and (hopefully) doesn't suck.",
        epilog=f"(c) Damien Boisvert (AlphaGameDeveloper) {d.year}.  Licensed under GNU GPL v3"
    )
    parser.add_argument("-d", "--debug", help="Enable debug mode for the bot.", action="store_true")
    parser.add_argument("-e", "--environment", help="Automatically load a environment file for the bot.")
    parser.add_argument("-t", "--token", help="Set the bot's token via the command line. (Not recommended)")
    parser.add_argument("-n", "--nodatabase", help="Force database to be disabled regardless of environment", action="store_true")
    args = parser.parse_args()

@bot.event
async def on_ready():
    if agb.cogwheel.isDebugEnv:
        game_name = os.getenv("DISCORD_STATUS", "Whack A Bug!")
    else:
        logging.debug("note: Using debug Discord activity")
        game_name = os.getenv("DISCORD_STATUS", "With the Discord API.")
    
    status = discord.Game(game_name)
    await bot.change_presence(activity=status)
    logging.info(f"Set the bot's Discord activity to playing \"{game_name}\".")
    bot.auto_sync_commands = True
    logging.info("Bot is now ready!")
    logging.info("Bot user is \"{0}\". (ID={1})".format(bot.user.name, bot.user.id))

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: discord.DiscordException):
    listener.error("Error in slash command /{0} - \"{1}\"".format(interaction.command, repr(error)))
    # Essentially a proxy function
    return await agb.system.commandError.handleApplicationCommandError(interaction, error)


@bot.listen()
async def on_application_command(ctx: discord.ApplicationContext):
    listener.info("Command Called: /{0}".format(ctx.command.name))
    if CAN_USE_DATABASE:
        # attempt to make a new user if not already in the database
        agb.cogwheel.initalizeNewUser(cnx, ctx.author.id)

        # Increase the value of commands_ran by 1 for the given user id
        query = "UPDATE user_stats SET commands_ran = commands_ran + 1 WHERE userid = %s"
        values = [ctx.author.id]
        cursor = cnx.cursor()
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()


@bot.event
async def on_message(ctx: discord.Message):
    # Essentially a proxy function
    return await agb.system.message.handleOnMessage(ctx, CAN_USE_DATABASE, cnx)

MYSQL_SERVER = os.getenv("MYSQL_HOST", False)
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", False)
MYSQL_USER = os.getenv("MYSQL_USER", False)
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", False)

if not (MYSQL_SERVER and MYSQL_DATABASE and MYSQL_USER and MYSQL_PASSWORD) and not args.nodatabase:
    logging.warning("MySQL connection information is invalid!  MySQL connection is required to use specific commands.")
    logging.warning("These environment variables must be set:")
    logging.warning("* MYSQL_HOST")
    logging.warning("* MYSQL_DATABASE")
    logging.warning("* MYSQL_USER")
    logging.warning("* MYSQL_PASSWORD")
    CAN_USE_DATABASE = False
    cnx = None
elif args.nodatabase:
    logging.warning("Database was force-disabled with '-n' or '--nodatabase'.  Database functionality is DISABLED.")
    CAN_USE_DATABASE = False
    cnx = None
else:
    CAN_USE_DATABASE = True
    cnx = mysql.connector.connect(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_SERVER,
        database=MYSQL_DATABASE
    )
# set command cogs
bot.add_cog(agb.utility.UtilityCog(bot))
bot.add_cog(agb.xkcd.xkcdCog(bot))
bot.add_cog(agb.memes.MemesCog(bot))
bot.add_cog(agb.jokes.jokesCog(bot))
bot.add_cog(agb.jojo.JojoCog(bot))
bot.add_cog(agb.rps.rpsCog(bot))
bot.add_cog(agb.minecraft.MinecraftCog(bot))
bot.add_cog(agb.moderation.ModerationCog(bot))
bot.add_cog(agb.rssFeedCog.RSSFeedCog(bot))
bot.add_cog(agb.fun.FunCog(bot))
bot.add_cog(agb.botinfo.BotInformationCog(bot))
bot.add_cog(agb.suntsu.SunTsuCog(bot))
bot.add_cog(agb.myersbriggs.MyersBriggsTypeIndicatorCog(bot))
bot.add_cog(agb.wikipedia.WikipediaCog(bot))
bot.add_cog(agb.mathematics.MathematicsCog(bot))
bot.add_cog(agb.dog.DogCog(bot))
bot.add_cog(agb.cat.CatCog(bot))
bot.add_cog(agb.userstats.UserStatsCog(bot, cnx, CAN_USE_DATABASE))
# bot.add_cog(agb.hyrule.HyruleCog(bot))
# don't want to put half-working code in production
# Uncomment this line if you want to use the /google
# command.

# bot.add_cog(agb.google.GoogleCog(bot))

if __name__ == "__main__":
    logging.info("Starting the bot...")
    token = os.getenv("TOKEN")
    tokenSource = "environment"

    if args.environment != None:
        logging.info("Loading the %s environment file because it was explicitly requested with '-e' or '--environment'." % args.environment)
        if not os.path.isfile(args.environment):
            logging.fatal("The environment file %s does not exist!  Please check the path and try again." % args.environment)
            sys.exit(1)
        if not load_dotenv(args.environment):
            logging.info("No (new) environment variables were loaded from the .env file.  This is normal if the file does not exist.")
        token = os.getenv("TOKEN")
        tokenSource = "environmentfile"

    if args.token:
        logging.warning("You tried to use the command line to set the bot's token.  This is insecure.  Please use the environment variable 'TOKEN' instead.")
        token = args.token
        tokenSource = "commandline"

    if token == None or token == "":
        logging.error("No token was given via the environment variable 'TOKEN', nor was one given via the commandline using '-t' or '--token'!")
        logging.error("Use '-e' or '--environment' to automatically load your .env file.")
        sys.exit(1)



    if agb.cogwheel.isDebug(argp=args) == True:
        logging.warning("Debug mode is ENABLED.  This is a development build.  Do not use this in a production environment.")
    
    try:
        logging.info("Logging in using static token from %s" % tokenSource)
        bot.run(token)
    except client_exceptions.ClientConnectorError as e:
        logging.fatal("Cannot connect to Discord's gateway!")
        logging.fatal("Maybe check your internet connection?")
        sys.exit(1)
    except discord.errors.LoginFailure as e:
        logging.fatal("LoginFailure: Invalid token given.  Please check the token and try again.")
        sys.exit(1)
    except Exception as e:
        logging.fatal("The bot has encountered a critical error and cannot continue.")
        logging.fatal("This is an uncaught exception on the bot run command.")
        logging.fatal("--- Here is some error information ---")
        logging.fatal("Error Type: %s" % str(type(e).__name__))
        logging.fatal("Error Message: %s" % repr(e))
        sys.exit(1)