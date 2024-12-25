use anyhow::{anyhow, bail, Error};
use regex::Regex;
use std::fmt::Display;

#[derive(Debug)]
pub enum Increment {
    Major,
    Minor,
    Patch,
    Pre,
    Iota,
}

impl TryFrom<&str> for Increment {
    type Error = Error;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        match value {
            "major" => Ok(Self::Major),
            "minor" => Ok(Self::Minor),
            "patch" => Ok(Self::Patch),
            "pre" => Ok(Self::Pre),
            "iota" => Ok(Self::Iota),
            _ => Err(anyhow!("Unknown increment")),
        }
    }
}

#[derive(Copy, Clone, Debug)]
pub enum PreRelease {
    Alpha,
    Beta,
    ReleaseCandidate,
}

impl Display for PreRelease {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Alpha => write!(f, "alpha"),
            Self::Beta => write!(f, "beta"),
            Self::ReleaseCandidate => write!(f, "rc"),
        }
    }
}

impl TryFrom<&str> for PreRelease {
    type Error = Error;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        match value {
            "alpha" => Ok(Self::Alpha),
            "beta" => Ok(Self::Beta),
            "rc" => Ok(Self::ReleaseCandidate),
            _ => Err(anyhow!("Unknown pre-release code")),
        }
    }
}

#[derive(Copy, Clone, Debug)]
pub struct PreReleaseInfo {
    pre_release: PreRelease,
    number: usize,
}

impl Display for PreReleaseInfo {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}.{}", self.pre_release, self.number)
    }
}

#[derive(Debug)]
pub struct Version {
    major: usize,
    minor: usize,
    patch: usize,
    pre_release: Option<PreReleaseInfo>,
}

impl Version {
    pub fn increment(&self, increment: Increment) -> anyhow::Result<Version> {
        let mut major = self.major;
        let mut minor = self.minor;
        let mut patch = self.patch;
        let mut pre_release: Option<PreReleaseInfo> = None;

        match increment {
            Increment::Major => {
                major += 1;
                minor = 0;
                patch = 0;
            }
            Increment::Minor => {
                minor += 1;
                patch = 0;
            }
            Increment::Patch => {
                patch += 1;
            }
            Increment::Pre => {
                let next_pre_release = match &self.pre_release {
                    Some(current) => match current.pre_release {
                        PreRelease::Alpha => PreRelease::Beta,
                        PreRelease::Beta => PreRelease::ReleaseCandidate,
                        PreRelease::ReleaseCandidate => {
                            bail!("unable to determine pre-release version")
                        }
                    },
                    None => {
                        patch += 1;

                        PreRelease::Alpha
                    }
                };

                pre_release = Some(PreReleaseInfo {
                    pre_release: next_pre_release,
                    number: 1,
                })
            }
            Increment::Iota => {
                let next_pre_release = match &self.pre_release {
                    Some(current) => PreReleaseInfo {
                        pre_release: current.pre_release,
                        number: current.number + 1,
                    },
                    None => {
                        patch += 1;

                        PreReleaseInfo {
                            pre_release: PreRelease::Alpha,
                            number: 1,
                        }
                    }
                };

                pre_release = Some(next_pre_release);
            }
        }

        Ok(Version {
            major,
            minor,
            patch,
            pre_release,
        })
    }
}

impl Display for Version {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if let Some(pre_release) = &self.pre_release {
            write!(
                f,
                "v{}.{}.{}-{}",
                self.major, self.minor, self.patch, pre_release
            )
        } else {
            write!(f, "v{}.{}.{}", self.major, self.minor, self.patch)
        }
    }
}

impl TryFrom<&str> for Version {
    type Error = Error;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        let re = Regex::new(
            r"^v(\d+)\.(\d+)\.(\d+)-?((alpha|beta|rc)(\d+))?(-\d+-g[a-f0-9]{7,9}(-(wip|dirty))?)?$",
        )?;
        if let Some(caps) = re.captures(value) {
            let major = caps[1].parse::<usize>()?;
            let minor = caps[2].parse::<usize>()?;
            let patch = caps[3].parse::<usize>()?;

            let mut pre_release: Option<PreReleaseInfo> = None;
            if caps.get(4).is_some() {
                let pre_release_code = PreRelease::try_from(&caps[5])?;
                let pre_release_num = caps[6].parse::<usize>()?;

                pre_release = Some(PreReleaseInfo {
                    pre_release: pre_release_code,
                    number: pre_release_num,
                })
            }

            return Ok(Version {
                major,
                minor,
                patch,
                pre_release,
            });
        }

        Err(anyhow!("unable to parse version"))
    }
}

