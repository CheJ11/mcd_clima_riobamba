from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Paths and settings
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "riobamba_daily_2015-01-01_2026-08-31.csv"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok = True)

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
BASE_START, BASE_END = "2015-01-01", "2024-12-31"
RECENT_START, RECENT_END = "2025-09-01", "2026-08-31"

plt.rcParams.update({"savefig.dpi": 150, "axes.grid": True, "grid.alpha": 0.3})

# Load daily data
df = pd.read_csv(DATA_FILE, parse_dates = ["date"])
df = df.set_index("date")
df = df.rename(columns = {
	"temperature_2m_mean": "t_mean",
	"temperature_2m_max": "t_max",
	"temperature_2m_min": "t_min",
	"precipitation_sum": "prcp",
})

# Monthly values: mean temperature, total precipitation, rainy days (>= 1 mm)
mensual = df[["t_mean", "t_max", "t_min"]].resample("MS").mean()
mensual["prcp"] = df["prcp"].resample("MS").sum()
mensual["dias_lluvia"] = (df["prcp"] >= 1).resample("MS").sum()
mensual["mes"] = mensual.index.month

# Habitual behaviour: average, minimum and maximum of each calendar month in the base period
base = mensual.loc[BASE_START:BASE_END]
habitual = base.groupby("mes").mean()
habitual_min = base.groupby("mes").min()
habitual_max = base.groupby("mes").max()

# Recent period, indexed by calendar month to compare with habitual
reciente = mensual.loc[RECENT_START:RECENT_END].set_index("mes").sort_index()

# Figure 1: daily mean temperature
fig, ax = plt.subplots(figsize = (12, 4))
ax.plot(df.index, df["t_mean"], lw = 0.4, alpha = 0.4, label = "Diaria")
ax.plot(df["t_mean"].rolling(30, center = True).mean(), lw = 1.5, color = "k", label = "Media móvil 30 días")
ax.set(title = "Riobamba: temperatura media diaria (2015–2026)", ylabel = "°C")
ax.legend(loc = "upper left")
fig.tight_layout()
fig.savefig(FIG_DIR / "01_temperatura_diaria.png")
plt.close(fig)

# Figure 2: average monthly precipitation, wettest and driest month highlighted
colores = ["tab:blue"] * 12
colores[habitual["prcp"].idxmax() - 1] = "navy"
colores[habitual["prcp"].idxmin() - 1] = "tab:orange"

fig, ax = plt.subplots(figsize = (9, 4.5))
ax.bar(habitual.index, habitual["prcp"], color = colores)
ax.set_xticks(habitual.index, MESES)
ax.set(title = "Precipitación mensual promedio (2015–2024)", ylabel = "mm/mes")
fig.tight_layout()
fig.savefig(FIG_DIR / "02_precipitacion_mensual.png")
plt.close(fig)

# Figure 3: average number of rainy days per month
fig, ax = plt.subplots(figsize = (9, 4.5))
ax.bar(habitual.index, habitual["dias_lluvia"], color = "tab:cyan")
ax.set_xticks(habitual.index, MESES)
ax.set(title = "Días con lluvia (≥ 1 mm) por mes, promedio 2015–2024", ylabel = "días")
fig.tight_layout()
fig.savefig(FIG_DIR / "03_dias_lluvia.png")
plt.close(fig)

# Figure 4: annual cycle of maximum, mean and minimum temperature
fig, ax = plt.subplots(figsize = (9, 4.5))
ax.plot(habitual.index, habitual["t_max"], "o-", color = "tab:red", label = "Máxima")
ax.plot(habitual.index, habitual["t_mean"], "o-", color = "k", label = "Media")
ax.plot(habitual.index, habitual["t_min"], "o-", color = "tab:blue", label = "Mínima")
ax.set_xticks(habitual.index, MESES)
ax.set(title = "Temperatura promedio por mes (2015–2024)", ylabel = "°C")
ax.legend()
fig.tight_layout()
fig.savefig(FIG_DIR / "04_temperatura_mensual.png")
plt.close(fig)

