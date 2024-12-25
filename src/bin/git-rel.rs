use accoutrements::{
    create_tag, detect_upstream_remote, get_current_version, get_next_version, push_tag,
    wait_for_confirmation, Increment,
};
use anyhow::Result;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// The name of the new tag to create or the increment that is required i.e. major, minor, patch
    #[arg(default_value = "patch")]
    tag: String,

    /// Fetch the latest changes
    #[arg(short, long, default_value_t = false)]
    fetch: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let current_version = get_current_version()?;
    let upstream_remote = detect_upstream_remote()?;

    // try and work out if the tag is actually a version increment, if so then we need to
    let next_version = match Increment::try_from(args.tag.as_str()) {
        Ok(increment) => get_next_version(current_version.as_str(), increment)?.to_string(),
        Err(_) => args.tag,
    };

    println!("Current version: {}", current_version);
    println!("   Next version: {}", next_version);
    println!("Upstream remote: {}", upstream_remote);

    // wait for the user confirmation
    wait_for_confirmation()?;

    // create the new tag
    create_tag(next_version.as_str())?;

    // push the tag to the remote
    push_tag(upstream_remote, next_version.as_str())?;

    Ok(())
}