pub fn get_next_version(current_version: &str, increment: Increment) -> anyhow::Result<Version> {
    let version = Version::try_from(current_version).unwrap_or_else(|_| Version {
        major: 0,
        minor: 0,
        patch: 0,
        pre_release: None,
    });

    version.increment(increment)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        let tests = vec![
            ("v0.0.3beta9-1-ga4578d1", Increment::Iota, "v0.0.3-beta.10"),
            ("v0.0.3beta9-1-ga4578d1", Increment::Iota, "v0.0.3-beta.10"),
            (
                "v0.0.3beta9-1-ga4578d1-wip",
                Increment::Iota,
                "v0.0.3-beta.10",
            ),
            (
                "v0.0.3-beta9-1-ga4578d1-dirty",
                Increment::Iota,
                "v0.0.3-beta.10",
            ),
            ("v10.12.13", Increment::Iota, "v10.12.14-alpha.1"),
            ("v1.2.3alpha1", Increment::Iota, "v1.2.3-alpha.2"),
            ("v1.2.3rc2-1-gabcdef1", Increment::Iota, "v1.2.3-rc.3"),
            ("v0.0.1-3-gef14a4a", Increment::Iota, "v0.0.2-alpha.1"),
            ("v0.1.0-42-g008b8c7b", Increment::Iota, "v0.1.1-alpha.1"),
            ("v0.9.1-rc1", Increment::Patch, "v0.9.2"),
            ("v0.0.3beta9-1-ga4578d1", Increment::Pre, "v0.0.3-rc.1"),
            ("v0.0.3beta9-1-ga4578d1-wip", Increment::Pre, "v0.0.3-rc.1"),
            (
                "v0.0.3-beta9-1-ga4578d1-dirty",
                Increment::Pre,
                "v0.0.3-rc.1",
            ),
            ("v10.12.13", Increment::Pre, "v10.12.14-alpha.1"),
            ("v1.2.3alpha1", Increment::Pre, "v1.2.3-beta.1"),
            ("v0.0.1-3-gef14a4a", Increment::Pre, "v0.0.2-alpha.1"),
            ("v0.1.0-42-g008b8c7b", Increment::Pre, "v0.1.1-alpha.1"),
            ("v0.0.3beta9-1-ga4578d1", Increment::Patch, "v0.0.4"),
            ("v0.0.3beta9-1-ga4578d1-wip", Increment::Patch, "v0.0.4"),
            ("v0.0.3-beta9-1-ga4578d1-dirty", Increment::Patch, "v0.0.4"),
            ("v10.12.13", Increment::Patch, "v10.12.14"),
            ("v1.2.3alpha1", Increment::Patch, "v1.2.4"),
            ("v1.2.3rc2-1-gabcdef1", Increment::Patch, "v1.2.4"),
            ("v0.0.1-3-gef14a4a", Increment::Patch, "v0.0.2"),
            ("v0.1.0-42-g008b8c7b", Increment::Patch, "v0.1.1"),
            ("v0.0.3beta9-1-ga4578d1", Increment::Minor, "v0.1.0"),
            ("v0.0.3beta9-1-ga4578d1-wip", Increment::Minor, "v0.1.0"),
            ("v0.0.3-beta9-1-ga4578d1-dirty", Increment::Minor, "v0.1.0"),
            ("v10.12.13", Increment::Minor, "v10.13.0"),
            ("v1.2.3alpha1", Increment::Minor, "v1.3.0"),
            ("v1.2.3rc2-1-gabcdef1", Increment::Minor, "v1.3.0"),
            ("v0.0.1-3-gef14a4a", Increment::Minor, "v0.1.0"),
            ("v0.1.0-42-g008b8c7b", Increment::Minor, "v0.2.0"),
            ("v0.0.3beta9-1-ga4578d1", Increment::Major, "v1.0.0"),
            ("v0.0.3beta9-1-ga4578d1-wip", Increment::Major, "v1.0.0"),
            ("v0.0.3-beta9-1-ga4578d1-dirty", Increment::Major, "v1.0.0"),
            ("v10.12.13", Increment::Major, "v11.0.0"),
            ("v1.2.3alpha1", Increment::Major, "v2.0.0"),
            ("v1.2.3rc2-1-gabcdef1", Increment::Major, "v2.0.0"),
            ("v0.0.1-3-gef14a4a", Increment::Major, "v1.0.0"),
            ("v0.1.0-42-g008b8c7b", Increment::Major, "v1.0.0"),
        ];

        for (current, increment, expected) in tests {
            let next_version = get_next_version(current, increment).unwrap();

            let next_tag = format!("{}", next_version);
            assert_eq!(&next_tag, expected);
        }
    }
}
