# gitea-api

The unified command for the previously separate functions

## `gitea-api -h`

Provides help. The command uses Python's `argparse`, so help can be requested of sub-commands as well. e.g. `gitea-api-tools python -h` Note that help is less useful on commands that don't take additional arguments.

## `gitea-api configure`

Configures the settings interactively. Will validate the configuration at the end.

## `gitea-api deploy_keys`

Shows all your deploy keys along with their public keys. Normally, the deploy key page on each repository only shows the user-chosen name and fingerprint.

## `gitea-api user_id`

Retrieves your user ID. The sub-command offers to save this ID in the configuration, if it isn't already recorded.

## `gitea-api python [-v VERSION] package`

Finds repositories that use Python dependent packages. If version is provided, the sub-command only shows repositories with dependencies lower than that version.
