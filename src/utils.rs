
pub fn wait_for_confirmation() -> anyhow::Result<()> {
    println!("press enter to continue");

    let mut buffer = String::new();
    let stdin = std::io::stdin(); // We get `Stdin` here.
    stdin.read_line(&mut buffer)?;

    Ok(())
}
