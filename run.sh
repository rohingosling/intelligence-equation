#!/usr/bin/env sh

case "$0" in
    */*)
        SCRIPT_PATH_DIRECTORY=${0%/*}
        ;;
    *)
        SCRIPT_PATH_DIRECTORY=.
        ;;
esac

SCRIPT_DIRECTORY=$(CDPATH= cd -- "$SCRIPT_PATH_DIRECTORY" && pwd) || exit 1

cd "$SCRIPT_DIRECTORY" || exit 1

if [ -x ".venv/bin/python" ]
then
    PYTHON_EXECUTABLE=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]
then
    PYTHON_EXECUTABLE=".venv/Scripts/python.exe"
elif [ -x "../.venv/bin/python" ]
then
    PYTHON_EXECUTABLE="../.venv/bin/python"
elif [ -x "../.venv/Scripts/python.exe" ]
then
    PYTHON_EXECUTABLE="../.venv/Scripts/python.exe"
else
    PYTHON_EXECUTABLE="${PYTHON:-python3}"
fi

if ! "$PYTHON_EXECUTABLE" -c "import yaml" >/dev/null 2>&1
then
    printf '%s\n' \
        "Error: PyYAML is not installed for $PYTHON_EXECUTABLE." \
        "" \
        "Create a project virtual environment and install the runtime dependencies:" \
        "  Linux:    python3 -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt" \
        "  Git Bash: py -3.12 -m venv .venv && ./.venv/Scripts/python.exe -m pip install -r requirements.txt" \
        >&2
    exit 1
fi

exec "$PYTHON_EXECUTABLE" main.py "$@"
