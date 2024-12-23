use anyhow::{bail, Result};
use std::collections::HashSet;
use std::process::Command;
use regex::Regex;

pub fn run_git_command(args: &[&str]) -> Result<String> {
    let mut cmd = Command::new("git");
    cmd.args(args);

    // check the status of the command
    let output = cmd.output()?;
    if !output.status.success() {
        bail!("failed to run command: {:?}", cmd)
    }

    // decode the string
    let output = std::str::from_utf8(&output.stdout)?.to_string();

    Ok(output)
}

pub fn detect_upstream_remote() -> Result<&'static str> {
    let output = run_git_command(&["remote"])?;
    let remotes: HashSet<String> = output
        .lines()
        .map(|s| s.chars().filter(|c| !c.is_whitespace()).collect())
        .collect();

    if remotes.contains("upstream") {
        return Ok("upstream");
    } else if remotes.contains("origin") {
        return Ok("origin");
    }

    bail!("failed to detect upstream remote")
}

fn build_remote_branch_set(remote: &str) -> Result<HashSet<String>> {
    let output = run_git_command(&["branch", "--list", "-r"])?;

    let pattern = Regex::new(r"^\s+(\w+)/([\w/-]+$)")?;

    let mut branch_set = HashSet::new();
    for line in output.lines() {
        if let Some(captures) = pattern.captures(line) {
            if &captures[1] == remote {
                branch_set.insert(captures[2].to_string());
            }
        }
    }

    Ok(branch_set)
}

pub fn detect_master_branch(remote: &str) -> Result<&'static str> {
    // detect_master_branch(remote)
    let remote_branches = build_remote_branch_set(remote)?;

    for candidate in ["master", "main", "trunk"] {
        if remote_branches.contains(candidate) {
            return Ok(candidate);
        }
    }

    bail!("failed to detect master branch")
}

pub fn detect_stale_branches() -> Result<Vec<String>> {
    let output = run_git_command(&["branch", "-vv"])?;

    let pattern = Regex::new(r"^\s+([\w/\-.]+)\s+[0-9a-f]+ \[[\w/\-.]+: gone]")?;

    let mut stale_branches = Vec::new();
    for line in output.lines() {
        if let Some(captures) = pattern.captures(line) {
            stale_branches.push(captures[1].to_string());
        }
    }

    Ok(stale_branches)
}