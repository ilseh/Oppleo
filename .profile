ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
export DATABASE_URL=postgresql://charger:charger@localhost:5432/charger
export CARCHARGING_ENV=production
export ENERGY_DEVICE_ID=laadpaal_noord


export PYTHONPATH="$ABSDIR/src"

source "$ABSDIR/venv/bin/activate"