from AviaxMusic.core.bot import Aviax
from AviaxMusic.core.dir import dirr
from AviaxMusic.core.git import git
from AviaxMusic.core.userbot import Userbot
from AviaxMusic.misc import dbb, heroku

from .logging import LOGGER

# Safe initialization
try:
    dirr()
except Exception as e:
    LOGGER(__name__).warning(f"dirr() failed: {e}")

try:
    git()
except Exception as e:
    LOGGER(__name__).warning(f"git() failed: {e}")

try:
    dbb()
except Exception as e:
    LOGGER(__name__).warning(f"dbb() failed: {e}")

try:
    heroku()
except Exception as e:
    LOGGER(__name__).warning(f"heroku() failed: {e}")

app = Aviax()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
