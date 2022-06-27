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
    url = "github:mayniklas/valorant-discord-bot";
    inputs = {
      # use the nixpkgs defined in this flake!
      # python3Packages.requests is currently broken!
      # nixpkgs.follows = "nixpkgs";
      flake-utils.follows = "flake-utils";
    };
  };
}
```

2. Enable the service in your configuration:

```nix
{ discord-bot-valorant, ... }: {

  imports = [ discord-bot-valorant.nixosModules.default ];

  services.valorant-discord-bot = {
    enable = true;
    user = "valorant-discord-bot";
    group = "valorant-discord-bot";
    dataDir = "/var/lib/valorant-discord-bot";
    envfile = "/var/src/secrets/valorant-discord-bot/envfile";
  };
}
```

3. Create & fill up the Envfile:

```sh
sudo mkdir -p /var/src/secrets/valorant-discord-bot
sudo touch /var/src/secrets/valorant-discord-bot/envfile
sudo nano /var/src/secrets/valorant-discord-bot/envfile
```
