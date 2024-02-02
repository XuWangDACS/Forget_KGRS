import pandas as pd
import numpy as np

# Dummy data for recommendations and explanations
recommendations = ['Item1', 'Item2', 'Item3', 'Item4', 'Item5']
explanations = ['Explanation1', 'Explanation2', 'Explanation3', 'Explanation4', 'Explanation5']

# Generate random scores for recency, popularity, and diversity
np.random.seed(42)  # For reproducibility
recency_scores = np.random.rand(len(recommendations))
popularity_scores = np.random.rand(len(recommendations))
diversity_scores = np.random.rand(len(recommendations))

# Weights for each property
weights = {'recency': 0.3, 'popularity': 0.4, 'diversity': 0.3}

# Re-ranking function
def re_rank(recommendations, explanations, recency_scores, popularity_scores, diversity_scores, weights):
    data = pd.DataFrame({
        'recommendation': recommendations,
        'explanation': explanations,
        'recency_score': recency_scores,
        'popularity_score': popularity_scores,
        'diversity_score': diversity_scores
    })

    # Calculate final score based on weighted sum of property scores
    data['final_score'] = (weights['recency'] * data['recency_score'] +
                           weights['popularity'] * data['popularity_score'] +
                           weights['diversity'] * data['diversity_score'])

    # Sort data based on final score
    data_sorted = data.sort_values(by='final_score', ascending=False)

    return data_sorted['recommendation'].tolist(), data_sorted['explanation'].tolist()

# Re-rank recommendations and explanations
new_recommendations, new_explanations = re_rank(recommendations, explanations, recency_scores, popularity_scores, diversity_scores, weights)

print("New Recommendations:", new_recommendations)
print("New Explanations:", new_explanations)
