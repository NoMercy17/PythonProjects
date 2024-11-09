import random
import simpy
from matplotlib import pyplot as plt


class Station:
    def __init__(self, env, name, capacity, init_bikes):
        self.env = env
        self.name = name
        self.capacity = capacity
        self.bikes = simpy.Container(env, init=init_bikes, capacity=capacity)
        self.bikes_under_maintenance = 0


def bike_trip(env, from_station, to_station, failure_prob, unhappy_customers):
    if from_station.bikes.level > 0:
        yield from_station.bikes.get(1)
        print(f"Time {int(env.now)}: Bike taken from {from_station.name}")
    else:
        print(f"Time {int(env.now)}: No bikes available at {from_station.name}")
        unhappy_customers[0] += 1
        return

    trip_duration = random.uniform(2, 5)
    yield env.timeout(trip_duration)

    if random.uniform(0, 1) < failure_prob:
        print(f"Time {int(env.now)}: Bike failed during the trip to {to_station.name}")
        yield env.process(repair_bike(env, from_station))
        if from_station.bikes.level == 0:
            unhappy_customers[0] += 1
            print(f"Time {int(env.now)}: No bikes available at {from_station.name} after failure.")
            return

    if to_station.bikes.level < to_station.capacity:
        yield to_station.bikes.put(1)
        print(f"Time {int(env.now)}: Bike returned to {to_station.name}")
    else:
        print(f"Time {int(env.now)}: No docks available at {to_station.name}, returning bike to {from_station.name}")
        yield env.timeout(trip_duration)
        if from_station.bikes.level < from_station.capacity:
            yield from_station.bikes.put(1)
            print(f"Time {int(env.now)}: Bike returned to {from_station.name}")
        else:
            unhappy_customers[0] += 1
            print(f"Time {int(env.now)}: No space at {from_station.name} to return the bike.")


def get_active_prob_matrix(env, env_now):
    current_time = env_now % (24 * 60)
    for slot in time_slots:
        if slot['start'] <= current_time < slot['end']:
            return slot['prob_matrix']
    return default_prob_matrix


def generate_trips(env, failure_prob, unhappy_customers):
    while True:
        prob_matrix = get_active_prob_matrix(env, env.now)
        for (from_station, to_station), prob in prob_matrix.items():
            if random.uniform(0, 1) < prob:
                env.process(bike_trip(env, from_station, to_station, failure_prob, unhappy_customers))
        yield env.timeout(1)


def repair_bike(env, station):
    station.bikes_under_maintenance += 1
    print(f"Time {int(env.now)}: Bike under maintenance at {station.name}")
    repair_time = random.uniform(3, 7)
    yield env.timeout(repair_time)
    station.bikes_under_maintenance -= 1
    print(f"Time {int(env.now)}: Bike repaired and available at {station.name}")


def rebalance_bikes(env, stations):
    while True:
        low_bikes_stations = [s for s in stations if s.bikes.level < s.capacity * 0.4]
        high_bikes_stations = [s for s in stations if s.bikes.level > s.capacity * 0.6]
        for low_station in low_bikes_stations:
            for high_station in high_bikes_stations:
                if high_station.bikes.level > 0 and low_station.bikes.level < low_station.capacity:
                    yield high_station.bikes.get(1)
                    yield env.timeout(1)
                    yield low_station.bikes.put(1)
                    print(f"Time {env.now}: Rebalanced a bike from {high_station.name} to {low_station.name}")
        yield env.timeout(10)


def monitor_stations(env, stations, bike_levels):
    while True:
        for station in stations:
            bike_levels[station.name].append((env.now, station.bikes.level))
        yield env.timeout(1)


def run_simulator():
    global time_slots

    env = simpy.Environment()
    upt_station = Station(env, "UPT", capacity=18, init_bikes=10)
    center_station = Station(env, "Center", capacity=10, init_bikes=8)
    p700_station = Station(env, "P700", capacity=9, init_bikes=6)
    private_station = Station(env, "Private", capacity=12, init_bikes=9)

    failure_prob = 0.1
    stations = [upt_station, center_station, p700_station, private_station]
    unhappy_customers = [0]

    bike_levels = {station.name: [] for station in stations}

    time_slots = [
        {
            'name': 'morning_start',
            'start': 0,
            'end': 120,
            'prob_matrix': {
                (upt_station, center_station): 0.3,
                (center_station, upt_station): 0.5,
                (upt_station, p700_station): 0.2,
                (p700_station, upt_station): 0.4,
                (center_station, p700_station): 0.2,
                (p700_station, center_station): 0.3,
                (upt_station, private_station): 0.2,
                (private_station, upt_station): 0.3,
            }
        },
        {
            'name': 'midday',
            'start': 120,
            'end': 720,
            'prob_matrix': {
                (upt_station, center_station): 0.15,
                (center_station, upt_station): 0.2,
                (upt_station, p700_station): 0.1,
                (p700_station, upt_station): 0.15,
                (center_station, p700_station): 0.15,
                (p700_station, center_station): 0.2,
                (upt_station, private_station): 0.1,
                (private_station, upt_station): 0.15,
            }
        }
    ]

    global default_prob_matrix
    default_prob_matrix = {
        (upt_station, center_station): 0.05,
        (center_station, upt_station): 0.05,
        (upt_station, p700_station): 0.05,
        (p700_station, upt_station): 0.05,
        (center_station, p700_station): 0.05,
        (p700_station, center_station): 0.05,
        (upt_station, private_station): 0.05,
        (private_station, upt_station): 0.05,
    }

    env.process(generate_trips(env, failure_prob, unhappy_customers))
    env.process(rebalance_bikes(env, stations))
    env.process(monitor_stations(env, stations, bike_levels))

    env.run(until=1440)
    for station_name, levels in bike_levels.items():
        if levels:
            times, counts = zip(*levels)
            plt.plot(times, counts, label=station_name)

    plt.xlabel('Time (minutes)')
    plt.ylabel('Number of Bikes')
    plt.title('Bike Levels at Each Station Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    run_simulator()
