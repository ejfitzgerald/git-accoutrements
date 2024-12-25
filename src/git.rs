use anyhow::bail;
use regex::Regex;
use std::collections::HashSet;
use std::process::Command;

pub fn run_git_command(args: &[&str]) -> anyhow::Result<String> {
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

pub fn get_current_version() -> anyhow::Result<String> {
    let output = run_git_command(&["describe", "--always"])?;
    Ok(output.trim().to_string())
}

pub fn detect_upstream_remote() -> anyhow::Result<&'static str> {
    let output = run_git_command(&["remote"])?;
    let remotes: HashSet<String> = output.lines().map(|s| s.trim().to_string()).collect();

    if remotes.contains("upstream") {
        return Ok("upstream");
    } else if remotes.contains("origin") {
        return Ok("origin");
    }

    bail!("failed to detect upstream remote")
}

fn build_remote_branch_set(remote: &str) -> anyhow::Result<HashSet<String>> {
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

pub fn detect_master_branch(remote: &str) -> anyhow::Result<&'static str> {
    // detect_master_branch(remote)
    let remote_branches = build_remote_branch_set(remote)?;

    for candidate in ["master", "main", "trunk"] {
        if remote_branches.contains(candidate) {
            return Ok(candidate);
        }
    }

    bail!("failed to detect master branch")
}

pub fn detect_stale_branches() -> anyhow::Result<Vec<String>> {
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

fn has_signing_key() -> bool {
    if let Ok(output) = run_git_command(&["config", "user.signingkey"]) {
        return !output.trim().is_empty();
    }

    false
}

pub fn create_tag(name: &str) -> anyhow::Result<()> {
    let sign_type = if has_signing_key() { "-s" } else { "-a" };
    run_git_command(&["tag", sign_type, name, "-m", name])?;

    Ok(())
}

pub fn push_tag(remote: &str, tag: &str) -> anyhow::Result<()> {
    run_git_command(&["push", remote, tag])?;

    Ok(())
}

pub fn has_working_changes() -> bool {
    run_git_command(&["diff", "--exit-code"]).is_err()
}
