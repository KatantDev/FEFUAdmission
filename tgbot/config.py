from dataclasses import dataclass
from environs import Env


@dataclass
class DbConfig:
    host: str
    port: int
    password: str
    user: str
    name: str


@dataclass
class TgBot:
    token: str
    use_redis: bool


@dataclass
class Misc:
    base_url: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Misc


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            use_redis=env.bool("USE_REDIS")
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            port=env.str('DB_PORT'),
            password=env.str('DB_PASSWORD'),
            user=env.str('DB_USER'),
            name=env.str('DB_NAME')
        ),
        misc=Misc(
            base_url=env.str('BASE_URL')
        )
    )
