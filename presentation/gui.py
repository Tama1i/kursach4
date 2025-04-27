import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data.database import DatabaseManager
from logic.fuzzy_logic import FuzzyEfficiencySystem
from logic.analysis import DataAnalyzer, TrendAnalyzer, RecommendationEngine


class EfficiencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ эффективности предприятия")
        self.root.geometry("1000x800")

        # Инициализация компонентов системы
        self.db_manager = DatabaseManager()
        self.fuzzy_system = FuzzyEfficiencySystem()
        self.data = pd.DataFrame()

        # Настройка интерфейса
        self._setup_ui()
        self._create_menu()

    def _setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель ввода параметров
        input_frame = ttk.LabelFrame(main_frame, text="Параметры предприятия")
        input_frame.pack(fill=tk.X, pady=5)

        # Поля ввода
        params = [
            ('profit', 'Прибыль:'), ('costs', 'Затраты:'),
            ('investments', 'Инвестиции:'), ('market_share', 'Доля рынка:'),
            ('economic_stability', 'Экон. стабильность:'), ('tax_rate', 'Налоговая ставка:')
        ]

        self.entries = {}
        for i, (param, label) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky=tk.E)
            entry = ttk.Entry(input_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[param] = entry

        # Кнопка расчета
        ttk.Button(
            input_frame,
            text="Рассчитать эффективность",
            command=self._calculate_efficiency
        ).grid(row=len(params), columnspan=2, pady=10)

        # Графики
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=main_frame)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        # Меню файла
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Загрузить данные", command=self._load_data)
        file_menu.add_command(label="Сохранить отчет", command=self._export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню анализа
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Показать анализ", command=self._show_analysis)
        analysis_menu.add_command(label="Анализ тенденций", command=self._show_trends)
        analysis_menu.add_command(label="Рекомендации", command=self._show_recommendations)
        menubar.add_cascade(label="Анализ", menu=analysis_menu)

        # Меню базы данных
        db_menu = tk.Menu(menubar, tearoff=0)
        db_menu.add_command(label="Сохранить в БД", command=self._save_to_db)
        db_menu.add_command(label="Загрузить из БД", command=self._load_from_db)
        menubar.add_cascade(label="База данных", menu=db_menu)

        self.root.config(menu=menubar)

    def _calculate_efficiency(self):
        try:
            inputs = {
                'profit': float(self.entries['profit'].get()),
                'costs': float(self.entries['costs'].get()),
                'investments': float(self.entries['investments'].get()),
                'market_share': float(self.entries['market_share'].get()),
                'economic_stability': float(self.entries['economic_stability'].get()),
                'tax_rate': float(self.entries['tax_rate'].get())
            }

            efficiency = self.fuzzy_system.evaluate(inputs)
            messagebox.showinfo(
                "Результат",
                f"Оценка эффективности: {efficiency:.2f}\n\n" +
                "\n".join(RecommendationEngine.generate_recommendations(pd.DataFrame([inputs])))
            )
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")

    def _load_data(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.data = pd.read_csv(filename)
            self._update_plots()
            self.status_var.set(f"Данные загружены из {filename}")

    def _save_to_db(self):
        if not self.data.empty:
            self.db_manager.save_results(self.data)
            self.status_var.set("Данные сохранены в базу данных")
        else:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")

    def _load_from_db(self):
        self.data = self.db_manager.load_recent_results()
        if not self.data.empty:
            self._update_plots()
            self.status_var.set("Данные загружены из базы данных")
        else:
            messagebox.showinfo("Информация", "В базе данных нет записей")

    def _export_report(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write("Отчет по эффективности предприятия\n")
                f.write("=" * 50 + "\n\n")
                f.write(self.data.describe().to_string())
                f.write("\n\nРекомендации:\n")
                f.write("\n".join(RecommendationEngine.generate_recommendations(self.data)))

            self.status_var.set(f"Отчет сохранен в {filename}")

    def _show_analysis(self):
        if self.data.empty:
            self.data = DataAnalyzer.generate_test_data()

        self._update_plots()

    def _show_trends(self):
        if not self.data.empty:
            trends = TrendAnalyzer.analyze_trends(self.data)
            message = "\n".join([f"{k}: {'↑ рост' if v > 0 else '↓ снижение'} ({v:.2f})"
                                 for k, v in trends.items()])
            messagebox.showinfo("Анализ тенденций", message)
        else:
            messagebox.showwarning("Предупреждение", "Нет данных для анализа")

    def _show_recommendations(self):
        if not self.data.empty:
            recommendations = RecommendationEngine.generate_recommendations(self.data)
            messagebox.showinfo("Рекомендации", "\n".join(recommendations))
        else:
            messagebox.showwarning("Предупреждение", "Нет данных для анализа")

    def _update_plots(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self.data.empty:
            for column in self.data.columns[1:]:
                if column != 'month':
                    ax.plot(self.data['month'], self.data[column], label=column)

            ax.set_xlabel('Месяц')
            ax.set_ylabel('Значение')
            ax.legend()
            ax.grid(True)

        self.plot_canvas.draw()