import discord
from discord.ext import commands
import json
import os

POINTS_FILE = "points.json"

ROLE_THRESHOLDS = [
    (500, "👑 Client VIP"),
    (200, "🥇 Client Or"),
    (100, "🥈 Client Argent"),
    (50, "🎖️ Client Bronze"),
    (0, "Membre"),
]

POINTS_COMMANDE = 50
POINTS_PHOTO = 30

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if os.path.exists(POINTS_FILE):
            with open(POINTS_FILE, "r") as f:
                self.points_data = json.load(f)
        else:
            self.points_data = {}

    def save_points(self):
        with open(POINTS_FILE, "w") as f:
            json.dump(self.points_data, f, indent=4)

    def get_role_by_points(self, guild, points):
        for threshold, role_name in ROLE_THRESHOLDS:
            if points >= threshold:
                return discord.utils.get(guild.roles, name=role_name)
        return None

    async def update_roles(self, member, points):
        guild = member.guild
        new_role = self.get_role_by_points(guild, points)
        if not new_role:
            return
        roles_to_remove = []
        for _, role_name in ROLE_THRESHOLDS:
            role = discord.utils.get(guild.roles, name=role_name)
            if role and role in member.roles and role != new_role:
                roles_to_remove.append(role)
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
        if new_role not in member.roles:
            await member.add_roles(new_role)

    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)

    @commands.command(name="commande")
    @is_admin()
    async def cmd_commande(self, ctx, member: discord.Member):
        user_id = str(member.id)
        self.points_data.setdefault(user_id, 0)
        self.points_data[user_id] += POINTS_COMMANDE
        self.save_points()
        await self.update_roles(member, self.points_data[user_id])
        await ctx.send(f"✅ {member.mention} a reçu +{POINTS_COMMANDE} points pour une commande validée. Total : {self.points_data[user_id]} pts.")

    @commands.command(name="photo")
    @is_admin()
    async def cmd_photo(self, ctx, member: discord.Member):
        user_id = str(member.id)
        self.points_data.setdefault(user_id, 0)
        self.points_data[user_id] += POINTS_PHOTO
        self.save_points()
        await self.update_roles(member, self.points_data[user_id])
        await ctx.send(f"📸 {member.mention} a reçu +{POINTS_PHOTO} points pour une photo validée. Total : {self.points_data[user_id]} pts.")

    @commands.command(name="points")
    async def cmd_points(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        user_id = str(member.id)
        pts = self.points_data.get(user_id, 0)
        await ctx.send(f"{member.mention} a actuellement **{pts} points**.")

    @commands.command(name="setpoints")
    @is_admin()
    async def cmd_setpoints(self, ctx, member: discord.Member, points: int):
        if points < 0:
            await ctx.send("❌ Les points ne peuvent pas être négatifs.")
            return
        user_id = str(member.id)
        self.points_data[user_id] = points
        self.save_points()
        await self.update_roles(member, points)
        await ctx.send(f"✅ Points de {member.mention} définis à {points} points.")

def setup(bot):
    bot.add_cog(Points(bot))
