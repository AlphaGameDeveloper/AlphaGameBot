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
import agb.cogwheel
from discord.ext import commands

class TestButtonView(discord.ui.View):
    def __init__(self, test):
        super().__init__()
        self.test = test

    

    @discord.ui.button(label="No",
                       style=discord.ButtonStyle.red)
    async def _no(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.questionNo()
        await self.test.nextQuestion()

    @discord.ui.button(label="Yes",
                       style=discord.ButtonStyle.green)
    async def _yes(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.questionYes()
        await self.test.nextQuestion()

class TestCompleteOptionView(discord.ui.View):
    def __init__(self, message: discord.Message, channel: discord.Thread):
        super().__init__()
        self.channel = channel
        self.message = message

    @discord.ui.button(label="Close Test",
                       style=discord.ButtonStyle.blurple)
    async def _close(self, button, interaction):
        # Close the thread in which the mbti test was preformed
        await self.channel.delete()

class MyersBriggsTypeIndicatorTest:
    def __init__(self, user):
        self.user = user # discord.User
        self.id = self.user.id
    
        self.key = {
            "I": "Introverted",
            "E": "Extraverted",
            "S": "Sensing",
            "N": "Intuitive",
            "T": "Thinking",
            "F": "Feeling",
            "P": "Prospecting",
            "J": "Judging"
        }

        self.stats = {
            "I": 0, # Introverted
            "E": 0, # Extraverted
            "S": 0, # Sensing (Observant)
            "N": 0, # Intuitive
            "T": 0, # Thinking
            "F": 0, # Feeling
            "P": 0, # Perceving (Prospecting)
            "J": 0  # Judging
        }
        self.currentquestion = 0
        self.thread = None 
        self.mbti = "XXXX"
        self.mbti_list = [None, None, None, None]
        self.QUESTIONS = [
            {
                "question": "I prefer to be around others usually.",
                "yes": "I",
                "no": "E"
            },
            {
                "question": "I get more energy from my close friends than other people.",
                "yes": "I",
                "no": "E"
            },
            {
                "question": "I always love when I'm the center of attention.",
                "yes": "E",
                "no": "I"
            },
            {
                "question": "I get anxious and overwhelmed if I'm in a crowd of people for long enough.",
                "yes": "I",
                "no": "E"
            },
            {
                "question": "I am quite popular in my respective social group.",
                "yes": "E",
                "no": "I"
            },
            {
                "question": "I like to participate in sports.",
                "yes": "S",
                "no": "N"
            },
            {
                "question": "I'm always thinking about other things when I do things.",
                "yes": "N",
                "no": "S"
            },
            {
                "question": "I'm able to think quickly in intense situations.",
                "yes": "S",
                "no": "N"
            },
            {
                "question": "I like to make up stories and realities in my head.",
                "yes": "N",
                "no": "S"
            },
            {
                "question": "I can tell very well what other people are thinking just by looking at them.",
                "yes": "N",
                "no": "S"
            },
            {
                "question": "I honor tradition.",
                "yes": "S",
                "no": "N"
            },
            {
                "question": "I prefer to use trusted methods than innovate.",
                "yes": "S",
                "no": "N"
            },
            {
                "question": "I like to come up with a lot of ideas",
                "yes": "N",
                "no": "S"
            },
            {
                "question": "I am good at puzzles.",
                "yes": "T",
                "no": "F"
            },
            {
                "question": "My emotions control me more than I control them.",
                "yes": "F",
                "no": "T"
            },
            {
                "question": "I tend to feel insecure/depressed often.",
                "yes": "F",
                "no": "T"
            },
            {
                "question": "I like to focus on science and the facts rather than my own beliefs.",
                "yes": "T",
                "no": "F"
            },
            {
                "question": "I always need someone to rely on for things.",
                "yes": "F",
                "no": "T"
            },
            {
                "question": "I like solutions that are efficient rather than ones that make people happy.",
                "yes": "T",
                "no": "F"
            },
            {
                "question": "I like to make a lot of backup plans to make sure there's a way for everything.",
                "yes": "J",
                "no": "P"
            },
            {
                "question": "I like to just do whatever I feel like doing instead of having a schedule.",
                "yes": "P",
                "no": "J"
            },
            {
                "question": "I am always organized with access to everything.",
                "yes": "J",
                "no": "P"
            },
            {
                "question": "I get distracted very easily.",
                "yes": "P",
                "no": "J"
            },
            {
                "question": "I usually do the bare minimum needed for things and not put in extra effort.",
                "yes": "P",
                "no": "J"
            }
        ]

        self.question = self.QUESTIONS[self.currentquestion]

    def questionYes(self):
        """Increments the score for the trait in the question for 'yes'"""
        self.stats[self.QUESTIONS[self.currentquestion]["yes"]] += 1

    def questionNo(self):
        """Increments the score for the trait in the question for 'no'"""
        self.stats[self.QUESTIONS[self.currentquestion]["no"]] += 1
        
    async def nextQuestion(self, advance=True):
        """Prepares and shows the next question"""
        if advance:
            self.currentquestion += 1
        if self.currentquestion >= len(self.QUESTIONS):
            await self.showResults()
            return
        self.question = self.QUESTIONS[self.currentquestion]

        await self.thread.send("{0}. {1}".format(self.currentquestion + 1, self.question["question"]), view=TestButtonView(self))

    async def showResults(self):
        """Displays the results to the user"""
        mbti = [None, None, None, None]
        
        # introverted or extraverted
        if self.stats["I"] >= self.stats["E"]:
            mbti[0] = "I"
        else:
            mbti[0] = "E"

        # intuitive or sensing
        if self.stats["S"] >= self.stats["N"]:
            mbti[1] = "S"
        else:
            mbti[1] = "N"
        
        # thinking or feeling
        if self.stats["F"] >= self.stats["T"]:
            mbti[2] = "F"
        else:
            mbti[2] = "T"
        
        # perceiving or judging
        if self.stats["P"] >= self.stats["J"]:
            mbti[3] = "P"
        else:
            mbti[3] = "J"

        
        mbti_string = "".join(mbti)
        self.mbti = mbti_string
        self.mbti_list = mbti
        embed = agb.cogwheel.Embed(title="Results", description="Your MBTI is: {0} *({1}, {2}, {3}, and {4})*".format(
            mbti_string,
            self.key[mbti_string[0]],
            self.key[mbti_string[1]],
            self.key[mbti_string[2]],
            self.key[mbti_string[3]]
        ))
        learnmore = "https://16personalities.com/{0}-personality".format(mbti_string.lower())
        await self.message.edit(embed=embed)
        view = TestCompleteOptionView(self.message, self.thread)
        learnmore_button = discord.ui.Button(label="Learn More!", style=discord.ButtonStyle.link, url=learnmore)
        view.add_item(learnmore_button)
        await self.thread.send(embed=embed, view=view)
        
    async def startTest(self,  interaction: discord.context.ApplicationContext):
        await interaction.response.send_message("**Please continue in the following thread.**")
        self.message = await interaction.channel.send("**%s's Myers-Briggs Type Indicator Test**" % self.user.name)
        self.thread = await self.message.create_thread(name="%s Myers-Briggs Type Indicator Test" % self.user.name, auto_archive_duration=60)
        await self.nextQuestion(advance=False)  # advance=False tells the function not to increase the question counter, as we are just starting.


# initalized into the bot by pycord - such a long class name lol
class MyersBriggsTypeIndicatorCog(agb.cogwheel.Cogwheel):
    @commands.slash_command(name="mbtitest", description="Take a Myers-Briggs type indicator test!")
    async def _mbtitest(self, interaction: discord.context.ApplicationContext):
        test = MyersBriggsTypeIndicatorTest(interaction.user)
        await test.startTest(interaction)
