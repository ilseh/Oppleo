import json
from datetime import datetime, timedelta
from nl.oppleo.config.OppleoConfig import OppleoConfig

oppleoConfig = OppleoConfig()
lastBackup = oppleoConfig.backupSuccessTimestamp
now = datetime.now()


weekDayList = json.loads(oppleoConfig.backupIntervalWeekday)
# Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
weekDayToday = now.weekday()


daysPast = 8
for i in range(7):
    # +1 to convert from 0=Monday to 0=Sunday
    # -i to go backwards through the week (7 days = range(7))
    daysPast = i if weekDayList[(weekDayToday+1-i)%7] and daysPast == 8 else daysPast


due = ((datetime.now() - timedelta(days=daysPast))
        .replace(hour=oppleoConfig.backupTimeOfDay.hour, 
                    minute=oppleoConfig.backupTimeOfDay.minute,
                    second=0, 
                    microsecond=0
                    )
        )

# Backup due? (daysPast=8 indicates no active days)
print( str(daysPast != 8) + ' and ' + str(lastBackup < due) + ' and ' + str(now > due))
