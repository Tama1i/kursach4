import numpy as np
import pandas as pd

class DataAnalyzer:
    @staticmethod
    def generate_test_data():
        """Генерирует тестовые данные"""
        months = np.arange(1, 13)
        return pd.DataFrame({
            'month': months,
            'profit': np.random.randint(30, 90, size=12),
            'costs': np.random.randint(20, 70, size=12),
            'investments': np.random.randint(10, 80, size=12),
            'market_share': np.random.randint(20, 100, size=12),
            'economic_stability': np.random.randint(40, 90, size=12),
            'tax_rate': [20] * 5 + [50] * 2 + [20] * 5
        })

class TrendAnalyzer:
    @staticmethod
    def analyze_trends(data):
        """Анализирует тенденции в данных"""
        trends = {}
        for column in data.columns[1:]:  # исключаем 'month'
            x = data['month']
            y = data[column]
            coeffs = np.polyfit(x, y, 1)
            trends[column] = coeffs[0]
        return trends

class RecommendationEngine:
    @staticmethod
    def generate_recommendations(data):
        """Генерирует рекомендации на основе данных"""
        recommendations = []
        last_row = data.iloc[-1] if not data.empty else None

        if last_row is not None:
            if last_row['efficiency'] < 30:
                recommendations.append("Срочно примите меры по повышению эффективности!")
            if last_row['costs'] > 70:
                recommendations.append("Рекомендуется сократить затраты")
            if last_row['investments'] < 30:
                recommendations.append("Рассмотрите возможность увеличения инвестиций")
            if last_row['market_share'] < 30:
                recommendations.append("Разработайте стратегию увеличения доли рынка")
            if last_row['tax_rate'] > 50:
                recommendations.append("Проконсультируйтесь с налоговым специалистом")

        return recommendations if recommendations else ["Все показатели в норме"]