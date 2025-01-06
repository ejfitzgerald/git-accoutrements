use clap::Parser;
use std::path::PathBuf;
use regex::Regex;
use serde::Deserialize;
use accoutrements::run_git_command;

#[derive(Deserialize, Debug)]
struct Config {
    user: UserConfig,
}

#[derive(Deserialize, Debug)]
struct UserConfig {
    name: String,
    email: String,
    signingkey: String,
}

fn find_config_file_path() -> anyhow::Result<Option<PathBuf>> {
    let mut current_dir = std::env::current_dir()?;

    loop {
        let config_file_path = current_dir.join(".ditto.toml");
        if config_file_path.exists() {
            return Ok(Some(config_file_path));
        }

        let parent = current_dir.parent();
        if parent.is_none() {
            break;
        }
        current_dir = parent.unwrap().to_path_buf();
    }

    Ok(None)
}

fn load_config() -> anyhow::Result<Option<Config>> {
    let config_path = find_config_file_path()?;
    if config_path.is_none() {
        return Ok(None);
    }

    let config_file_path = config_path.unwrap();
    let config_file_contents = std::fs::read_to_string(config_file_path)?;
    let config: Config = toml::from_str(&config_file_contents)?;

    Ok(Some(config))
}

fn update_working_copy(cfg: &Config) -> anyhow::Result<()> {

    // update the configuration
    run_git_command(&["config", "user.name", &cfg.user.name])?;
    run_git_command(&["config", "user.email", &cfg.user.email])?;
    run_git_command(&["config", "user.signingkey", &cfg.user.signingkey])?;

    println!("Set user name to: {}", cfg.user.name);
    println!("Set user email to: {}", cfg.user.email);
    println!("Set user signing key to: {}", cfg.user.signingkey);

    Ok(())
}

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// The uri to download or "update" to correct the configuration of the current folder
    #[arg()]
    uri: String,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();

    // load the configuration
    let cfg = load_config()?.ok_or(anyhow::anyhow!("No config file found"))?;

    let mut original_directory: Option<PathBuf> = None;
    if args.uri != "update" {
        let re = Regex::new(r"^git@.*?/(.*)\.git$")?;
        let captures = re.captures(&args.uri).ok_or(anyhow::anyhow!("Unknown URL {}", &args.uri))?;

        let current_directory = std::env::current_dir()?;
        let output_directory = current_directory.join(&captures[1]);

        // clone the repo
        println!("Cloning {}...", &args.uri);
        run_git_command(&["clone", &args.uri])?;

        // change the directory to the output directory
        std::env::set_current_dir(output_directory)?;
        original_directory = Some(current_directory);
    }

    // update the working copy configuration
    update_working_copy(&cfg)?;

    // restore the original working copy if needed
    if let Some(original_directory) = original_directory {
        std::env::set_current_dir(original_directory)?;
    }

    Ok(())
}
