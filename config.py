from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
APP_URL = env.str("APP_URL")
DB_URI = env.str("DB_URI")