import re
from typing import Optional

VERSION_MATCHER = re.compile(r'^v(\d+)\.(\d+)\.(\d+)-?((alpha|beta|rc)(\d+))?(-\d+-g[a-f0-9]{7,9}(-(wip|dirty))?)?$')
VALID_MODES = ('iota', 'pre', 'patch', 'minor', 'major', 'minor-iota', 'minor-rc', 'release')


class VersionMatchError(RuntimeError):
    def __init__(self, version):
        super().__init__('Unable to extract version information from supplied string')
        self._version = version

    @property
    def version(self):
        return self._version


def _validate_mode(mode: str):
    if mode not in VALID_MODES:
        raise RuntimeError('Incorrect mode {}. Choose on of: {}'.format(mode, ','.join(list(VALID_MODES))))


def _increment_pre(pre: str) -> Optional[str]:
    if pre == 'rc':
        return None
    elif pre == 'beta':
        return 'rc'
    elif pre == 'alpha':
        return 'beta'
    elif pre == 'rel':
        return 'alpha'


def next_version(version: str, mode: str) -> Optional[str]:
    # ensure the right mode has been chosen correctly
    _validate_mode(mode)

    # break down the existing version
    match = VERSION_MATCHER.match(version)

    # if the version string doesn't match up to what we are expecting then there is nothing that we can do
    if match is None:
        raise VersionMatchError(version)

    # extract the version configuration
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    pre = match.group(5) or 'rel'
    pre_version = int(match.group(6) or 0)

    # based on the mode update the version number
    if mode == 'major':
        major += 1
        minor = 0
        patch = 0
        pre = 'rel'
        pre_version = 0
    elif mode in ('minor', 'minor-iota', 'minor-rc'):
        minor += 1
        patch = 0
        if mode in ('minor-iota', 'minor-rc'):
            pre = 'rc' if mode == 'minor-rc' else 'alpha'
            pre_version = 1
        else:
            pre = 'rel'
            pre_version = 0
    elif mode == 'patch':
        patch += 1
        pre = 'rel'
        pre_version = 0
    elif mode == 'pre':
        if pre == 'rel' and pre_version == 0:
            pre = 'beta'
            patch += 1
        else:
            pre = _increment_pre(pre)

            # in the case when a version increment is valid tne we must exit accordingly
            if pre is None:
                return None

        pre_version = 1
    elif mode == 'iota':
        if pre_version == 0 and pre == 'rel':
            pre = 'alpha'
            pre_version = 1
            patch += 1
        else:
            pre_version += 1
    elif mode == 'release':
        if pre != 'rc':
            return None
        else:
            pre = 'rel'

    # finally, based on the updated information generate the new version information
    next_ver = 'v{}.{}.{}'.format(major, minor, patch)

    if pre != 'rel':
        next_ver += '-{}{}'.format(pre, pre_version)

    return next_ver
