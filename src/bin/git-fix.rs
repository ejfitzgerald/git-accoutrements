use accoutrements::checkout_new_development_branch;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// The name of the new feature branch
    #[arg()]
    name: Vec<String>,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    checkout_new_development_branch("fix", args.name)?;

    Ok(())
}
