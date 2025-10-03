class PrefixerError(Exception):
    pass

class NoSteamError(PrefixerError):
    pass

class NoTweakError(PrefixerError):
    pass

class NoPrefixError(PrefixerError):
    pass

class NoTaskError(PrefixerError):
    pass

class BadFileError(PrefixerError):
    pass

class BadDownloadError(PrefixerError):
    pass

class BadTweakError(PrefixerError):
    pass

class InternalExeError(PrefixerError):
    pass