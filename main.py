import discord, json
from discord import ui
from discord.commands import option
from os.path import isfile

if isfile("settings.json"):
    with open("settings.json", "r") as f:
        settings: dict = json.load(f)
else:
    settings = {"token": input("bot token: "), "guild_id": int(input("server id: ")), "ping_role": input("role to ping: ")}
    with open("settings.json", "w") as f:
        json.dump(settings, f)

if isfile("allowed_members.json"):
    with open("allowed_members.json", "r") as f:
        allowed: list = json.load(f)
else:
    allowed = [int(input("owner id: "))]
    with open("allowed_members.json", "w") as f:
        json.dump(allowed, f)

bot = discord.Bot()

def gen_poll_message(se_text, se_desc, en_text, en_desc, pattern, proposed_by):
    return f"""# Röstning
{settings["ping_role"]}

## 🇸🇪 {se_text}
{se_desc}
## 🇬🇧 {en_text}
{en_desc}

Mönster/Pattern: {pattern}
Förslaget av/Proposed by: {proposed_by}"""

@bot.slash_command(name = "poll", description = "Do a poll", guild_ids=[settings["guild_id"]])
@option(
    name = "proposed_by",
    description = "User that the poll was proposed by"
)
async def create_poll(ctx: discord.ApplicationContext, proposed_by: discord.Member):
    if ctx.user.id in allowed:
        await ctx.response.send_modal(CreatePollModal(proposed_by.mention, title="Create poll"))
    else:
        await ctx.response.send_message("Unauthorized", ephemeral=True)

class CreatePollModal(ui.Modal):
    def __init__(self, proposed_by, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(ui.InputText(label='Swedish text'))
        self.add_item(ui.InputText(label='Swedish description'))
        self.add_item(ui.InputText(label='English text'))
        self.add_item(ui.InputText(label='English description'))
        self.add_item(ui.InputText(label='Pattern'))
        self.proposed_by = proposed_by

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(gen_poll_message(self.children[0].value, self.children[1].value, self.children[2].value, self.children[3].value, self.children[4].value, self.proposed_by))
        message = await interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")

@bot.message_command(name = "tally", description = "Tally results", guild_ids=[settings["guild_id"]])
async def tally(interaction: discord.Interaction, message: discord.Message):
    if interaction.user.id in allowed:
        if message.author.id != bot.user.id:
            await interaction.response.send_message("Can only edit bot's messages", ephemeral=True)
            return
        thumbs_down = None
        thumbs_up = None
        for reaction in message.reactions:
            if reaction.emoji == "👍":
                thumbs_up = reaction.count
            elif reaction.emoji == "👎":
                thumbs_down = reaction.count
        if thumbs_down is None or thumbs_up is None:
            await interaction.response.send_message("No reactions to count", ephemeral=True)
            return
        content = message.content
        if thumbs_up > thumbs_down:
            content += f"\n\n# Resultat/Result\n**👍 {thumbs_up}** / 👎 {thumbs_down}"
        elif thumbs_down > thumbs_up:
            content += f"\n\n# Resultat/Result\n👍 {thumbs_up} / **👎 {thumbs_down}**"
        else:
            content += f"\n\n# Resultat/Result\n👍 {thumbs_up} / 👎 {thumbs_down}\n## Oavgjort/Tie"
        if len(content) > 2000:
            await interaction.response.send_message("Too many characters", ephemeral=True)
            return
        await message.edit(content=content)
        await interaction.response.send_message("Results tallied", ephemeral=True)
    else:
        await interaction.response.send_message("Unauthorized", ephemeral=True)

@bot.slash_command(name = "authorize", description = "Add an allowed user", guild_ids=[settings["guild_id"]])
@option(
    name = "user",
    description = "User to authorize"
)
async def add_allowed(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in allowed:
        if user.id in allowed:
            await interaction.response.send_message("Already authorized", ephemeral=True)
            return
        allowed.append(user.id)
        with open("allowed_members.json", "w") as f:
            json.dump(allowed, f)
        await interaction.response.send_message("Added user", ephemeral=True)
    else:
        await interaction.response.send_message("Unauthorized", ephemeral=True)

@bot.event
async def on_ready():
    print("Ready!")

bot.run(settings["token"])