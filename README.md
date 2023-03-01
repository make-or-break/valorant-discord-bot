# valorant-discord-bot

## Usage

### Nix & NixOS

```bash
# run the package from the repository
nix run .#

# build the package
nix build .#
```

### Linux & MacOS

```bash
# create virtual environment
python3 -m venv .venv

# use virtual environment
source .venv/bin/activate

# install dependencies from requirements.txt
pip3 install -r requirements.txt

# install package in development mode (changes will take effect automatically)
pip install -e .
```

### Environment Variables

```sh
export TOKEN="<your-API-token>"
```

## How to install

### NixOS

1. Add this repository to your `flake.nix`:

```nix
{
  inputs.discord-bot-valorant = {
    url = "github:make-or-break/valorant-discord-bot";
  };
}
```

2. Enable the services in your configuration:

```nix
{ discord-bot-valorant, ... }: {

  imports = [
    # A discord bot for valorant communities
    # https://github.com/make-or-break/valorant-discord-bot
    discord-bot-valorant.nixosModules.valorant-discord-bot
    discord-bot-valorant.nixosModules.valorant-match-history
  ];

  # nix flake lock --update-input discord-bot-valorant
  services = {
    valorant-discord-bot = {
      enable = true;
      dataDir = "/var/lib/valorant";
      envfile = "/var/src/secrets/valorant/envfile";
    };
    valorant-match-history = {
      enable = true;
      dataDir = "/var/lib/valorant";
    };
  };

}
```

3. Create & fill up the Envfile:

```sh
sudo mkdir -p /var/src/secrets/valorant-discord-bot
sudo touch /var/src/secrets/valorant-discord-bot/envfile
sudo nano /var/src/secrets/valorant-discord-bot/envfile
```
