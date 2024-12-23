use anyhow::Result;
use clap::Parser;
use git_accoutrements::{detect_stale_branches, run_git_command};

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Fetch the latest changes
    #[arg(short, long, default_value_t = false)]
    fetch: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();

    // fetch the latest changes if we need to
    if args.fetch {
        run_git_command(&["fetch", "--all", "-p"])?;
    }

    // detect what the main / master branch is
    let stale_branches = detect_stale_branches()?;

    println!("The following stale branches will be removed:");
    for branch in &stale_branches {
        println!(" - {}", branch);
    }
    println!("press enter to continue");

    let mut buffer = String::new();
    let stdin = std::io::stdin(); // We get `Stdin` here.
    stdin.read_line(&mut buffer)?;

    // delete all the branches
    for branch in stale_branches {
        run_git_command(&["branch", "-D", &branch])?;
    }

    Ok(())
}
