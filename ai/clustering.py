import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def assign_cluster(df_baseline, math_score, reading_score):
    scaler = StandardScaler()

    combined = pd.concat([
        df_baseline[['math', 'reading']],
        pd.DataFrame([[math_score, reading_score]],
                     columns=['math', 'reading'])
    ])

    kmeans = KMeans(n_clusters=3, n_init=10)
    labels = kmeans.fit_predict(scaler.fit_transform(combined))

    return int(labels[-1])
