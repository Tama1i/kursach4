import numpy as np
import pandas as pd


# Функция генерации данных для компании с учетом изменяющейся налоговой ставки
def generate_company_data(seed=None):
    if seed is not None:
        np.random.seed(seed)

    months = np.arange(1, 13)
    data = pd.DataFrame({
        'month': months,
        'profit': np.random.randint(30, 90, size=12),
        'costs': np.random.randint(20, 70, size=12),
        'investments': np.random.randint(10, 80, size=12),
        'market_share': np.random.randint(20, 100, size=12),
        'economic_stability': np.random.randint(40, 90, size=12),
        'tax_rate': [20] * 5 + [50] * 2 + [20] * 5  # Повышенная налоговая ставка на 6-7 месяц
    })
    return data


# Генерация трех различных пакетов данных
company_data_1 = generate_company_data(seed=42)
company_data_2 = generate_company_data(seed=99)
company_data_3 = generate_company_data(seed=123)

# Сохранение данных в CSV
company_data_1.to_csv("company_data_1.csv", index=False)
company_data_2.to_csv("company_data_2.csv", index=False)
company_data_3.to_csv("company_data_3.csv", index=False)

company_data_1.head(), company_data_2.head(), company_data_3.head()
