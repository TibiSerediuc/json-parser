# flake.nix
{
  description = "JSON Parser development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python and UV
            python3
            uv
            git
            
            # Development tools
            tree
            ripgrep
            fd
            
            # Might use in future for porting to C 
            #gcc
            #gdb
            #valgrind
            
            # Documentation
            man-pages
          ];

          shellHook = ''
            echo "JSON Parser Development Environment"
            echo "Python version: $(python --version)"
            echo "UV version: $(uv --version)"
            echo ""
            echo "Setup commands:"
            echo "  uv venv              - Create virtual environment"
            echo "  source .venv/bin/activate  - Activate venv"
            echo "  uv pip install -e . - Install project in dev mode"
            echo ""
            echo "Development commands:"
            echo "  uv run pytest       - Run tests"
            echo "  uv run black .       - Format code"
            echo "  uv run flake8 .      - Lint code"
            echo "  uv run mypy src/     - Type checking"
            echo ""
            echo "Project structure:"
            echo "  src/        - Source code"
            echo "  tests/      - Test files"
            echo "  examples/   - Example JSON files"
            echo ""
            
            # Create directories if they don't exist
            mkdir -p src tests examples tests/fixtures/valid tests/fixtures/invalid
            
            # Initialize __init__.py files
            touch src/__init__.py tests/__init__.py
            
            # Create virtual environment if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment..."
              uv venv
            fi
            
            # Activate virtual environment
            source .venv/bin/activate
            
            # Set up Python path
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
          '';
        };
      });
}
