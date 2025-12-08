class DirectPFXError(Exception):
    pass

class DPFXParsingError(DirectPFXError):
    pass

class DPFXWritingError(DirectPFXError):
    pass

class DPFXWineserverError(DirectPFXError):
    pass

class RegeditParsingError(DPFXParsingError):
    pass

class RegeditWritingError(DPFXWritingError):
    pass
