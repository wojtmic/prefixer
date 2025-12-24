import os

class DriveNotMappedError(Exception): pass

def resolve_path(pfx_path: str, windows_path: str):
    windows_path = windows_path.replace('\\', '/')

    if ':' not in windows_path: raise ValueError('Path must be absolute for Windows! (include a drive letter)')

    drive, tail = windows_path.split(':', 1)

    dosdevices = os.path.join(pfx_path, 'dosdevices')
    drive_link = os.path.join(dosdevices, f'{drive.lower()}:')

    if not os.path.exists(drive): raise DriveNotMappedError(f'Drive {drive} is not mapped in this prefix')

    root = os.path.realpath(drive_link)

    return os.path.join(root, tail)
