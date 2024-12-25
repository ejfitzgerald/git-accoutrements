use accoutrements::{detect_master_branch, detect_upstream_remote, run_git_command};
use anyhow::Result;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Fetch the latest changes
    #[arg(short, long, default_value_t = false)]
    fetch: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();

    // detect the upstream
    let upstream = detect_upstream_remote()?;

    // fetch the latest changes if we need to
    if args.fetch {
        run_git_command(&["fetch", upstream, "-p"])?;
    }

    // detect what the main / master branch is
    let master_branch = detect_master_branch(upstream)?;

    // checkout the main/master branch
    run_git_command(&[
        "checkout",
        "-B",
        master_branch,
        &format!("{}/{}", upstream, master_branch),
    ])?;

    Ok(())
}
