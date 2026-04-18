import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("db/db.sqlite")

products = pd.read_sql("SELECT * FROM Product", conn)
bom = pd.read_sql("SELECT * FROM BOM", conn)
bom_components = pd.read_sql("SELECT * FROM BOM_Component", conn)

# BOM_Component -> BOM join
df = bom_components.merge(
    bom,
    left_on="BOMId",
    right_on="Id",
    suffixes=("_component", "_bom")
)

# product info des konsumierten Produkts holen (= raw material)
df = df.merge(
    products[["Id", "SKU", "Type"]],
    left_on="ConsumedProductId",
    right_on="Id",
    how="left"
)

# produced product -> company information
produced = products[["Id", "CompanyId"]].rename(columns={"Id": "ProducedProductId"})
df = df.merge(produced, on="ProducedProductId", how="left")

companies = pd.read_sql("SELECT * FROM Company", conn)
df = df.merge(companies[["Id", "Name"]], left_on="CompanyId", right_on="Id", how="left")
df = df.rename(columns={"Name": "Company"})

# nur raw materials
df = df[df["Type"] == "raw-material"].copy()

# lesbaren Namen aus SKU extrahieren
df["ingredient"] = df["SKU"].str.extract(r"RM-C\d+-(.*)-[a-z0-9]+", expand=False)

# fallback, falls regex mal nicht matched
df["ingredient"] = df["ingredient"].fillna(df["SKU"])

# count products per ingredient per company
counts = (
    df.groupby(["ingredient", "Company"])["ProducedProductId"]
      .nunique()
      .reset_index()
)

# total usage per ingredient (for ranking)
totals = counts.groupby("ingredient")["ProducedProductId"].sum().sort_values(ascending=False)

# top ingredients
top_n = 20
top_ingredients = totals.head(top_n).index

plot_df = counts[counts["ingredient"].isin(top_ingredients)]
plot_df = plot_df.pivot(index="ingredient", columns="Company", values="ProducedProductId").fillna(0)

# sort ingredients by total usage (bucket height)
plot_df = plot_df.loc[plot_df.sum(axis=1).sort_values(ascending=False).index]

fig, ax = plt.subplots(figsize=(12,6))
plot_df.plot(kind="bar", stacked=True, ax=ax)

ax.set_title("Top Raw Materials Used Across Products (Colored by Company)")
ax.set_xlabel("Raw Material")
ax.set_ylabel("Number of Distinct Products Using It")
plt.xticks(rotation=45, ha="right")

ax.legend(title="Company", bbox_to_anchor=(1.02,1), loc="upper left")

fig.tight_layout()
plt.show()