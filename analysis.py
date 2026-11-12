

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 130

df = pd.read_csv("data/ventes_ecommerce_2024_2026.csv", parse_dates=["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)
df["margin_pct"] = df["profit"] / df["revenue"]

print("=== APERÇU ===")
print(df.describe(include="all").T[["count", "mean", "min", "max"]].head(10))

# 1. CA mensuel
monthly = df.groupby("month")[["revenue", "profit"]].sum()
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly["revenue"], marker="o", label="Chiffre d'affaires")
plt.plot(monthly.index, monthly["profit"], marker="o", label="Profit")
plt.xticks(rotation=60)
plt.title("Évolution mensuelle du CA et du profit")
plt.ylabel("€")
plt.legend()
plt.tight_layout()
plt.savefig("charts/01_ca_mensuel.png")
plt.close()

# 2. CA et marge par catégorie
by_cat = df.groupby("category").agg(revenue=("revenue", "sum"),
                                     profit=("profit", "sum"))
by_cat["margin_pct"] = by_cat["profit"] / by_cat["revenue"] * 100
by_cat = by_cat.sort_values("revenue", ascending=False)

fig, ax1 = plt.subplots(figsize=(9, 5))
by_cat["revenue"].plot(kind="bar", ax=ax1, color="#4C72B0")
ax1.set_ylabel("CA (€)")
ax2 = ax1.twinx()
by_cat["margin_pct"].plot(ax=ax2, color="#DD8452", marker="o")
ax2.set_ylabel("Marge (%)")
plt.title("CA et marge par catégorie")
plt.tight_layout()
plt.savefig("charts/02_ca_marge_categorie.png")
plt.close()

# 3. Impact de la remise sur la marge
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="discount_pct", y="margin_pct")
plt.title("Impact du taux de remise sur la marge réalisée")
plt.xlabel("Remise appliquée")
plt.ylabel("Marge (%)")
plt.tight_layout()
plt.savefig("charts/03_remise_vs_marge.png")
plt.close()

# 4. CA par région
by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(9, 5))
by_region.plot(kind="barh", color="#55A868")
plt.title("Chiffre d'affaires par région")
plt.xlabel("CA (€)")
plt.tight_layout()
plt.savefig("charts/04_ca_region.png")
plt.close()

# 5. CA par segment client et canal
pivot = df.pivot_table(index="customer_segment", columns="channel",
                        values="revenue", aggfunc="sum")
plt.figure(figsize=(8, 5))
sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="Blues")
plt.title("CA par segment client et canal de vente")
plt.tight_layout()
plt.savefig("charts/05_segment_canal.png")
plt.close()

print("\n=== INSIGHTS CLÉS ===")
print(f"CA total : {df['revenue'].sum():,.0f} €  |  Profit total : {df['profit'].sum():,.0f} €  |  Marge globale : {df['profit'].sum()/df['revenue'].sum()*100:.1f}%")
print(f"Nombre de commandes : {len(df):,}  |  Panier moyen : {df['revenue'].mean():,.0f} €")

top_cat = by_cat.index[0]
print(f"Catégorie n°1 en CA : {top_cat} ({by_cat.loc[top_cat, 'revenue']:,.0f} €, marge {by_cat.loc[top_cat, 'margin_pct']:.1f}%)")
best_margin_cat = by_cat['margin_pct'].idxmax()
print(f"Catégorie la plus rentable (marge) : {best_margin_cat} ({by_cat.loc[best_margin_cat, 'margin_pct']:.1f}%)")

margin_no_discount = df[df.discount_pct == 0]["margin_pct"].mean() * 100
margin_high_discount = df[df.discount_pct >= 0.2]["margin_pct"].mean() * 100
print(f"Marge moyenne sans remise : {margin_no_discount:.1f}%  vs  avec remise >=20% : {margin_high_discount:.1f}%")

top_region = by_region.index[0]
bottom_region = by_region.index[-1]
print(f"Région leader : {top_region} ({by_region.iloc[0]:,.0f} €)  |  Région la plus faible : {bottom_region} ({by_region.iloc[-1]:,.0f} €)")

best_month = monthly["revenue"].idxmax()
worst_month = monthly["revenue"].idxmin()
print(f"Meilleur mois : {best_month} ({monthly.loc[best_month, 'revenue']:,.0f} €)  |  Mois le plus faible : {worst_month} ({monthly.loc[worst_month, 'revenue']:,.0f} €)")
