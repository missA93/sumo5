import os
import pickle
import random
import traci
import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np
import xml.etree.ElementTree as xml_parser

# from trafic_light import TraficLight, TraficState

sumo_port = 8813
step = 0
counter = 0
jam_lengths = []
traffic_light_phases = []
traffic_light_id = "J9"
edge_id = "E0"
charging_vehicles = []
modified_vehicles = []
vehicles_log = []
traci.start(
    port=sumo_port,
    cmd=["sumo-gui", "-c", "chargstation.sumocfg", "--random", "--quit-on-end"],
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
            if traci.vehicle.getPosition(vehicle_id)[0] < 110:
                try:
                    selected_station_id = "cs_0"
                    traci.vehicle.setRoute(vehicle_id, ["E0", "E1", "E2", "E3"])
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


def count_vehicles_at_red_light(traci, traffic_light_pos, distance_threshold=50):
    count = 0
    vehicles_behind_traffic = []
    for vehicle_id in traci.vehicle.getIDList():
        vehicle_pos = traci.vehicle.getPosition(vehicle_id)
        dist = traci.simulation.getDistance2D(
            traffic_light_pos[0], traffic_light_pos[1], vehicle_pos[0], vehicle_pos[1]
        )
        if (
            traffic_light_pos[0] > vehicle_pos[0]
            and traci.vehicle.getSpeed(vehicle_id) < 2
        ):

            count += 1

    return count

    traffic_jam_level = count_vehicles_at_red_light(
        traci_connection, traffic_light_position
    )

    # # Traffic light control logic
    # if traffic_jam_level >= TrafficState.High.value or keep_green_light:
    #     keep_green_light = True
    #     if waiting_steps_counter >= TrafficState.High.value * 1.5:
    #         keep_green_light = False
    #         waiting_steps_counter = 0
    #     else:
    #         waiting_steps_counter += 1
    #     traci_connection.trafficlight.setPhase(
    #         traffic_light_id, TrafficLightPhase.Green.value
    #     )
    # else:
    #     traci_connection.trafficlight.setPhase(
    #         traffic_light_id, TrafficLightPhase.Red.value
    #     )

    # # Record current state
    # current_phase = traci_connection.trafficlight.getPhase(traffic_light_id)
    # traffic_history.append(traffic_jam_level)
    # traffic_light_phase_history.append("Red" if current_phase == 2 else "Green")

    # current_step += 1
