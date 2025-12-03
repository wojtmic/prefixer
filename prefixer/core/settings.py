import os

NO_DOWNLOAD = os.environ.get('PF_NO_DOWNLOAD', 'false') == 'true'
SILENCE_EXTERNAL = os.environ.get('PF_SILENCE_EXTERNAL', 'false') == 'true'
ALLOW_SHELL = os.environ.get('PF_ALLOW_SHELL', 'false') == 'true'