# Figure 5: recent vs habitual temperature (band = min–max of the base period)
fig, ax = plt.subplots(figsize = (9, 4.5))
ax.fill_between(habitual.index, habitual_min["t_mean"], habitual_max["t_mean"],
				color = "grey", alpha = 0.25, label = "Rango 2015–2024")
ax.plot(habitual.index, habitual["t_mean"], "o-", color = "k", label = "Habitual (promedio 2015–2024)")
ax.plot(reciente.index, reciente["t_mean"], "o-", color = "tab:red", label = "Sep 2025 – Ago 2026")
ax.set_xticks(habitual.index, MESES)
ax.set(title = "Temperatura media mensual: reciente vs habitual", ylabel = "°C")
ax.legend()
fig.tight_layout()
fig.savefig(FIG_DIR / "05_temperatura_reciente_vs_habitual.png")
plt.close(fig)

# Figure 6: recent vs habitual precipitation (band = min–max of the base period)
fig, ax = plt.subplots(figsize = (9, 4.5))
ax.fill_between(habitual.index, habitual_min["prcp"], habitual_max["prcp"],
				color = "grey", alpha = 0.25, label = "Rango 2015–2024")
ax.plot(habitual.index, habitual["prcp"], "o-", color = "k", label = "Habitual (promedio 2015–2024)")
ax.plot(reciente.index, reciente["prcp"], "o-", color = "tab:blue", label = "Sep 2025 – Ago 2026")
ax.set_xticks(habitual.index, MESES)
ax.set(title = "Precipitación mensual: reciente vs habitual", ylabel = "mm/mes")
ax.legend()
fig.tight_layout()
fig.savefig(FIG_DIR / "06_precipitacion_reciente_vs_habitual.png")
plt.close(fig)

# P1: precipitation and rainy days per month, from wettest to driest
print("P1. Precipitación y días de lluvia promedio por mes:")
p1 = habitual[["prcp", "dias_lluvia"]].sort_values("prcp", ascending = False)
p1.index = [MESES[m - 1] for m in p1.index]
print(p1.round(1))

# P2: warmest and coldest month, annual and daily temperature range
print("\nP2. Temperatura:")
print(f"  Mes más cálido: {MESES[habitual['t_mean'].idxmax() - 1]} ({habitual['t_mean'].max():.1f} °C)")
print(f"  Mes más frío:   {MESES[habitual['t_mean'].idxmin() - 1]} ({habitual['t_mean'].min():.1f} °C)")
print(f"  Diferencia entre mes más cálido y más frío: {habitual['t_mean'].max() - habitual['t_mean'].min():.1f} °C")
print(f"  Diferencia promedio entre máxima y mínima diaria: {(habitual['t_max'] - habitual['t_min']).mean():.1f} °C")

# P3: recent months vs habitual, flagging months outside the base-period range
print("\nP3. Reciente vs habitual:")
p3 = pd.DataFrame({
	"T_reciente": reciente["t_mean"],
	"T_habitual": habitual["t_mean"],
	"dif_T": reciente["t_mean"] - habitual["t_mean"],
	"P_reciente": reciente["prcp"],
	"P_habitual": habitual["prcp"],
	"T_fuera_rango": (reciente["t_mean"] < habitual_min["t_mean"]) | (reciente["t_mean"] > habitual_max["t_mean"]),
	"P_fuera_rango": (reciente["prcp"] < habitual_min["prcp"]) | (reciente["prcp"] > habitual_max["prcp"]),
})
p3.index = [MESES[m - 1] for m in p3.index]
print(p3.round(1))
print(f"\n  Diferencia media de temperatura: {p3['dif_T'].mean():+.2f} °C")
print(f"  Lluvia total: {reciente['prcp'].sum():.0f} mm vs {habitual['prcp'].sum():.0f} mm habituales")