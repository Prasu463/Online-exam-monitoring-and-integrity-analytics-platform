import pandas as pd
import matplotlib.pyplot as plt
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
print("Loading integrity data...")

df = pd.read_csv(INPUT_FILE)

print(
    "Sessions loaded:",
    len(df)
)


if df.empty:

    print("No data available.")

    exit()


# ============================================================
# 1. INTEGRITY SCORE DISTRIBUTION
# ============================================================

print()
print(
    "Creating integrity score distribution..."
)


plt.figure(
    figsize=(10, 6)
)


plt.hist(

    df["integrity_score"],

    bins=8,

    edgecolor="black"

)


plt.xlabel(
    "Integrity Score"
)

plt.ylabel(
    "Number of Sessions"
)

plt.title(
    "Integrity Score Distribution"
)

plt.grid(
    axis="y",
    alpha=0.3
)


distribution_file = os.path.join(

    OUTPUT_FOLDER,

    "integrity_score_distribution.png"

)


plt.savefig(

    distribution_file,

    dpi=150,

    bbox_inches="tight"

)


plt.show()


print(
    "Saved:",
    distribution_file
)


# ============================================================
# 2. EVENT FREQUENCY HEATMAP
# ============================================================

print()
print(
    "Creating event frequency heatmap..."
)


event_columns = [

    "FACE_PRESENT",

    "FACE_ABSENT",

    "LOOKING_LEFT",

    "LOOKING_RIGHT",

    "LOOKING_UP",

    "LOOKING_DOWN",

    "MULTIPLE_PERSONS",

    "MOBILE_PHONE",

    "TAB_SWITCH",

    "WINDOW_BLUR",

    "KEYBOARD_ACTIVITY",

    "MOUSE_ACTIVITY"

]


# Make sure all columns exist

for column in event_columns:

    if column not in df.columns:

        df[column] = 0


# Create matrix

heatmap_data = df[
    event_columns
].copy()


# Use session IDs as rows

heatmap_data.index = df[
    "session_id"
]


# Limit long session IDs for display

heatmap_data.index = [

    str(x)[-8:]

    for x in heatmap_data.index

]


plt.figure(

    figsize=(14, 9)

)


plt.imshow(

    heatmap_data,

    aspect="auto"

)


plt.colorbar(
    label="Event Count"
)


plt.xticks(

    range(len(event_columns)),

    event_columns,

    rotation=60,

    ha="right"

)


plt.yticks(
    range(len(heatmap_data)),
    heatmap_data.index
)


plt.xlabel(
    "Event Type"
)

plt.ylabel(
    "Session"
)

plt.title(
    "Exam Session Event Frequency Heatmap"
)


plt.tight_layout()


heatmap_file = os.path.join(

    OUTPUT_FOLDER,

    "event_frequency_heatmap.png"

)


plt.savefig(

    heatmap_file,

    dpi=150,

    bbox_inches="tight"

)


plt.show()


print(
    "Saved:",
    heatmap_file
)


# ============================================================
# 3. COHORT RISK PROFILING
# ============================================================

print()
print(
    "Creating cohort risk profile..."
)


risk_counts = df[
    "risk_label"
].value_counts()


# Ensure all risk categories exist

for risk in [

    "LOW",

    "MEDIUM",

    "HIGH"

]:

    if risk not in risk_counts:

        risk_counts[risk] = 0


risk_counts = risk_counts[
    [
        "LOW",
        "MEDIUM",
        "HIGH"
    ]
]


print()
print(
    "======================================================"
)

print(
    "                 COHORT RISK PROFILE"
)

print(
    "======================================================"
)


for risk, count in risk_counts.items():

    percentage = (

        count
        /
        len(df)
        *
        100

    )


    print(

        f"{risk}: "
        f"{count} sessions "
        f"({percentage:.2f}%)"

    )


print(
    "------------------------------------------------------"
)


# ============================================================
# RISK BAR CHART
# ============================================================

plt.figure(

    figsize=(8, 6)

)


plt.bar(

    risk_counts.index,

    risk_counts.values

)


plt.xlabel(
    "Risk Level"
)

plt.ylabel(
    "Number of Sessions"
)

plt.title(
    "Cohort Risk Profile"
)


plt.grid(

    axis="y",

    alpha=0.3

)


risk_file = os.path.join(

    OUTPUT_FOLDER,

    "cohort_risk_profile.png"

)


plt.savefig(

    risk_file,

    dpi=150,

    bbox_inches="tight"

)


plt.show()


print(
    "Saved:",
    risk_file
)


# ============================================================
# 4. SUMMARY STATISTICS
# ============================================================

print()
print(
    "======================================================"
)

print(
    "              ANALYTICS SUMMARY"
)

print(
    "======================================================"
)


print(

    "Average Integrity Score:",

    round(
        df["integrity_score"].mean(),
        2
    )

)


print(

    "Minimum Integrity Score:",

    round(
        df["integrity_score"].min(),
        2
    )

)


print(

    "Maximum Integrity Score:",

    round(
        df["integrity_score"].max(),
        2
    )

)


print(

    "Average Face Presence Ratio:",

    round(
        df["face_presence_ratio"].mean(),
        3
    )

)


print(

    "Total Sessions:",

    len(df)

)


print(
    "======================================================"
)


# ============================================================
# FINISHED
# ============================================================

print()

print(
    "Milestone 3 analytics completed successfully."
)

print()

print(
    "Generated files:"
)

print(
    "1. integrity_score_distribution.png"
)

print(
    "2. event_frequency_heatmap.png"
)

print(
    "3. cohort_risk_profile.png"
)

print(
    "======================================================"
)