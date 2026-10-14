'''Main file which includes functions for managing the energy system meter
    and calcuating bills based off of the meter'''
import json
from datetime import datetime

# Global state
meters = {}
RATE_TIER_1 = 3.5
RATE_TIER_2 = 5.0
RATE_TIER_3 = 7.5
SPIKE_LIMIT = 500


def record_reading(meter_id, units, history=None):
    '''Adding an amount of units to the meter_id given (if not created),
        and add a record to history'''
    if not history:
        history = []
    history.append((meter_id, units, str(datetime.now())))
    meters[meter_id] = meters.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    '''Calculate the cost of the items in a single bill
        (with a specific meter_Id)'''
    units = meters[meter_id]
    if units <= 100:
        return units * tier_rates[0]
    if units <= 300:
        return 100 * tier_rates[0] + (units - 100) * tier_rates[1]
    return (
        100 * tier_rates[0]
        + 200 * tier_rates[1]
        + (units - 300) * tier_rates[2]
    )


def raise_rates(percent, rates):
    '''Raise the rates of a unit of all 3 tiers
        of energy by a given percentage'''
    for i, v in enumerate(rates):
        rates[i] = v * (1 + percent / 100)
    return rates


def flag_spikes(meters_local, spike_limit):
    '''If more than SPIKE_LIMIT units have been used in a bill,
        flag it by adding the meter_id to the global list spikes'''
    spikes = []
    for m in meters_local:
        if meters_local[m] > spike_limit:
            spikes.append(m)
    return spikes


def load_meter_data(file="meters.json"):
    '''Read from the file that all bills have
        been written (default name meters.json)'''
    try:
        with open(file, encoding='ascii') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return {}


def save_meter_data(meters_local, file="meters.json"):
    '''Write meters into a json file - default name meters.json'''
    with open(file, "w", encoding='ascii') as f:
        f.write(json.dumps(meters_local))


def main(rates, spike_limit, meters_local):
    '''Main function (driver)'''
    record_reading("M-01", 120)
    record_reading("M-02", 640)
    h = record_reading("M-03", -50)
    print("Readings stored so far:", len(h))
    rates = raise_rates(10, rates)
    print(f"Bill M-01: {compute_bill("M-01", rates)}.2f")
    print(f"Bill M-03: {compute_bill("M-03", rates)}.2f")
    print("Spikes:", flag_spikes(meters, spike_limit))
    adjustment = (
        int(
            input("Extra units for M-01 as an expression (Enter for 0): ")
        )
        or "0"
    )
    record_reading("M-01", adjustment, h)
    save_meter_data(meters_local)
    meters_local = load_meter_data()
    print(f"Bill M-01 after reload: {compute_bill("M-01", rates)}.2f")


main([RATE_TIER_1, RATE_TIER_2, RATE_TIER_3], SPIKE_LIMIT, meters)
