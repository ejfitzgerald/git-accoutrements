# Git Accoutrements

An opinionated set of git python scripts and that have been developed over time to improve primarily
Github flow based workflows.

# Tools

## git master

Checks out the latest copy of the (master|main|trunk) branch of the project and ensures the local
branch is up to date.


## git (feature|chore|bugfix)

Creates a (feature|chore|bugfix) branch at the current version of the (master|main|trunk) branch.
Useful in a Github flow based workflow

## git tidy

Attempts to find merged branches / pruned branches in your local repo and will prompt the user to
delete them. Quite useful when working on projects that user Github Flow.

## git ditto

### Cloning a repo

A simple replacement for the git clone command, however it will scan up through the filesystem looking 
a file called `.git-ditto.toml`. This file can be used to store configuration updates that should be
applied after the clone.

This is particularly useful if you want to associate a different git profile (user, email, signingkey)
for a particular folder. i.e.

    ~/Code/Work/.git-ditto.toml    # the clones in this folder will have use work profile

And

    ~/Code/Home/.git-ditto.toml    # the clones in this folder will have use home profile

Example `.git-ditto.toml`

```toml
[user]
name = "<insert name here>"
email = "<insert email here>"
signingkey = "<insert signing key>"
```

### Updating the user information

Additionally, the `git ditto` command can be used to update existing checkouts. Either a single repo by exectuting the
following command in the checkout

```bash
$ git ditto update
```

Or additionally on all git checkouts inside a folder using the following command

```bash
$ git ditto scan
```

## git del

Deletes both local and remove copies of a branch

## git rel

Creates a new signed or annotated tag and pushes it up to the upstream repo.
