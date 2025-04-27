import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import sqlite3
from datetime import datetime
import seaborn as sns


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('efficiency.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                   month INTEGER,
                  efficiency REAL,
                  profit REAL,
                  costs REAL,
                  investments REAL,
                  market_share REAL,
                  economic_stability REAL,
                  tax_rate REAL)''')
    conn.commit()
    conn.close()


init_db()


# Создание нечеткой системы
def create_fuzzy_system():
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

    # Создание системы
    system_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(system_ctrl)


fuzzy_system = create_fuzzy_system()


class EfficiencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ эффективности предприятия")
        self.root.geometry("900x700")
        self.data = pd.DataFrame()
        self.current_lang = 'ru'
        self.languages = {
            'ru': {
                'title': "Анализ эффективности предприятия",
                'file': "Файл",
                'open': "Открыть",
                'save': "Сохранить",
                'exit': "Выход",
                'analysis': "Анализ",
                'show_analysis': "Показать анализ",
                'trends': "Анализ тенденций",
                'recommendations': "Рекомендации",
                'manual_calc': "Рассчитать вручную",
                'save_db': "Сохранить в БД",
                'load_db': "Загрузить из БД",
                'export': "Экспорт",
                'report': "Отчет",
                'profit': "Прибыль",
                'costs': "Затраты",
                'investments': "Инвестиции",
                'market_share': "Доля рынка",
                'economic_stability': "Экономическая стабильность",
                'tax_rate': "Налоговая ставка",
                'efficiency': "Эффективность"
            },
            'en': {
                'title': "Enterprise Efficiency Analysis",
                'file': "File",
                'open': "Open",
                'save': "Save",
                'exit': "Exit",
                'analysis': "Analysis",
                'show_analysis': "Show Analysis",
                'trends': "Trend Analysis",
                'recommendations': "Recommendations",
                'manual_calc': "Calculate Manually",
                'save_db': "Save to DB",
                'load_db': "Load from DB",
                'export': "Export",
                'report': "Report",
                'profit': "Profit",
                'costs': "Costs",
                'investments': "Investments",
                'market_share': "Market Share",
                'economic_stability': "Economic Stability",
                'tax_rate': "Tax Rate",
                'efficiency': "Efficiency"
            }
        }

        self.create_menu()
        self.create_widgets()
        self.update_language()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # Меню файла
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.languages[self.current_lang]['open'], command=self.load_data)
        file_menu.add_command(label=self.languages[self.current_lang]['save'], command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label=self.languages[self.current_lang]['exit'], command=self.root.quit)
        menubar.add_cascade(label=self.languages[self.current_lang]['file'], menu=file_menu)

        # Меню анализа
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label=self.languages[self.current_lang]['show_analysis'], command=self.show_analysis)
        analysis_menu.add_command(label=self.languages[self.current_lang]['trends'], command=self.analyze_trends)
        analysis_menu.add_command(label=self.languages[self.current_lang]['recommendations'],
                                  command=self.show_recommendations)
        menubar.add_cascade(label=self.languages[self.current_lang]['analysis'], menu=analysis_menu)

        # Меню базы данных
        db_menu = tk.Menu(menubar, tearoff=0)
        db_menu.add_command(label=self.languages[self.current_lang]['save_db'], command=self.save_to_db)
        db_menu.add_command(label=self.languages[self.current_lang]['load_db'], command=self.load_from_db)
        menubar.add_cascade(label="База данных", menu=db_menu)

        # Меню экспорта
        export_menu = tk.Menu(menubar, tearoff=0)
        export_menu.add_command(label=self.languages[self.current_lang]['report'], command=self.export_report)
        menubar.add_cascade(label=self.languages[self.current_lang]['export'], menu=export_menu)

        # Меню языка
        lang_menu = tk.Menu(menubar, tearoff=0)
        lang_menu.add_command(label="Русский", command=lambda: self.change_language('ru'))
        lang_menu.add_command(label="English", command=lambda: self.change_language('en'))
        menubar.add_cascade(label="Язык", menu=lang_menu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм ввода данных
        input_frame = ttk.LabelFrame(main_frame, text="Ручной ввод параметров")
        input_frame.pack(fill=tk.X, pady=5)

        # Поля ввода
        ttk.Label(input_frame, text=self.languages[self.current_lang]['profit'] + ":").grid(row=0, column=0, padx=5,
                                                                                            pady=2, sticky=tk.E)
        self.profit_entry = ttk.Entry(input_frame)
        self.profit_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text=self.languages[self.current_lang]['costs'] + ":").grid(row=1, column=0, padx=5,
                                                                                           pady=2, sticky=tk.E)
        self.costs_entry = ttk.Entry(input_frame)
        self.costs_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text=self.languages[self.current_lang]['investments'] + ":").grid(row=2, column=0,
                                                                                                 padx=5, pady=2,
                                                                                                 sticky=tk.E)
        self.investments_entry = ttk.Entry(input_frame)
        self.investments_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text=self.languages[self.current_lang]['market_share'] + ":").grid(row=3, column=0,
                                                                                                  padx=5, pady=2,
                                                                                                  sticky=tk.E)
        self.market_share_entry = ttk.Entry(input_frame)
        self.market_share_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text=self.languages[self.current_lang]['economic_stability'] + ":").grid(row=4, column=0,
                                                                                                        padx=5, pady=2,
                                                                                                        sticky=tk.E)
        self.economic_stability_entry = ttk.Entry(input_frame)
        self.economic_stability_entry.grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text=self.languages[self.current_lang]['tax_rate'] + ":").grid(row=5, column=0, padx=5,
                                                                                              pady=2, sticky=tk.E)
        self.tax_rate_entry = ttk.Entry(input_frame)
        self.tax_rate_entry.grid(row=5, column=1, padx=5, pady=2)

        # Кнопка ручного расчета
        ttk.Button(input_frame, text=self.languages[self.current_lang]['manual_calc'],
                   command=self.manual_input).grid(row=6, columnspan=2, pady=5)

        # Фрейм кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # Кнопки действий
        ttk.Button(button_frame, text=self.languages[self.current_lang]['show_analysis'],
                   command=self.show_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.languages[self.current_lang]['trends'],
                   command=self.analyze_trends).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.languages[self.current_lang]['recommendations'],
                   command=self.show_recommendations).pack(side=tk.LEFT, padx=5)

        # Таблица для отображения данных
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)

    def update_language(self):
        self.root.title(self.languages[self.current_lang]['title'])
        # Здесь нужно обновить все тексты в интерфейсе

    def change_language(self, lang):
        self.current_lang = lang
        self.create_menu()
        self.update_language()

    def evaluate_efficiency(self, profit_val, costs_val, investments_val,
                            market_share_val, economic_stability_val, tax_rate_val):
        fuzzy_system.input['profit'] = profit_val
        fuzzy_system.input['costs'] = costs_val
        fuzzy_system.input['investments'] = investments_val
        fuzzy_system.input['market_share'] = market_share_val
        fuzzy_system.input['economic_stability'] = economic_stability_val
        fuzzy_system.input['tax_rate'] = tax_rate_val
        fuzzy_system.compute()
        return fuzzy_system.output['efficiency']

    def generate_company_data(self):
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

    def save_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            self.data.to_csv(filename, index=False)
            self.status_var.set(f"Данные сохранены в {filename}")

    def load_data(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.data = pd.read_csv(filename)
            self.data['efficiency'] = self.data.apply(
                lambda row: self.evaluate_efficiency(
                    row['profit'], row['costs'], row['investments'],
                    row['market_share'], row['economic_stability'], row['tax_rate']
                ), axis=1)
            self.update_treeview()
            self.status_var.set(f"Данные загружены из {filename}")

    def update_treeview(self):
        # Очистка текущего дерева
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Настройка колонок
        self.tree["columns"] = list(self.data.columns)
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Добавление данных
        for _, row in self.data.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def plot_data(self, data):
        plt.style.use('seaborn')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # График эффективности
        ax1.plot(data['month'], data['efficiency'], 'b-o', label=self.languages[self.current_lang]['efficiency'])
        ax1.set_ylabel(self.languages[self.current_lang]['efficiency'])
        ax1.legend(loc='upper left')
        ax1.grid(True)
        ax1.set_title(self.languages[self.current_lang]['efficiency'] + " по месяцам")

        # Графики всех показателей
        for column in data.columns[1:-1]:  # исключаем 'month' и 'efficiency'
            ax2.plot(data['month'], data[column], label=self.languages[self.current_lang].get(column, column))

        ax2.set_xlabel(self.languages[self.current_lang].get('month', 'Month'))
        ax2.set_ylabel('Значения')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True)

        plt.tight_layout()
        plt.show()

    def animate_data(self, data):
        fig, ax = plt.subplots(figsize=(10, 5))
        line, = ax.plot([], [], 'r-o')

        def init():
            ax.set_xlim(0, 13)
            ax.set_ylim(0, 100)
            ax.set_xlabel('Месяц')
            ax.set_ylabel('Эффективность')
            ax.set_title('Динамика эффективности предприятия')
            ax.grid(True)
            return line,

        def update(frame):
            x = data['month'][:frame + 1]
            y = data['efficiency'][:frame + 1]
            line.set_data(x, y)

            # Добавляем точки для каждого месяца
            ax.plot(x, y, 'bo')

            # Добавляем текст с значениями
            for i, txt in enumerate(y):
                ax.annotate(f"{txt:.1f}", (x[i], y[i]), textcoords="offset points", xytext=(0, 10), ha='center')

            return line,

        ani = FuncAnimation(fig, update, frames=len(data), init_func=init, blit=False, interval=500)
        plt.show()

    def analyze_trends(self):
        if self.data.empty:
            messagebox.showwarning("Предупреждение", "Нет данных для анализа")
            return

        trends = {}
        for column in self.data.columns[1:]:
            x = self.data['month']
            y = self.data[column]
            coeffs = np.polyfit(x, y, 1)

            if coeffs[0] > 0.5:
                trend = "↑ рост"
            elif coeffs[0] < -0.5:
                trend = "↓ снижение"
            else:
                trend = "→ стабильно"

            trends[column] = f"{trend} (наклон: {coeffs[0]:.2f})"

        analysis = "\n".join([f"{self.languages[self.current_lang].get(k, k)}: {v}" for k, v in trends.items()])
        messagebox.showinfo("Анализ тенденций", analysis)

    def generate_recommendations(self):
        if self.data.empty:
            return self.languages[self.current_lang].get('no_data', "Нет данных для анализа")

        last_row = self.data.iloc[-1]
        recommendations = []

        if last_row['efficiency'] < 30:
            recommendations.append("Срочно примите меры по повышению эффективности!")
        if last_row['costs'] > 70:
            recommendations.append("Рекомендуется сократить затраты")
        if last_row['investments'] < 30:
            recommendations.append("Рассмотрите возможность увеличения инвестиций")
        if last_row['market_share'] < 30:
            recommendations.append("Разработайте стратегию увеличения доли рынка")
        if last_row['tax_rate'] > 50:
            recommendations.append("Проконсультируйтесь с налоговым специалистом для оптимизации")

        return "\n".join(recommendations) if recommendations else "Все показатели в норме"

    def show_recommendations(self):
        if self.data.empty:
            messagebox.showwarning("Предупреждение", "Нет данных для анализа")
            return

        recommendations = self.generate_recommendations()
        messagebox.showinfo("Рекомендации", recommendations)

    def manual_input(self):
        try:
            profit_val = float(self.profit_entry.get())
            costs_val = float(self.costs_entry.get())
            investments_val = float(self.investments_entry.get())
            market_share_val = float(self.market_share_entry.get())
            economic_stability_val = float(self.economic_stability_entry.get())
            tax_rate_val = float(self.tax_rate_entry.get())

            efficiency = self.evaluate_efficiency(
                profit_val, costs_val, investments_val,
                market_share_val, economic_stability_val, tax_rate_val
            )

            messagebox.showinfo(
                "Результат",
                f"{self.languages[self.current_lang]['efficiency']}: {efficiency:.2f}\n\n" +
                self.generate_recommendations_single(
                    profit_val, costs_val, investments_val,
                    market_share_val, economic_stability_val, tax_rate_val
                )
            )
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа")

    def generate_recommendations_single(self, profit, costs, investments, market_share, economic_stability, tax_rate):
        recommendations = []

        if profit < 30:
            recommendations.append("- Увеличьте доходы от продаж")
        if costs > 70:
            recommendations.append("- Оптимизируйте производственные затраты")
        if investments < 20:
            recommendations.append("- Рассмотрите возможность инвестирования в развитие")
        if market_share < 25:
            recommendations.append("- Проведите маркетинговую кампанию для увеличения доли рынка")
        if tax_rate > 50:
            recommendations.append("- Проконсультируйтесь с налоговым специалистом")

        return "Рекомендации:\n" + "\n".join(recommendations) if recommendations else "Все показатели в норме"

    def show_analysis(self):
        self.data = self.generate_company_data()
        self.data['efficiency'] = self.data.apply(
            lambda row: self.evaluate_efficiency(
                row['profit'], row['costs'], row['investments'],
                row['market_share'], row['economic_stability'], row['tax_rate']
            ), axis=1)

        self.update_treeview()
        self.plot_data(self.data)
        self.animate_data(self.data)  # Раскомментируйте для анимированного графика

    def save_to_db(self):
        if self.data.empty:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return

        conn = sqlite3.connect('efficiency.db')
        self.data.to_sql('results', conn, if_exists='append', index=False)
        conn.close()
        self.status_var.set("Данные сохранены в базу данных")

    def load_from_db(self):
        conn = sqlite3.connect('efficiency.db')
        query = "SELECT * FROM results ORDER BY timestamp DESC LIMIT 12"
        self.data = pd.read_sql(query, conn)
        conn.close()

        if not self.data.empty:
            self.update_treeview()
            self.status_var.set("Загружены последние данные из базы данных")
        else:
            messagebox.showinfo("Информация", "В базе данных нет записей")

    def export_report(self):
        if self.data.empty:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")]
        )

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Отчет по эффективности предприятия\n")
                f.write(f"Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")

                # Основные показатели
                f.write("Средние значения показателей:\n")
                f.write(self.data.describe().to_string())
                f.write("\n\n")

                # Тренды
                f.write("Анализ тенденций:\n")
                trends = {}
                for column in self.data.columns[1:]:
                    x = self.data['month']
                    y = self.data[column]
                    coeffs = np.polyfit(x, y, 1)
                    trends[column] = coeffs[0]

                for k, v in sorted(trends.items(), key=lambda item: abs(item[1]), reverse=True):
                    f.write(f"{k}: {'рост' if v > 0 else 'снижение'} ({v:.2f})\n")

                # Рекомендации
                f.write("\nРекомендации:\n")
                f.write(self.generate_recommendations())

            self.status_var.set(f"Отчет сохранен в {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EfficiencyApp(root)
    root.mainloop()