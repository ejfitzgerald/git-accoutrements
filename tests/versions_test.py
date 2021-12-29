import pytest

from accoutrements.versions import next_version


@pytest.mark.parametrize("curr_version,mode,expected", [
    ("v0.0.3beta9-1-ga4578d1", 'iota', 'v0.0.3-beta10'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'iota', 'v0.0.3-beta10'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'iota', 'v0.0.3-beta10'),
    ('v10.12.13', 'iota', 'v10.12.14-alpha1'),
    ('v1.2.3alpha1', 'iota', 'v1.2.3-alpha2'),
    ('v1.2.3rc2-1-gabcdef1', 'iota', 'v1.2.3-rc3'),
    ('v0.0.1-3-gef14a4a', 'iota', 'v0.0.2-alpha1'),
    ('v0.1.0-42-g008b8c7b', 'iota', 'v0.1.1-alpha1'),

    ('v0.9.1-rc1', 'release', 'v0.9.1'),

    ("v0.0.3beta9-1-ga4578d1", 'minor-iota', 'v0.1.0-alpha1'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'minor-iota', 'v0.1.0-alpha1'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'minor-iota', 'v0.1.0-alpha1'),
    ('v10.12.13', 'minor-iota', 'v10.13.0-alpha1'),
    ('v1.2.3alpha1', 'minor-iota', 'v1.3.0-alpha1'),
    ('v1.2.3rc2-1-gabcdef1', 'minor-iota', 'v1.3.0-alpha1'),
    ('v0.0.1-3-gef14a4a', 'minor-iota', 'v0.1.0-alpha1'),
    ('v0.1.0-42-g008b8c7b', 'minor-iota', 'v0.2.0-alpha1'),

    ("v0.0.3beta9-1-ga4578d1", 'minor-rc', 'v0.1.0-rc1'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'minor-rc', 'v0.1.0-rc1'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'minor-rc', 'v0.1.0-rc1'),
    ('v10.12.13', 'minor-rc', 'v10.13.0-rc1'),
    ('v1.2.3alpha1', 'minor-rc', 'v1.3.0-rc1'),
    ('v1.2.3rc2-1-gabcdef1', 'minor-rc', 'v1.3.0-rc1'),
    ('v0.0.1-3-gef14a4a', 'minor-rc', 'v0.1.0-rc1'),
    ('v0.1.0-42-g008b8c7b', 'minor-rc', 'v0.2.0-rc1'),

    ("v0.0.3beta9-1-ga4578d1", 'pre', 'v0.0.3-rc1'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'pre', 'v0.0.3-rc1'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'pre', 'v0.0.3-rc1'),
    ('v10.12.13', 'pre', 'v10.12.14-beta1'),
    ('v1.2.3alpha1', 'pre', 'v1.2.3-beta1'),
    ('v1.2.3rc2-1-gabcdef1', 'pre', None),
    ('v0.0.1-3-gef14a4a', 'pre', 'v0.0.2-beta1'),
    ('v0.1.0-42-g008b8c7b', 'pre', 'v0.1.1-beta1'),

    ("v0.0.3beta9-1-ga4578d1", 'patch', 'v0.0.4'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'patch', 'v0.0.4'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'patch', 'v0.0.4'),
    ('v10.12.13', 'patch', 'v10.12.14'),
    ('v1.2.3alpha1', 'patch', 'v1.2.4'),
    ('v1.2.3rc2-1-gabcdef1', 'patch', 'v1.2.4'),
    ('v0.0.1-3-gef14a4a', 'patch', 'v0.0.2'),
    ('v0.1.0-42-g008b8c7b', 'patch', 'v0.1.1'),

    ("v0.0.3beta9-1-ga4578d1", 'minor', 'v0.1.0'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'minor', 'v0.1.0'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'minor', 'v0.1.0'),
    ('v10.12.13', 'minor', 'v10.13.0'),
    ('v1.2.3alpha1', 'minor', 'v1.3.0'),
    ('v1.2.3rc2-1-gabcdef1', 'minor', 'v1.3.0'),
    ('v0.0.1-3-gef14a4a', 'minor', 'v0.1.0'),
    ('v0.1.0-42-g008b8c7b', 'minor', 'v0.2.0'),

    ("v0.0.3beta9-1-ga4578d1", 'major', 'v1.0.0'),
    ('v0.0.3beta9-1-ga4578d1-wip', 'major', 'v1.0.0'),
    ('v0.0.3-beta9-1-ga4578d1-dirty', 'major', 'v1.0.0'),
    ('v10.12.13', 'major', 'v11.0.0'),
    ('v1.2.3alpha1', 'major', 'v2.0.0'),
    ('v1.2.3rc2-1-gabcdef1', 'major', 'v2.0.0'),
    ('v0.0.1-3-gef14a4a', 'major', 'v1.0.0'),
    ('v0.1.0-42-g008b8c7b', 'major', 'v1.0.0'),
])
def test_next_version(curr_version, mode, expected):
    assert next_version(curr_version, mode) == expected
