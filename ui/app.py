import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import os
import subprocess

from models import Loads
from services.mechanics import calculate_reactions, calculate_moments, calculate_min_diameter
from services.bearings import select_bearing


class ShaftWizardApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="catppuccin-dark", title="ShaftWizard - Инженерный расчет", size=(1100, 800))
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk.Label(main_frame, text="Расчет вала редуктора", font=("TkDefaultFont", 18, "bold")).pack(pady=(0, 10))

        # ================= ИСХОДНЫЕ ДАННЫЕ =================
        input_frame = ttk.Labelframe(main_frame, text="1. Нагрузки", bootstyle="info", padding=10)
        input_frame.pack(fill=X, pady=5)

        self.entries = {}
        fields = [
            ("F_t (Окружная сила, Н)", "0", 0, 0),
            ("F_r (Радиальная сила, Н)", "0", 0, 1),
            ("T (Момент, Н*мм)", "0", 0, 2),
            ("L (Между опорами, мм)", "0", 1, 0),
            ("a (Плечо слева, мм)", "0", 1, 1),
            ("b (Плечо справа, мм)", "0", 1, 2),
        ]

        for label, default, row, col in fields:
            ttk.Label(input_frame, text=label).grid(row=row * 2, column=col, sticky=W, padx=5, pady=(2, 0))
            entry = ttk.Entry(input_frame, width=15)
            entry.insert(0, default)
            entry.grid(row=row * 2 + 1, column=col, padx=5, pady=(0, 5))
            self.entries[label] = entry

        # ================= ГЕОМЕТРИЯ ВАЛА =================
        geom_frame = ttk.Labelframe(main_frame, text="2. Геометрия вала (Ступени)", bootstyle="warning", padding=10)
        geom_frame.pack(fill=X, pady=5)

        self.steps_tree = ttk.Treeview(geom_frame, columns=("d", "l"), show="headings", height=4)
        self.steps_tree.heading("d", text="Диаметр, мм")
        self.steps_tree.heading("l", text="Длина, мм")
        self.steps_tree.column("d", width=100, anchor=CENTER)
        self.steps_tree.column("l", width=100, anchor=CENTER)
        self.steps_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        btn_geom_frame = ttk.Frame(geom_frame)
        btn_geom_frame.pack(side=RIGHT, fill=Y, padx=5)
        ttk.Button(btn_geom_frame, text="+ Добавить", bootstyle="success", command=self._add_step_dialog).pack(fill=X, pady=2)
        ttk.Button(btn_geom_frame, text="- Удалить", bootstyle="danger", command=self._remove_step).pack(fill=X, pady=2)

        # ================= КНОПКИ ДЕЙСТВИЙ =================
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=X, pady=10)

        ttk.Button(action_frame, text="🚀 РАССЧИТАТЬ", bootstyle="success", command=self._calculate).pack(side=LEFT, padx=5)
        ttk.Button(action_frame, text="Сбросить", bootstyle="secondary", command=self._reset).pack(side=LEFT, padx=5)

        ttk.Label(action_frame, text="Имя файла:").pack(side=RIGHT, padx=(20, 5))
        self.filename_entry = ttk.Entry(action_frame, width=20)
        self.filename_entry.insert(0, "shaft_model")
        self.filename_entry.pack(side=RIGHT, padx=5)
        ttk.Button(action_frame, text="⚙️ Сгенерировать 3D", bootstyle="info", command=self._generate_3d).pack(side=RIGHT, padx=5)

        # ================= РЕЗУЛЬТАТЫ =================
        self.result_frame = ttk.Labelframe(main_frame, text="Результаты", bootstyle="primary", padding=10)
        self.result_frame.pack(fill=BOTH, expand=True, pady=5)
        self.output_text = tk.Text(self.result_frame, height=8, bg="#1e1e2e", fg="#cdd6f4", font=("Consolas", 10), borderwidth=0)
        self.output_text.pack(fill=BOTH, expand=True)

    def _add_step_dialog(self):
        dialog = ttk.Toplevel(self)
        dialog.title("Добавить ступень")
        dialog.geometry("350x280")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Контейнер с отступами
        frm = ttk.Frame(dialog, padding=20)
        frm.pack(fill=BOTH, expand=True)

        # Поле Диаметр
        ttk.Label(frm, text="Диаметр (мм):", font=("TkDefaultFont", 10)).pack(anchor=W, pady=(0, 5))
        d_entry = ttk.Entry(frm, width=20)
        d_entry.pack(fill=X, pady=(0, 15))

        # Поле Длина
        ttk.Label(frm, text="Длина (мм):", font=("TkDefaultFont", 10)).pack(anchor=W, pady=(0, 5))
        l_entry = ttk.Entry(frm, width=20)
        l_entry.pack(fill=X, pady=(0, 20))

        def save_step():
            try:
                d = float(d_entry.get())
                l = float(l_entry.get())
                self.steps_tree.insert("", "end", values=(d, l))
                dialog.destroy()
            except ValueError:
                Messagebox.show_error("Введите числа!", title="Ошибка")

        # Кнопка Добавить (на всю ширину)
        ttk.Button(frm, text="Добавить", bootstyle="success", command=save_step).pack(fill=X, pady=(5, 0))

    def _remove_step(self):
        for item in self.steps_tree.selection():
            self.steps_tree.delete(item)

    def _calculate(self):
        try:
            F_t = float(self.entries["F_t (Окружная сила, Н)"].get())
            F_r = float(self.entries["F_r (Радиальная сила, Н)"].get())
            T = float(self.entries["T (Момент, Н*мм)"].get())
            L = float(self.entries["L (Между опорами, мм)"].get())
            a = float(self.entries["a (Плечо слева, мм)"].get())
            b = float(self.entries["b (Плечо справа, мм)"].get())

            loads = Loads(F_t=F_t, F_r=F_r, T=T, L=L, a=a, b=b)
            reactions = calculate_reactions(loads)
            moments = calculate_moments(loads)
            d_min = calculate_min_diameter(moments["M_eq"])
            bearing = select_bearing(reactions["R_A"], n=300, L_h=10000, d_required=30.0)

            self.output_text.delete("1.0", END)
            result_str = f"""
=== РЕАКЦИИ ОПОР ===
R_A = {reactions['R_A']:.2f} Н
R_B = {reactions['R_B']:.2f} Н

=== МОМЕНТЫ ===
M_сум = {moments['M_sum']:.2f} Н*мм
M_экв = {moments['M_eq']:.2f} Н*мм

=== ПРОЧНОСТЬ ===
Мин. диаметр: {d_min:.2f} мм

=== ПОДШИПНИК ===
Подобран: {bearing.designation} (C = {bearing.C} Н)
            """
            self.output_text.insert("1.0", result_str)
        except ValueError as e:
            self.output_text.insert("1.0", f"Ошибка ввода: {e}")

    def _reset(self):
        for entry in self.entries.values():
            entry.delete(0, END)
            entry.insert(0, "0")
        self.output_text.delete("1.0", END)

    def _generate_3d(self):
        # 1. Считываем ступени из таблицы
        steps = []
        for child in self.steps_tree.get_children():
            values = self.steps_tree.item(child)["values"]
            steps.append((float(values[0]), float(values[1])))

        if not steps:
            Messagebox.show_warning("Сначала добавьте ступени!", title="Ошибка")
            return

        # 2. Получаем имя файла
        filename = self.filename_entry.get().strip()
        if not filename:
            filename = "shaft_model"
        filename_fcstd = f"{filename}.FCStd"

        # 3. Создаем скрипт для FreeCAD
        script_content = f"""
import sys
sys.path.append(r'{os.getcwd()}')
from freecad_generator import build_shaft

steps = {steps}
build_shaft(steps, "{filename_fcstd}")
"""
        with open("temp_gen.py", "w") as f:
            f.write(script_content)

        self.output_text.insert("end", f"\n\n⏳ Генерация {filename_fcstd}...")

        # 4. Запускаем freecadcmd
        try:
            subprocess.run(["freecadcmd", "temp_gen.py"], check=True, capture_output=True)
            self.output_text.insert("end", f"\n✅ Успешно! Файл {filename_fcstd} создан.")
        except FileNotFoundError:
            self.output_text.insert("end", "\n❌ Ошибка: freecadcmd не найден.")
        except subprocess.CalledProcessError as e:
            self.output_text.insert("end", f"\n❌ Ошибка FreeCAD: {e.stderr.decode()}")

if __name__ == "__main__":
    app = ShaftWizardApp()
    app.mainloop()