import numpy as np
import pandas as pd

def run_topsis_df(df, weights, impacts):
    matrix = df.iloc[:, 1:]

    weights = np.array(weights, dtype=float)
    weights = weights / weights.sum()

    norm = np.sqrt((matrix ** 2).sum())
    norm_matrix = matrix / norm
    weighted_matrix = norm_matrix * weights

    ideal_best = []
    ideal_worst = []

    for i, impact in enumerate(impacts):
        col = weighted_matrix.iloc[:, i]
        if impact == "+":
            ideal_best.append(col.max())
            ideal_worst.append(col.min())
        else:
            ideal_best.append(col.min())
            ideal_worst.append(col.max())

    dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))

    scores = dist_worst / (dist_best + dist_worst)
    ranks = scores.rank(ascending=False).astype(int)

    df["Topsis Score"] = scores
    df["Rank"] = ranks

    return df.sort_values("Rank")
