ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)

source "$ABSDIR/.profile"

python3 "$ABSDIR/src/nl/oppleo/runner/DevicesStarter.py" start