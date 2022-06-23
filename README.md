# discord-bot-valorant-rank

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

# install package, but any changes will immediately take effect.
python setup.py develop
```
