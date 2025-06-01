import discord
from discord.ext import commands

ROLE_NON_MEMBRE = "Non Membre"
ROLE_MEMBRE = "Membre"
CANAL_REGLEMENT = "📜-reglement"
CANAL_BIENVENUE = "👋-bienvenue"
CANAL_POINTS = "📊-points"
CANAL_GESTION = "👮-gestion-commandes"

class ReglementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Accepter les règles", style=discord.ButtonStyle.success)
    async def accepter(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_membre = discord.utils.get(interaction.guild.roles, name=ROLE_MEMBRE)
        role_non_membre = discord.utils.get(interaction.guild.roles, name=ROLE_NON_MEMBRE)
        salon_bienvenue = discord.utils.get(interaction.guild.text_channels, name=CANAL_BIENVENUE)

        if role_membre:
            await interaction.user.add_roles(role_membre)
            if role_non_membre and role_non_membre in interaction.user.roles:
                await interaction.user.remove_roles(role_non_membre)

            await interaction.response.send_message("Tu as accepté les règles. Bienvenue ! 🎉", ephemeral=True)

            if salon_bienvenue:
                await salon_bienvenue.send(f"{interaction.user.mention}, bienvenue sur le serveur ! 🎉")

        else:
            await interaction.response.send_message("⚠️ Le rôle 'Membre' est introuvable, contacte un admin.", ephemeral=True)

class PointsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Afficher mes points", style=discord.ButtonStyle.primary, custom_id="show_points")
    async def show_points_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Récupérer le cog points pour accéder à points_data
        cog = interaction.client.get_cog("Points")
        if not cog:
            await interaction.response.send_message("Le système de points est indisponible.", ephemeral=True)
            return
        user_id = str(interaction.user.id)
        pts = cog.points_data.get(user_id, 0)
        await interaction.response.send_message(f"Tu as actuellement **{pts} points**.", ephemeral=True)

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        role_non_membre = discord.utils.get(guild.roles, name=ROLE_NON_MEMBRE)
        if role_non_membre:
            await member.add_roles(role_non_membre)
        channel = discord.utils.get(guild.text_channels, name=CANAL_REGLEMENT)
        if channel:
            await channel.send(f"Bienvenue {member.mention} ! Lis les règles et clique sur le bouton ci-dessous pour accéder au serveur.", view=ReglementView())

    @commands.command(name="regler")
    @is_admin()
    async def cmd_regler(self, ctx):
        await ctx.send("Clique sur le bouton ci-dessous pour accepter le règlement :", view=ReglementView())

    @commands.command(name="accepter")
    async def cmd_accepter(self, ctx):
        role_membre = discord.utils.get(ctx.guild.roles, name=ROLE_MEMBRE)
        role_non_membre = discord.utils.get(ctx.guild.roles, name=ROLE_NON_MEMBRE)
        salon_bienvenue = discord.utils.get(ctx.guild.text_channels, name=CANAL_BIENVENUE)

        if role_membre:
            await ctx.author.add_roles(role_membre)
            if role_non_membre and role_non_membre in ctx.author.roles:
                await ctx.author.remove_roles(role_non_membre)
            await ctx.send(f"{ctx.author.mention}, tu as maintenant accès au reste du serveur !")

            if salon_bienvenue:
                await salon_bienvenue.send(f"{ctx.author.mention}, bienvenue sur le serveur ! 🎉")

        else:
            await ctx.send("Le rôle 'Membre' n'existe pas, dis à l'admin de le créer.")

    @commands.command(name="postregles")
    @is_admin()
    async def cmd_postregles(self, ctx):
        regles_texte = """
📜・RÈGLES DU SERVEUR

🔹 Respect avant tout  
Sois respectueux avec chacun. Aucun propos haineux, raciste, sexiste, homophobe ou insultant ne sera toléré.

🚫 Pas de spam ni de pub non autorisée  
Le spam, flood, et publicité sans l’accord du staff sont interdits.

🗂️ Utilise les bons salons  
Chaque salon a une fonction. Merci de poster au bon endroit, pour garder le serveur clair.

🧨 Comportement toxique ou troll = sanction  
Provocations, troll, drama ou attitude toxique peuvent entraîner mute ou bannissement.

🔧 Pas de revente ou partage illégal de la tech  
Toute tentative de vente ou diffusion non autorisée de contenu sera sanctionnée par un ban immédiat.

👮 Respecte le staff  
Les décisions des modérateurs doivent être respectées. Si tu as un souci, ouvre un ticket calmement.

🎫 Passe par les tickets pour toute demande  
Que ce soit pour une question, un problème ou un achat, utilise le système de ticket.

📖 Lis les salons informatifs avant de poser une question  
De nombreuses réponses sont déjà disponibles. Merci de vérifier avant de demander.
"""
        await ctx.send(regles_texte, view=ReglementView())

    @commands.command(name="postpoints")
    @is_admin()
    async def cmd_postpoints(self, ctx):
        description = (
            "Voici le système de points de fidélité :\n"
            "✅ 1 commande validée = +50 points\n"
            "📸 1 photo de commande validée = +30 points\n\n"
            "Progression des rôles :\n"
            "• 0 pts : Membre\n"
            "• 50 pts : 🎖️ Client Bronze\n"
            "• 100 pts : 🥈 Client Argent\n"
            "• 200 pts : 🥇 Client Or\n"
            "• 500 pts : 👑 Client VIP\n\n"
            "Clique sur le bouton ci-dessous pour afficher tes points actuels."
        )
        await ctx.send(description, view=PointsView())

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # Restreindre commandes dans canal gestion sauf admins
        gestion_channel = discord.utils.get(ctx.guild.text_channels, name=CANAL_GESTION)
        if gestion_channel and ctx.channel == gestion_channel:
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ Tu ne peux pas utiliser les commandes ici.")
                ctx.command.reset_cooldown(ctx)
                raise commands.CheckFailure("Non admin dans canal gestion")

def setup(bot):
    bot.add_cog(Reglement(bot))
