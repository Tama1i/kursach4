import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl


class FuzzyEfficiencySystem:
    def __init__(self):
        self.system = self._create_system()

    def _create_system(self):
        # Входные переменные
        profit = ctrl.Antecedent(np.arange(0, 101, 1), 'profit')
        costs = ctrl.Antecedent(np.arange(0, 101, 1), 'costs')
        investments = ctrl.Antecedent(np.arange(0, 101, 1), 'investments')
        market_share = ctrl.Antecedent(np.arange(0, 101, 1), 'market_share')
        economic_stability = ctrl.Antecedent(np.arange(0, 101, 1), 'economic_stability')
        tax_rate = ctrl.Antecedent(np.arange(0, 101, 1), 'tax_rate')

        # Выходная переменная
        efficiency = ctrl.Consequent(np.arange(0, 101, 1), 'efficiency')

        # Функции принадлежности
        for var in [profit, costs, investments, market_share, economic_stability, tax_rate]:
            var['low'] = fuzz.trimf(var.universe, [0, 0, 50])
            var['medium'] = fuzz.trimf(var.universe, [25, 50, 75])
            var['high'] = fuzz.trimf(var.universe, [50, 100, 100])

        efficiency['low'] = fuzz.trimf(efficiency.universe, [0, 0, 50])
        efficiency['medium'] = fuzz.trimf(efficiency.universe, [25, 50, 75])
        efficiency['high'] = fuzz.trimf(efficiency.universe, [50, 100, 100])

        # Правила
        rules = [
            ctrl.Rule(profit['high'] & costs['low'] & investments['medium'] &
                      market_share['high'] & economic_stability['high'] & tax_rate['low'], efficiency['high']),
            ctrl.Rule(profit['medium'] & costs['medium'] & investments['high'] &
                      market_share['medium'] & economic_stability['medium'] & tax_rate['medium'], efficiency['medium']),
            ctrl.Rule(profit['low'] | costs['high'] | investments['low'] |
                      market_share['low'] | economic_stability['low'] | tax_rate['high'], efficiency['low']),
            ctrl.Rule(profit['high'] & costs['low'] & investments['high'], efficiency['high']),
            ctrl.Rule(profit['high'] & market_share['high'] & economic_stability['medium'], efficiency['high']),
            ctrl.Rule(tax_rate['high'] & (profit['medium'] | profit['low']), efficiency['low'])
        ]

        return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

    def evaluate(self, inputs):
        """Вычисляет эффективность на основе входных параметров"""
        for key, value in inputs.items():
            self.system.input[key] = value
        self.system.compute()
        return self.system.output['efficiency']