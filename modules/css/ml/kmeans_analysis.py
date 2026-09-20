import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATABASE = "database/examguard.db"


def run_kmeans():

    connection = sqlite3.connect(DATABASE)

    query = """
        SELECT
            candidate_name,
            candidate_email,
            score,
            total_questions,
            percentage,
            total_warnings,
            looking_left,
            looking_right,
            looking_up,
            looking_down,
            no_face,
            mobile,
            multiple_persons,
            tab_switch
        FROM exam_results
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()


    if len(df) < 3:

        print(
            "Need at least 3 exam results for K-Means."
        )

        return


    features = [
        "score",
        "percentage",
        "total_warnings",
        "looking_left",
        "looking_right",
        "looking_up",
        "looking_down",
        "no_face",
        "mobile",
        "multiple_persons",
        "tab_switch"
    ]


    X = df[features]


    # Normalize the features

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)


    # Create K-Means model

    model = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=10
    )


    # Assign cluster

    df["cluster"] = model.fit_predict(
        X_scaled
    )


    print()
    print("================================")
    print("K-MEANS RESULTS")
    print("================================")


    print(
        df[
            [
                "candidate_name",
                "score",
                "percentage",
                "total_warnings",
                "cluster"
            ]
        ]
    )


    print()
    print("Cluster Analysis:")
    print()


    for cluster in sorted(
        df["cluster"].unique()
    ):

        cluster_data = df[
            df["cluster"] == cluster
        ]


        average_warnings = (
            cluster_data[
                "total_warnings"
            ].mean()
        )


        average_percentage = (
            cluster_data[
                "percentage"
            ].mean()
        )


        print(
            "Cluster:",
            cluster
        )

        print(
            "Students:",
            len(cluster_data)
        )

        print(
            "Average Percentage:",
            round(
                average_percentage,
                2
            )
        )

        print(
            "Average Warnings:",
            round(
                average_warnings,
                2
            )
        )

        print(
            "----------------------------"
        )


    return df


if __name__ == "__main__":

    run_kmeans()