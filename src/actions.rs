use anyhow::bail;
use crate::{detect_master_branch, detect_upstream_remote, has_working_changes, run_git_command};

pub fn checkout_new_development_branch(prefix: &str, names: Vec<String>) -> anyhow::Result<()> {
    // check if the working copy has uncommitted changes
    if has_working_changes() {
        bail!("working copy has changes please commit first before switching")
    }

    // detect chosen remote
    let upstream = detect_upstream_remote()?;
    let main_branch = detect_master_branch(upstream)?;

    // fetch (and prune) latest changes from the target remote
    run_git_command(&["fetch", upstream, "-p"])?;

    // define the branch name
    let branch_name = format!("{}/{}", prefix, names.join("-"));
    let starting_point = format!("{}/{}", upstream, main_branch);

    // create the branch wherever we currently hard
    run_git_command(&["checkout", "-b", branch_name.as_str()])?;

    // hard reset the branch to the specific point in time (we do not want to have any of the git
    // branching tracking entries in the .git/config).
    // this is why we must check for any changes before doing this
    run_git_command(&["reset", "--hard", starting_point.as_str()])?;

    Ok(())
}