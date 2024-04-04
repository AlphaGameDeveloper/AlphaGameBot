import discord
from discord.ext import commands
from mcstatus import JavaServer, BedrockServer
import logging
from socket import gaierror

from mcstatus.querier import QueryResponse

import agb.cogwheel


class MinecraftCog(discord.Cog):
    group = discord.SlashCommandGroup(name="minecraft", description="Minecraft-related commands")
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("MinecraftCog has been initialized!")

    @group.command(name="mcjava", description="Ping a Minecraft: Java Edition server amd get data!")
    async def _java(self, interaction,
                         host: discord.Option(str, description="The host IP address of the server"),
                         port: discord.Option(int, description="The port of the Minecraft server", default=25565)):
        if port == 25565:
            addr = "{0}".format(host)
        else:
            addr = "{0}:{1}".format(host, port)
        server = JavaServer.lookup(addr)
        await interaction.response.defer()
        try:
            status = server.status()
        except gaierror as e:  # socket.gaierror: [Errno -2] Name or service not known
            embed = agb.cogwheel.embed(title="Error!",
                                       description="The server data cannot be found!  Check the domain name and/or the port.\n\nThe reason for this is:\n`{0}`".format(
                                           repr(e)))
            embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft-error.png")
            await interaction.followup.send(embed=embed)
            return 1
        except TimeoutError as e:
            embed = agb.cogwheel.embed(title="Error!",
                                       description="The server timed out!\n`{0}`".format(repr(e)))
            embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft-error.png")
            await interaction.followup.send(embed=embed)
            return e

        enableQuery = False
        try:
            query = server.query()
            enableQuery = True
        except TimeoutError:
            pass

        online = status.players.online
        maximum = status.players.max
        latency = status.latency
        version = status.version.name
        protocol = status.version.protocol

        embed = agb.cogwheel.embed(title="Server info for {}".format(addr),
                                   description="Server information is limited as server disabled advanced query." if enableQuery == False else "")

        embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft.png")
        embed.add_field(name="Players Online", value="{0}/{1}".format(online, maximum))
        embed.add_field(name="Latency", value=round(latency/10, 2))
        embed.add_field(name="Version", value="{0} (Protocol {1})".format(version, protocol))
        embed.add_field(name="Secure Chat", value=str(status.enforces_secure_chat))
        if enableQuery:
            embed.add_field(name="Software", value="{0} {1}".format(query.software.brand, query.software.version))

        await interaction.followup.send(embed=embed)

    @group.command(name="mcbedrock", description="Ping a Minecraft: Bedrock Edition server and get data!")
    async def _bedrock(self, interaction,
                       host: discord.Option(str, description="The host IP of the Minecraft server"),
                       port: discord.Option(int, description="The port that the Minecraft server us running on",
                                            default=19132)):
        if port == 25565:
            addr = "{0}".format(host)
        else:
            addr = "{0}:{1}".format(host, port)
        server = BedrockServer.lookup(addr)
        await interaction.response.defer()
        try:
            status = server.status()
        except gaierror as e:  # socket.gaierror: [Errno -2] Name or service not known
            embed = agb.cogwheel.embed(title="Error!",
                                       description="The server data cannot be found!  Check the domain name and/or the port.\n\nThe reason for this is:\n`{0}`".format(
                                           repr(e)))
            embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft-error.png")
            await interaction.followup.send(embed=embed)
            return 1
        except TimeoutError as e:
            embed = agb.cogwheel.embed(title="Error!",
                                       description="The server timed out!\n`{0}`".format(repr(e)))
            embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft-error.png")
            await interaction.followup.send(embed=embed)
            return e

        embed = agb.cogwheel.embed(title="Server info for {0}".format(addr),
                                   description=status.description)
        embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft.png")

        online = status.players.online
        maximum = status.players.max
        version = status.version.name
        protocol = status.version.protocol
        mapname = status.map_name
        gamemode = status.gamemode
        # add info
        embed.add_field(name="Players online", value="{0}/{1}".format(online, maximum))
        embed.add_field(name="Version", value="{0} (Protocol {1})".format(version, protocol))
        embed.add_field(name="Map Name", value=mapname)
        embed.add_field(name="Gamemode", value=gamemode)

