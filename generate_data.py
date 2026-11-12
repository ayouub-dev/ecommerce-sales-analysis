

import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)

REGIONS = ["Île-de-France", "Auvergne-Rhône-Alpes", "Hauts-de-France",
           "Nouvelle-Aquitaine", "Occitanie", "Provence-Alpes-Côte d'Azur",
           "Grand Est", "Bretagne"]

# poids de population/activité économique -> volume de commandes par région
REGION_WEIGHTS = [0.27, 0.15, 0.11, 0.10, 0.10, 0.10, 0.09, 0.08]

CATEGORIES = {
    "Électronique":     {"base_price": (80, 650),  "margin": 0.14, "weight": 0.22},
    "Mode":             {"base_price": (15, 120),   "margin": 0.42, "weight": 0.30},
    "Maison & Jardin":  {"base_price": (10, 300),   "margin": 0.33, "weight": 0.18},
    "Sport & Loisirs":  {"base_price": (12, 250),   "margin": 0.30, "weight": 0.15},
    "Beauté & Santé":   {"base_price": (8, 90),     "margin": 0.48, "weight": 0.15},
}

SEGMENTS = {"Particulier": 0.72, "Professionnel": 0.20, "Grand compte": 0.08}

CHANNELS = {"Site web": 0.55, "Application mobile": 0.30, "Marketplace": 0.15}

START = date(2024, 11, 1)
N_DAYS = 730  # 24 mois
N_ORDERS = 18000

cat_names = list(CATEGORIES.keys())
cat_weights = [v["weight"] for v in CATEGORIES.values()]

def seasonality_factor(d: date) -> float:
    """Pics en novembre-décembre (soldes/fêtes) et en juin-juillet (soldes d'été)."""
    m = d.month
    if m in (11, 12):
        return 1.6
    if m in (6, 7):
        return 1.25
    if m in (1,):
        return 1.3  # soldes d'hiver
    if m in (8,):
        return 0.7  # creux estival
    return 1.0

rows = []
order_id = 100000

for day_offset in range(N_DAYS):
    d = START + timedelta(days=day_offset)
    season = seasonality_factor(d)
    weekday_factor = 1.25 if d.weekday() >= 4 else 1.0  # vendredi-dimanche plus actifs
    daily_orders = max(1, int(rng.poisson((N_ORDERS / N_DAYS) * season * weekday_factor)))

    for _ in range(daily_orders):
        order_id += 1
        category = rng.choice(cat_names, p=cat_weights)
        cat_info = CATEGORIES[category]
        region = rng.choice(REGIONS, p=REGION_WEIGHTS)
        segment = rng.choice(list(SEGMENTS.keys()), p=list(SEGMENTS.values()))
        channel = rng.choice(list(CHANNELS.keys()), p=list(CHANNELS.values()))

        price = rng.uniform(*cat_info["base_price"])
        quantity = rng.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.2, 0.15, 0.1, 0.06, 0.04])

        # Les remises sont plus fréquentes en période de soldes/fêtes
        discount_prob = 0.55 if season > 1.2 else 0.25
        discount = 0.0
        if rng.random() < discount_prob:
            discount = float(rng.choice([0.05, 0.10, 0.15, 0.20, 0.30],
                                         p=[0.30, 0.30, 0.20, 0.15, 0.05]))

        revenue = round(price * quantity * (1 - discount), 2)
        base_margin = cat_info["margin"]
        # Une remise élevée écrase la marge plus que proportionnellement
        effective_margin = max(0.02, base_margin - discount * 0.9)
        profit = round(revenue * effective_margin, 2)

        # Professionnels/Grands comptes commandent plus mais avec marge négociée plus faible
        if segment == "Grand compte":
            quantity = quantity * rng.integers(3, 8)
            revenue = round(price * quantity * (1 - max(discount, 0.12)), 2)
            profit = round(revenue * max(0.05, base_margin - 0.15), 2)
        elif segment == "Professionnel":
            quantity = quantity * rng.integers(1, 4)
            revenue = round(price * quantity * (1 - max(discount, 0.05)), 2)
            profit = round(revenue * max(0.08, base_margin - 0.08), 2)

        rows.append({
            "order_id": order_id,
            "order_date": d.isoformat(),
            "region": region,
            "category": category,
            "customer_segment": segment,
            "channel": channel,
            "quantity": int(quantity),
            "unit_price": round(price, 2),
            "discount_pct": discount,
            "revenue": revenue,
            "profit": profit,
        })

df = pd.DataFrame(rows)
df.sort_values(["order_date", "order_id"], inplace=True)
df.to_csv("/home/claude/ecommerce-sales-analysis/data/ventes_ecommerce_2024_2026.csv", index=False)

print(f"Dataset généré : {len(df):,} commandes")
print(f"Période : {df['order_date'].min()} -> {df['order_date'].max()}")
print(f"CA total : {df['revenue'].sum():,.0f} €")
print(f"Profit total : {df['profit'].sum():,.0f} €")
