import os

class DriveNotMappedError(Exception): pass

def resolve_path(pfx_path: str, windows_path: str):
    windows_path = windows_path.replace('\\', '/')

    if ':' not in windows_path: raise ValueError('Path must be absolute for Windows! (include a drive letter)')

    drive, tail = windows_path.split(':', 1)
    drive = drive.lower()
    tail = tail.lstrip('/')

    dosdevices = os.path.join(pfx_path, 'dosdevices')
    drive_link = os.path.join(dosdevices, f'{drive}:')

    if not os.path.lexists(drive_link): raise DriveNotMappedError(f'Drive {drive} is not mapped in this prefix')

    link_root = os.path.realpath(drive_link)

    return os.path.join(link_root, tail)
