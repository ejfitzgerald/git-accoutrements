use clap::Parser;
use accoutrements::checkout_new_development_branch;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// The name of the new feature branch
    #[arg()]
    name: Vec<String>,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    checkout_new_development_branch("feat", args.name)?;

    Ok(())
}