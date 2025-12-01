import os

NO_DOWNLOAD = os.environ.get('NO_DOWNLOAD', 'false') == 'true'
SILENCE_EXTERNAL = os.environ.get('SILENCE_EXTERNAL', 'false') == 'true'
