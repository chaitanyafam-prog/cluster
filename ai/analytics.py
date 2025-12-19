import numpy as np

def analyze_patterns(history_df):
    if len(history_df) < 2:
        return "Not enough history yet.", 0, 0

    recent_math = history_df['math'].iloc[-1]
    prev_math = history_df['math'].iloc[-2]
    velocity = recent_math - prev_math

    if velocity > 0:
        msg = f"🚀 Improving! You gained {velocity} points since last time."
    elif velocity < 0:
        msg = f"📉 Warning: Score dropped by {abs(velocity)}. Review requested."
    else:
        msg = "⚖️ Stable: No change in performance."

    return msg, velocity, recent_math


def goal_prediction(current_math, velocity, target_score):
    if velocity <= 0:
        return None

    points_needed = target_score - current_math
    sessions_needed = int(np.ceil(points_needed / velocity))
    return sessions_needed
