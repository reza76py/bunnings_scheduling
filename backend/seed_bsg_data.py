import os
import random
from datetime import datetime, time, timedelta
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()

from django.utils import timezone
from apps.scheduling.models import CountingSession, SessionParticipant, Supplier

# Supplier averages (minutes)
SUPPLIER_AVERAGES = {
    "Sika": 12,
    "BSG": 58,
    "Allegion": 35,
    "Orom": 20,
    "Stanley": 43,
    "PPG": 36,
    "Ames": 79,
    "Paslode": 7,
    "3M": 21,
    "Macsim": 27,
    "Crommelin": 24,
    "Stafani": 48,
    "Moroody": 21,
    "KSG": 16,
    "Unipro": 28,
    "Journe": 17,
    "Twist": 13,
}

PEOPLE = ["Reza", "Holly", "Ara", "Mehdi"]
PEOPLE_SPEED = {
    "Reza": -0.15,  # 15% faster
    "Holly": -0.10, # 10% faster
    "Ara": 0.0,     # average
    "Mehdi": 0.10,  # 10% slower
}
PEOPLE_PROB = {
    "Reza": 0.80,
    "Holly": 0.60,
    "Ara": 0.50,
    "Mehdi": 0.20,
}
TEAM_SIZE_FACTOR = {1: 1.0, 2: 0.75, 3: 0.60, 4: 0.50}

def pick_team():
    team = [p for p in PEOPLE if random.random() < PEOPLE_PROB[p]]
    if not team:
        team = [random.choices(PEOPLE, weights=[PEOPLE_PROB[p] for p in PEOPLE])[0]]
    if len(team) > 3:
        team = random.sample(team, 3)
    return team

def random_start_time(days_back=60):
    day_offset = random.randint(0, days_back - 1)
    target_date = timezone.localdate() - timedelta(days=day_offset)
    minute_of_day = random.randint(7 * 60, 15 * 60)
    hour, minute = divmod(minute_of_day, 60)
    naive_dt = datetime.combine(target_date, time(hour=hour, minute=minute))
    current_tz = timezone.get_current_timezone()
    return timezone.make_aware(naive_dt, current_tz)

def random_value():
    amount = random.uniform(500, 15000)
    return Decimal(f"{amount:.2f}")

def main():
    print("Seeding 500 realistic sessions using only existing suppliers...")
    suppliers = list(Supplier.objects.all())
    supplier_names = [s.name for s in suppliers]
    print(f"Found {len(suppliers)} suppliers: {supplier_names}")
    supplier_map = {s.name: s for s in suppliers}
    sessions_created = 0
    for i in range(500):
        supplier = random.choice(suppliers)
        supplier_name = supplier.name
        supplier_avg = SUPPLIER_AVERAGES.get(supplier_name)
        if supplier_avg is None:
            # fallback: use mean of all averages
            supplier_avg = sum(SUPPLIER_AVERAGES.values()) / len(SUPPLIER_AVERAGES)
        team = pick_team()
        team_size = len(team)
        team_factor = TEAM_SIZE_FACTOR.get(team_size, 1.0)
        base = supplier_avg * team_factor
        avg_speed = sum(PEOPLE_SPEED[p] for p in team) / team_size
        duration = base * (1 + avg_speed)
        noise = random.uniform(-0.10, 0.10) * base
        duration += noise
        duration = max(5, round(duration))
        value = random_value()
        start_time = random_start_time(60)
        end_time = start_time + timedelta(minutes=duration)
        people_working = f"Store 8164 | {', '.join(team)}"
        session = CountingSession.objects.create(
            supplier=supplier,
            value=value,
            people_working=people_working,
            start_time=start_time,
            end_time=end_time,
        )
        SessionParticipant.objects.bulk_create([
            SessionParticipant(
                session=session,
                name=person,
                joined_at=start_time,
                left_at=end_time,
            ) for person in team
        ])
        sessions_created += 1
        print(f"[{i+1:03}/500] {supplier_name} team={team} duration={duration}m value=${value}")
    print(f"Done. Created {sessions_created} sessions.")

if __name__ == "__main__":
    main()
