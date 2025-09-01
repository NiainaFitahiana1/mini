import click
import asyncio
from sqlalchemy.future import select
from datetime import datetime
from ..db import engine, Base, AsyncSessionLocal
from ..models.user import User
from ..security import hash_password

@click.group()
def cli():
    """Commandes app"""
    pass

# -----------------------
# Init DB
# -----------------------
@cli.command("init-db")
@click.option("--with-user", is_flag=True, help="Créer aussi l'utilisateur par défaut")
def init_db(with_user):
    """Créer les tables SQLite et éventuellement l'utilisateur par défaut."""
    async def run():
        # Création des tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)   # ⚠️ reset complet
            await conn.run_sync(Base.metadata.create_all)

        # Création de l'utilisateur par défaut
        if with_user:
            async with AsyncSessionLocal() as session:
                user = await session.get(User, 1)
                if not user:
                    user = User(
                        id=1,
                        nom="Admin",
                        prenom="User",
                        email="admin@example.com",
                        password_hash=hash_password("admin123"),
                        bio="Utilisateur par défaut",
                        specialite="Backend",
                        lien_github="https://github.com/admin",
                        lien_avatar="https://example.com/avatar.png",
                        lien_portaljob="https://portaljob.mg/admin",
                        date_de_naissance=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),
                        disponibilite=True
                    )
                    session.add(user)
                    await session.commit()

    asyncio.run(run())
    click.echo("✅ Base de données initialisée.")
    if with_user:
        click.echo("👤 Utilisateur par défaut créé (admin@example.com / admin123)")

# -----------------------
# Set user (id=1)
# -----------------------
@cli.command("set-user")
@click.option("--nom", required=True)
@click.option("--prenom", required=True)
@click.option("--email", required=True)
@click.option("--password", required=True)
@click.option("--bio", default="")
@click.option("--specialite", default="")
@click.option("--avatar", "lien_avatar", default="")
@click.option("--github", "lien_github", default="")
@click.option("--linkedin", "lien_linkedin", default="")
@click.option("--dribbble", "lien_dribbble", default="")
@click.option("--portaljob", "lien_portaljob", default="")
@click.option("--telephone", default="")
@click.option("--adresse", default="")
@click.option("--date-naissance", default="", help="Format YYYY-MM-DD")
@click.option("--dispo/--no-dispo", "disponibilite", default=True)
def set_user(nom, prenom, email, password, bio, specialite,
             lien_avatar, lien_github, lien_linkedin, lien_dribbble, lien_portaljob,
             telephone, adresse, date_naissance, disponibilite):
    """Crée ou met à jour l'unique user (id=1)."""

    async def run():
        async with AsyncSessionLocal() as session:
            user = await session.get(User, 1)

            # Conversion date
            birth_date = None
            if date_naissance:
                try:
                    birth_date = datetime.strptime(date_naissance, "%Y-%m-%d").date()
                except ValueError:
                    click.echo("⚠️ Format de date invalide. Utiliser YYYY-MM-DD.")
                    return

            if not user:
                # Création
                user = User(
                    id=1,
                    nom=nom,
                    prenom=prenom,
                    email=email.lower().strip(),
                    password_hash=hash_password(password),
                    bio=bio,
                    specialite=specialite,
                    lien_avatar=lien_avatar,
                    lien_github=lien_github,
                    lien_linkedin=lien_linkedin,
                    lien_dribbble=lien_dribbble,
                    lien_portaljob=lien_portaljob,
                    telephone=telephone,
                    adresse=adresse,
                    date_de_naissance=birth_date,
                    disponibilite=disponibilite
                )
                session.add(user)
            else:
                # Mise à jour
                user.nom = nom
                user.prenom = prenom
                user.email = email.lower().strip()
                user.password_hash = hash_password(password)
                user.bio = bio
                user.specialite = specialite
                user.lien_avatar = lien_avatar
                user.lien_github = lien_github
                user.lien_linkedin = lien_linkedin
                user.lien_dribbble = lien_dribbble
                user.lien_portaljob = lien_portaljob
                user.telephone = telephone
                user.adresse = adresse
                user.date_de_naissance = birth_date
                user.disponibilite = disponibilite

            await session.commit()

    asyncio.run(run())
    click.echo("✅ Utilisateur unique mis en place.")
