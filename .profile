ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
export DATABASE_URL=postgresql://charger:charger@localhost:5432/charger
export CARCHARGING_ENV=production


export PYTHONPATH="$ABSDIR/src"

source "$ABSDIR/venv/bin/activate"