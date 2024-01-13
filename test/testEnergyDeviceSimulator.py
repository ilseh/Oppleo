from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel

import datetime

"""
    Testing the energy device simulator
"""

oppleoConfig = OppleoConfig()
device_measurement = EnergyDeviceMeasureModel()


device_measurement.kwh_l1 = 12.1
device_measurement.kwh_l2 = 13.1
device_measurement.kwh_l3 = 14.1
device_measurement.a_l1 = 1.1
device_measurement.a_l2 = 2.1
device_measurement.a_l3 = 3.1
device_measurement.p_l1 = 70.1
device_measurement.p_l2 = 71.1
device_measurement.p_l3 = 72.1
device_measurement.v_l1 = 221
device_measurement.v_l2 = 222
device_measurement.v_l3 = 223
device_measurement.kw_total = 210
device_measurement.hz = 50.0

device_measurement.created_at = datetime.datetime(2023, 10, 22)

measurement = device_measurement.to_dict()

translation = { "energy_device_id": "Meter",
                "created_at": "Timestamp",
                "kwh_l1": "E1",
                "kwh_l2": "E2",
                "kwh_l3": "E3",
                "a_l1": "A1",
                "a_l2": "A2",
                "a_l3": "A3",
                "p_l1": "P1",
                "p_l2": "P2",
                "p_l3": "P2",
                "v_l1": "V1",
                "v_l2": "V2",
                "v_l3": "V3",
                "kw_total": "ET",
                "hz": "Frequency"
        }
translated_measurement = {}

for item, value in translation.items():
    translated_measurement[value] = measurement[item]

pass    