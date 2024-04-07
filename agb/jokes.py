import logging

import discord
from discord.ext import commands
import agb.requestHandler
import json
from nltk.corpus import words
import random
import cowsay
import agb.cogwheel

class jokesCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("jokesCog has been initalized.")

    @commands.slash_command(name="joke", description="I'm so funny, right?")
    async def _joke(self, interaction):
        r = agb.requestHandler.handler.get(agb.cogwheel.getAPIEndpoint("joke", "GET_JOKE"), attemptCache=False)
        joke = json.loads(r.text)

        embed = discord.Embed(title="Joke #{}".format(joke["id"]), description="{0}\n{1}".format(joke["setup"], joke["punchline"]))
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="wisdom", description="Get a word of wisdom")
    async def _wisdom(self, interaction):
        await interaction.response.send_message(random.choice(words.words()))

    @commands.slash_command(name="shakespeare", description="Shakespeare translator!")
    async def _shakespeare(self, interaction,
                           text: discord.Option(str, description="Text to translate!")):
        endpoint = agb.cogwheel.getAPIEndpoint("shakespeare", "TRANSLATE")
        if text[len(text) - 1] == " ":
            text[len(text) - 1] = ""
        text = text.lower()
        # following spaces so cache is possible lol
        r = agb.requestHandler.handler.get(endpoint + "?text=" + text)
        j = json.loads(r.text)
        await interaction.response.send_message(j['contents']["translated"])

    @commands.slash_command(name="hello", description="I'm polite, you know!")
    async def _hello(self, interaction):
        await interaction.response.send_message(":wave: Hi, {0}".format(interaction.user.mention))

    @commands.slash_command(name="dog", description="Get a dog picture!")
    async def _dog(self, interaction):
        endpoint = agb.cogwheel.getAPIEndpoint("dog", "GET_PICTURE")
        r = agb.requestHandler.handler.get(endpoint, attemptCache=False)
        embed = discord.Embed(title="Dog")
        url = json.loads(r.text)["message"]
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="dogbreed", description="Dog breeds :3")
    async def _dogbreeds(self, interaction):
        endpoint = agb.cogwheel.getAPIEndpoint("dog", "GET_BREEDS")
        r = agb.requestHandler.handler.get(endpoint)
        j = json.loads(r.text)
        a = list(j["message"].keys())
        breed = random.choice(list(a))
        await interaction.response.send_message(":dog: `{0}`".format(breed))

    @commands.slash_command(name="coinflip", description="Flip a coin!")
    async def _coinflip(self, interaction):
        await interaction.response.send_message(":coin: %s" % "Heads" if random.choice([True,False]) else "Tails")

    @commands.slash_command(name="cowsay", description="Linux cowsay command in Discord")
    async def _cowsay(self, interaction,
                      text: discord.Option(str, description="The text for the cow to say!"),
                      character: discord.Option(str, description="The character you want to use!",
                                                default="cow", choices=cowsay.char_names)):
        t = cowsay.get_output_string(character, text)
        if len(t) > 2000:
            await interaction.response.send_message(":x: Too long! ({0} > 2000)".format(len(t)))
            return
        await interaction.response.send_message("```\n{0}\n```".format(t))

