ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)

source "$ABSDIR/.profile"

python3 "$ABSDIR/src/nl/carcharging/daemon/LedLightHandler.py" stop
python3 "$ABSDIR/src/nl/carcharging/daemon/LedLightHandler.py" kill