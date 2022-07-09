{
  description = "valorant discord bot";

  inputs = {

    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    valorant-utils = {
      url = "github:make-or-break/valorant-utils";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };


  };

  outputs = { self, nixpkgs, flake-utils, ... }:

    {
      nixosModules.default = self.nixosModules.valorant;
      nixosModules.valorant = { lib, pkgs, config, ... }:
        with lib;

        let cfg = config.services.valorant;
        in
        {

          options.services.valorant = {

            enable = mkEnableOption "valorant-discord-bot";

            match_crawler = mkEnableOption "match crawler";

            dataDir = mkOption {
              type = types.str;
              default = "/var/lib/valorant";
              description = ''
                The directory where valorant services store their data files. If left as the default value this directory will automatically be created before the server starts, otherwise the sysadmin is responsible for ensuring the directory exists with appropriate ownership and permissions.
              '';
            };

            envfile = mkOption {
              type = types.str;
              default = "/var/src/secrets/valorant/envfile";
              description = ''
                The location of the envfile containing secrets
              '';
            };

            user = mkOption {
              type = types.str;
              default = "valorant";
              description = "User account under which valorant services run.";
            };

            group = mkOption {
              type = types.str;
              default = "valorant";
              description = "Group under which which valorant services run.";
            };

          };

          config = mkIf cfg.enable {

            systemd.services.valorant-discord-bot = {
              description = "A discord bot for our valorant group";
              wantedBy = [ "multi-user.target" ];
              serviceConfig = mkMerge [
                {
                  EnvironmentFile = [ cfg.envfile ];
                  User = cfg.user;
                  Group = cfg.group;
                  WorkingDirectory = cfg.dataDir;
                  ExecStart = "${self.packages."${pkgs.system}".valorant-discord-bot}/bin/valorant-discord-bot";
                  Restart = "on-failure";
                }
                (mkIf (cfg.dataDir == "/var/lib/valorant") {
                  StateDirectory = "valorant";
                })
              ];
            };

            # valorant match crawler service
            systemd.timers.valorant-match-crawler = mkIf cfg.match_crawler {
              wantedBy = [ "timers.target" ];
              partOf = [ "valorant-match-crawler.service" ];
              timerConfig.OnCalendar = "*-*-* *:00:00";
            };

            systemd.services.valorant-match-crawler = mkIf cfg.match_crawler {
              serviceConfig = mkMerge [
                {
                  User = cfg.user;
                  Group = cfg.group;
                  WorkingDirectory = cfg.dataDir;
                  Type = "oneshot";
                  ExecStart = "${self.packages."${pkgs.system}".valorant-discord-bot}/bin/valorant-match-crawler";
                }
                (mkIf (cfg.dataDir == "/var/lib/valorant") {
                  StateDirectory = "valorant";
                })
              ];
            };


            users.users = mkIf
              (cfg.user == "valorant")
              {
                valorant = {
                  isSystemUser = true;
                  group = cfg.group;
                  description = "valorant system user";
                };
              };

            users.groups =
              mkIf
                (cfg.group == "valorant")
                { valorant = { }; };

          };
          meta = { maintainers = with lib.maintainers; [ mayniklas ]; };
        };
    }

    //

    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in
      rec {

        # Use nixpkgs-fmt for `nix fmt'
        formatter = pkgs.nixpkgs-fmt;

        defaultPackage = packages.valorant-discord-bot;
        packages = flake-utils.lib.flattenTree rec {

          valorant-discord-bot = with pkgs.python310Packages;
            buildPythonPackage rec {
              pname = "valorant-discord-bot";
              version = "0.2.0";

              src = self;
              propagatedBuildInputs = [

                # flake inputs
                self.inputs.valorant-utils.packages.${system}.valorant-utils

                # we want to use discordpy 2.0.0a
                # but it's not available in nixpkgs yet (it's still in alpha)
                # discord.py uses a newer API version with new features
                # the older API version will stop working in the future
                (discordpy.overrideAttrs
                  (old: rec {
                    pname = "discord.py";
                    version = "2.0.0a";
                    src = pkgs.fetchFromGitHub {
                      owner = "Rapptz";
                      repo = pname;
                      rev = "55849d996e65613a334d73adbfc43bbe7b77d31a";
                      sha256 = "sha256-7s+wIIaih0CtXCzD4nAfSxvebZuEbYIo5LMH6RZgX9A=";
                    };
                  }))

                requests
                sqlalchemy

              ];

              doCheck = false;
              pythonImportsCheck = [
                "database.sql_scheme"
                "database.sql_statements"
              ];

              meta = with pkgs.lib; {
                description = "valorant discord bot";
                homepage = "https://github.com/make-or-break/valorant-discord-bot/";
                platforms = platforms.unix;
                maintainers = with maintainers; [ mayniklas ];
              };
            };

          # Documenation for this feature: https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/docker/examples.nix
          # nix build .#docker-image
          # docker load < result
          docker-image = pkgs.dockerTools.buildLayeredImage {
            name = "valorant-discord-bot";
            # needed so we can enter the container using bash
            contents = [
              pkgs.coreutils
              pkgs.bash
            ];
            config = {
              Cmd = [ "${self.packages.${system}.valorant-discord-bot}/bin/valorant-discord-bot" ];
              Env = [
                "TOKEN=discord_token"
              ];
            };
          };

        };


      });
}
