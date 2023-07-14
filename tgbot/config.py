from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    db_url: str


@dataclass
class TgBot:
    token: str
    admin_ids: list
    channel_id: str
    use_redis: bool


@dataclass
class Miscellaneous:
    didox_token_url: str
    didox_url: str
    didox_inn_url: str
    didox_pass: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            channel_id=env.str("CHANNEL_ID"),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            db_url=env.str("DB_URL")
        ),
        misc=Miscellaneous(didox_token_url=env.str("DIDOX_TOKEN_URL"),
                           didox_url=env.str("DIDOX_URL"),
                           didox_inn_url=env.str("DIDOX_INN_URL"),
                           didox_pass=env.str("DIDOX_PASS"))
    )
