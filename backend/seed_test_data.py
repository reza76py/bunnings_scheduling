import os
import random
from collections import Counter
from datetime import datetime, time, timedelta
from decimal import Decimal

import django
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.scheduling.models import CountingSession, SessionParticipant, Supplier


SUPPLIER_DURATION_RANGES = {
    "Sika": (8, 18),
    "BSG": (45, 70),
    "Allegion": (25, 45),
    "Orom": (15, 30),
    "Stanley": (35, 55),
    "PPG": (30, 50),
    "Ames": (60, 90),
    "Paslode": (5, 12),
    "3M": (15, 25),
    "Macsim": (20, 35),
}

PERSON_APPEARANCE_PROBABILITY = {
    "Reza": 0.80,
    "Holly": 0.60,
    "Ara": 0.50,
    "Mehdi": 0.20,
}

PERSON_SPEED_MODIFIER = {
    "Reza": -0.10,
    "Holly": -0.05,
    "Ara": 0.00,
    "Mehdi": 0.10,
}

STORE_NUMBER = "8164"
SESSION_COUNT = 100


def pick_team():
    selected = [
        name
        for name, probability in PERSON_APPEARANCE_PROBABILITY.items()
        if random.random() < probability
    ]

    if not selected:
        names = list(PERSON_APPEARANCE_PROBABILITY.keys())
        weights = list(PERSON_APPEARANCE_PROBABILITY.values())
        selected = [random.choices(names, weights=weights, k=1)[0]]

    if len(selected) > 3:
        weights = [PERSON_APPEARANCE_PROBABILITY[name] for name in selected]
        selected = random.choices(selected, weights=weights, k=3)
        selected = list(dict.fromkeys(selected))
        while len(selected) < 3:
            candidate = random.choices(
                list(PERSON_APPEARANCE_PROBABILITY.keys()),
                weights=list(PERSON_APPEARANCE_PROBABILITY.values()),
                k=1,
            )[0]
            if candidate not in selected:
                selected.append(candidate)

    if len(selected) > 3:
        selected = selected[:3]

    return selected


def random_start_time(days_back=30):
    day_offset = random.randint(0, days_back - 1)
    target_date = timezone.localdate() - timedelta(days=day_offset)

    minute_of_day = random.randint(7 * 60, 15 * 60)
    hour, minute = divmod(minute_of_day, 60)
    naive_dt = datetime.combine(target_date, time(hour=hour, minute=minute))

    current_tz = timezone.get_current_timezone()
    return timezone.make_aware(naive_dt, current_tz)


def calculate_duration_minutes(supplier_name, team):
    low, high = SUPPLIER_DURATION_RANGES[supplier_name]
    base_duration = random.uniform(low, high)

    average_modifier = sum(PERSON_SPEED_MODIFIER[name] for name in team) / len(team)
    person_adjusted = base_duration * (1 + average_modifier)

    small_variation = random.uniform(0.95, 1.05)
    duration = max(1, int(round(person_adjusted * small_variation)))
    return duration


def random_value():
    amount = random.uniform(500, 15000)
    return Decimal(f"{amount:.2f}")


def main():
    print("Seeding realistic test sessions with Django ORM...")
    print(f"Target sessions: {SESSION_COUNT}")
    print(f"Store number: {STORE_NUMBER}")

    supplier_cache = {}
    for supplier_name in SUPPLIER_DURATION_RANGES:
        supplier_obj, _ = Supplier.objects.get_or_create(name=supplier_name)
        supplier_cache[supplier_name] = supplier_obj

    created_sessions = []
    person_counter = Counter()
    supplier_counter = Counter()

    for index in range(1, SESSION_COUNT + 1):
        supplier_name = random.choice(list(SUPPLIER_DURATION_RANGES.keys()))
        supplier_obj = supplier_cache[supplier_name]

        team = pick_team()
        start_time = random_start_time(days_back=30)
        duration_minutes = calculate_duration_minutes(supplier_name, team)
        end_time = start_time + timedelta(minutes=duration_minutes)
        value = random_value()
        people_working_text = f"Store {STORE_NUMBER} | {', '.join(team)}"

        session = CountingSession.objects.create(
            supplier=supplier_obj,
            value=value,
            people_working=people_working_text,
            start_time=start_time,
            end_time=end_time,
        )

        SessionParticipant.objects.bulk_create(
            [
                SessionParticipant(
                    session=session,
                    name=person,
                    joined_at=start_time,
                    left_at=end_time,
                )
                for person in team
            ]
        )

        created_sessions.append(session.id)
        supplier_counter[supplier_name] += 1
        person_counter.update(team)

        print(
            f"[{index:03}/{SESSION_COUNT}] session_id={session.id} "
            f"supplier={supplier_name} team={team} "
            f"start={start_time.isoformat()} duration={duration_minutes}m value=${value}"
        )

    print("\nSeed complete.")
    print(f"Created sessions: {len(created_sessions)}")

    print("\nSupplier distribution:")
    for supplier_name in SUPPLIER_DURATION_RANGES:
        print(f"- {supplier_name}: {supplier_counter[supplier_name]}")

    print("\nPerson appearance counts and percentages:")
    for person_name in PERSON_APPEARANCE_PROBABILITY:
        count = person_counter[person_name]
        pct = (count / SESSION_COUNT) * 100
        print(f"- {person_name}: {count} sessions ({pct:.1f}%)")


if __name__ == "__main__":
    main()