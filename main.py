import os
import pickle
import random
import traci
import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np
import xml.etree.ElementTree as xml_parser

sumo_port = 8813
step = 0
counter = 0
charging_vehicles = []
modified_vehicles = []
vehicles_log = []
traci.start(
    port=sumo_port,
    cmd=["sumo-gui", "-c", "chargstation.sumocfg", "--quit-on-end"],
)
direction_flag = True
while step < 1000:
    traci.simulationStep()
    for vehicle_id in traci.vehicle.getIDList():
        if not vehicle_id in modified_vehicles:
            vehicle_battery_capcity = float(
                traci.vehicle.getParameter(vehicle_id, "device.battery.capacity")
            )
            if np.random.choice([0, 1], p=[0.08, 0.92]) == 0:

                traci.vehicle.setParameter(
                    vehicle_id,
                    "device.battery.actualBatteryCapacity",
                    str(vehicle_battery_capcity * 0.15),
                )
                # print(f"Lower vehicle charge level. {counter}")
            else:
                traci.vehicle.setParameter(
                    vehicle_id,
                    "device.battery.actualBatteryCapacity",
                    str(vehicle_battery_capcity * random.uniform(0.4, 0.9)),
                )
            modified_vehicles.append(vehicle_id)

        current_battery = float(
            traci.vehicle.getParameter(
                vehicle_id,
                "device.battery.actualBatteryCapacity",
            )
        )
        vehicles_log.append(
            {"id": vehicle_id, "start": current_battery / vehicle_battery_capcity}
        )
        if (
            current_battery <= vehicle_battery_capcity * 0.15
            and not vehicle_id in charging_vehicles
        ):
            if traci.vehicle.getPosition(vehicle_id)[0] < 57:
                try:
                    selected_station_id = "cs_1"
                    traci.vehicle.setRoute(vehicle_id, ["E0_1", "E3", "E4", "E2"])
                    traci.vehicle.setChargingStationStop(
                        vehicle_id,
                        selected_station_id,
                    )

                    print(
                        f"vehicle {vehicle_id} with battery level {current_battery} started charging."
                    )
                    charging_vehicles.append(vehicle_id)
                except:
                    print("error in setting routes")

            # charging_cars_ids = traci.chargingstation.getVehicleIDs("cs_0")

        for v_id in charging_vehicles:

            current_battery = float(
                traci.vehicle.getParameter(
                    v_id,
                    "device.battery.actualBatteryCapacity",
                )
            )
            vehicle_battery_capcity = float(
                traci.vehicle.getParameter(v_id, "device.battery.capacity")
            )

            if current_battery >= vehicle_battery_capcity * 0.2:
                print(f"vehicle with id {v_id} was charged.{current_battery}")
                traci.vehicle.resume(v_id)
                charging_vehicles.remove(v_id)
                for vehicle in vehicles_log:
                    if vehicle["id"] == v_id:
                        vehicle["end"] = current_battery
                        vehicle["charged"] = True
    step += 1
traci.close()

time.sleep(3)
BATTERY_DATA_FILE = "battery_output.xml"  # مسیر خروجی داده‌های باتری

balances = []
for vehicle in vehicles_log:
    start_soc = vehicle["start"]
    end_soc = vehicle["end"]
    charged = 1500 if vehicle["charged"] else 0
    consumption = (start_soc + charged) - end_soc
    balances.append(consumption)

print("Number of vehicles finished:", len(balances))
print("Energy consumptions:", balances)

plt.hist(balances, bins=20)
plt.xlabel("Energy Consumed (Wh)")
plt.ylabel("Number of Vehicles")
plt.title("Histogram of Energy Consumption per Vehicle")
plt.grid(True)
plt.show()
