import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "modules/ml/output/integrity_scores.csv"

OUTPUT_FOLDER = "modules/ml/output"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading integrity scores...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    "Sessions found:",
    len(df)
)


# ============================================================
# CHECK DATA
# ============================================================

if len(df) < 3:

    print(
        "Need at least 3 exam sessions for K-Means."
    )

    exit()


# ============================================================
# FEATURES
# ============================================================

features = [

    "total_events",

    "total_penalty",

    "face_presence_ratio",

    "integrity_score"

]


X = df[features].copy()


# ============================================================
# HANDLE MISSING VALUES
# ============================================================

X = X.fillna(0)


# ============================================================
# STANDARDIZE FEATURES
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# K-MEANS
# ============================================================

print()
print("Running K-Means clustering...")


kmeans = KMeans(

    n_clusters=3,

    random_state=42,

    n_init=10

)


df["cluster"] = kmeans.fit_predict(
    X_scaled
)


# ============================================================
# ANALYZE CLUSTERS
# ============================================================

cluster_summary = df.groupby(
    "cluster"
).agg(

    sessions=(
        "session_id",
        "count"
    ),

    average_score=(
        "integrity_score",
        "mean"
    ),

    average_penalty=(
        "total_penalty",
        "mean"
    ),

    average_face_ratio=(
        "face_presence_ratio",
        "mean"
    ),

    average_events=(
        "total_events",
        "mean"
    )

).reset_index()


# ============================================================
# ROUND VALUES
# ============================================================

cluster_summary[
    "average_score"
] = cluster_summary[
    "average_score"
].round(2)


cluster_summary[
    "average_penalty"
] = cluster_summary[
    "average_penalty"
].round(2)


cluster_summary[
    "average_face_ratio"
] = cluster_summary[
    "average_face_ratio"
].round(3)


cluster_summary[
    "average_events"
] = cluster_summary[
    "average_events"
].round(2)


# ============================================================
# ASSIGN CLUSTER RISK
# ============================================================

def determine_cluster_risk(score):

    if score >= 75:

        return "LOW"

    elif score >= 50:

        return "MEDIUM"

    else:

        return "HIGH"


cluster_summary[
    "cluster_risk"
] = cluster_summary[
    "average_score"
].apply(
    determine_cluster_risk
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print(
    "======================================================"
)

print(
    "             K-MEANS SESSION CLUSTERS"
)

print(
    "======================================================"
)


for _, row in cluster_summary.iterrows():

    print()

    print(
        "Cluster:",
        int(row["cluster"])
    )

    print(
        "Sessions:",
        int(row["sessions"])
    )

    print(
        "Average Integrity Score:",
        row["average_score"]
    )

    print(
        "Average Penalty:",
        row["average_penalty"]
    )

    print(
        "Average Face Presence:",
        row["average_face_ratio"]
    )

    print(
        "Average Events:",
        row["average_events"]
    )

    print(
        "Risk Profile:",
        row["cluster_risk"]
    )

    print(
        "------------------------------------------------------"
    )


# ============================================================
# SAVE SESSION CLUSTERS
# ============================================================

cluster_file = os.path.join(

    OUTPUT_FOLDER,

    "kmeans_session_clusters.csv"

)


df.to_csv(

    cluster_file,

    index=False

)


# ============================================================
# SAVE CLUSTER SUMMARY
# ============================================================

summary_file = os.path.join(

    OUTPUT_FOLDER,

    "kmeans_cluster_summary.csv"

)


cluster_summary.to_csv(

    summary_file,

    index=False

)


print()

print(
    "Session cluster file:"
)

print(
    cluster_file
)


print()

print(
    "Cluster summary file:"
)

print(
    summary_file
)


# ============================================================
# VISUALIZATION
# ============================================================

plt.figure(
    figsize=(10, 6)
)


for cluster in sorted(
    df["cluster"].unique()
):

    cluster_data = df[
        df["cluster"] == cluster
    ]

    plt.scatter(

        cluster_data[
            "total_penalty"
        ],

        cluster_data[
            "integrity_score"
        ],

        label=f"Cluster {cluster}",

        s=80

    )


plt.xlabel(
    "Total Penalty"
)

plt.ylabel(
    "Integrity Score"
)

plt.title(
    "Exam Session K-Means Clustering"
)

plt.legend()

plt.grid(
    True,
    alpha=0.3
)


plot_file = os.path.join(

    OUTPUT_FOLDER,

    "kmeans_clusters.png"

)


plt.savefig(
    plot_file,
    dpi=150,
    bbox_inches="tight"
)


plt.show()


print()

print(
    "Cluster visualization saved:"
)

print(
    plot_file
)


print()

print(
    "K-Means analysis completed successfully."
)