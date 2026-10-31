# Source suite definitions in-process so they share the runner's paths, logging helpers, and status variables.
source "$SCRIPT_DIR/unified/unit.sh"
source "$SCRIPT_DIR/unified/integration.sh"
source "$SCRIPT_DIR/unified/acceptance.sh"
source "$SCRIPT_DIR/unified/contracts.sh"
