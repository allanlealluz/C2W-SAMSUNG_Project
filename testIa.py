import seaborn as sns
from models import get_student_scores
data = get_student_scores()
sns.scatterplot(data = data, x = 'nota', y = 'concluida', hue = 'median_house_value')