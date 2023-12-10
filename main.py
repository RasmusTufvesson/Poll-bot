import discord, json
from discord import app_commands

with open("settings.json", "r") as f:
    settings: dict = json.load(f)

with open("allowed_members.json", "r") as f:
    allowed: list = json.load(f)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def gen_poll_message(se_text, se_desc, en_text, en_desc, pattern, proposed_by):
    return f"""# Röstning
{settings["ping_role"]}

## 🇸🇪 {se_text}
{se_desc}
## 🇬🇧 {en_text}
{en_desc}

Mönster/Pattern: {pattern}
Förslaget av/Proposed by: {proposed_by}"""

@tree.command(name = "poll", description = "Do a poll", guild=discord.Object(settings["guild_id"]))
async def create_poll(interaction: discord.Interaction, swedish_text: str, swedish_description: str, english_text: str, english_description: str, pattern: str, proposed_by: str):
    if interaction.user.id in allowed:
        await interaction.response.send_message(gen_poll_message(swedish_text, swedish_description, english_text, english_description, pattern, proposed_by))
        message = await interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    else:
        await interaction.response.send_message("Unauthorized", ephemeral=True)

@tree.command(name = "tally", description = "Tally results", guild=discord.Object(settings["guild_id"]))
async def tally(interaction: discord.Interaction, message_id: str):
    if interaction.user.id in allowed:
        message = await interaction.channel.fetch_message(int(message_id))
        thumbs_down = None
        thumbs_up = None
        for reaction in message.reactions:
            if reaction.emoji == "👍":
                thumbs_up = reaction.count
            elif reaction.emoji == "👎":
                thumbs_down = reaction.count
        content = message.content
        if thumbs_up > thumbs_down:
            content += f"\n\n# Resultat/Result\n**👍 {thumbs_up}** / 👎 {thumbs_down}"
        elif thumbs_down > thumbs_up:
            content += f"\n\n# Resultat/Result\n👍 {thumbs_up} / **👎 {thumbs_down}**"
        else:
            content += f"\n\n# Resultat/Result\n👍 {thumbs_up} / 👎 {thumbs_down}\n## Oavgjort/Tie"
        await message.edit(content=content)
        await interaction.response.send_message("Results tallied", ephemeral=True)
    else:
        await interaction.response.send_message("Unauthorized", ephemeral=True)

@tree.command(name = "add_allowed", description = "Add an allowed user", guild=discord.Object(settings["guild_id"]))
async def create_poll(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in allowed:
        allowed.append(user.id)
        with open("allowed_members.json", "w") as f:
            json.dump(allowed, f)
        await interaction.response.send_message("Added user", ephemeral=True)
    else:
        await interaction.response.send_message("Unauthorized", ephemeral=True)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(settings["guild_id"]))
    print("Ready!")

client.run(settings["token"])