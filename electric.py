#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

# Словарь цветов с RGB-значениями
colors = {
    "черный": {"digit": 0, "multiplier": 10**0, "tolerance": None, "rgb": (0, 0, 0)},
    "коричневый": {"digit": 1, "multiplier": 10**1, "tolerance": "±1%", "rgb": (139, 69, 19)},
    "красный": {"digit": 2, "multiplier": 10**2, "tolerance": "±2%", "rgb": (255, 0, 0)},
    "оранжевый": {"digit": 3, "multiplier": 10**3, "tolerance": None, "rgb": (255, 165, 0)},
    "желтый": {"digit": 4, "multiplier": 10**4, "tolerance": None, "rgb": (255, 255, 0)},
    "зеленый": {"digit": 5, "multiplier": 10**5, "tolerance": "±0.5%", "rgb": (0, 128, 0)},
    "синий": {"digit": 6, "multiplier": 10**6, "tolerance": "±0.25%", "rgb": (0, 0, 255)},
    "фиолетовый": {"digit": 7, "multiplier": 10**7, "tolerance": "±0.1%", "rgb": (128, 0, 128)},
    "серый": {"digit": 8, "multiplier": 10**8, "tolerance": "±0.05%", "rgb": (128, 128, 128)},
    "белый": {"digit": 9, "multiplier": 10**9, "tolerance": None, "rgb": (255, 255, 255)},
    "золотой": {"digit": None, "multiplier": 10**-1, "tolerance": "±5%", "rgb": (255, 215, 0)},
    "серебряный": {"digit": None, "multiplier": 10**-2, "tolerance": "±10%", "rgb": (192, 192, 192)},
    "нет": {"digit": None, "multiplier": None, "tolerance": None, "rgb": (0.8, 0.8, 0.8)}
}

color_list = list(colors.keys())

def calculate_resistor_value(bands):
    try:
        if len(bands) == 5 and bands[4] == "нет":
            bands = bands[:4]
        if len(bands) == 4:
            digit1 = colors[bands[0]]["digit"]
            digit2 = colors[bands[1]]["digit"]
            multiplier = colors[bands[2]]["multiplier"]
            tolerance = colors[bands[3]]["tolerance"]
            if digit1 is None or digit2 is None:
                return "Ошибка: первые две полоски не могут быть золотыми или серебряными."
            value = (digit1 * 10 + digit2) * multiplier
        elif len(bands) == 5:
            digit1 = colors[bands[0]]["digit"]
            digit2 = colors[bands[1]]["digit"]
            digit3 = colors[bands[2]]["digit"]
            multiplier = colors[bands[3]]["multiplier"]
            tolerance = colors[bands[4]]["tolerance"]
            if digit1 is None or digit2 is None or digit3 is None:
                return "Ошибка: первые три полоски не могут быть золотыми или серебряными."
            value = (digit1 * 100 + digit2 * 10 + digit3) * multiplier
        else:
            return "Ошибка: поддерживаются только 4 или 5 полосок."
        
        if value >= 10**6:
            value_str = f"{value / 10**6:.2f} МОм"
        elif value >= 10**3:
            value_str = f"{value / 10**3:.2f} кОм"
        else:
            value_str = f"{value:.2f} Ом"
        tolerance_str = tolerance if tolerance else "нет данных о допуске"
        return f"Номинал: {value_str}, допуск: {tolerance_str}"
    except KeyError:
        return "Ошибка: неверный цвет."

def get_colors_from_value(value):
    if not isinstance(value, (int, float)) or value <= 0:
        return None, "Ошибка: введите положительное число."
    
    multiplier = 0
    temp_value = value
    while temp_value >= 100:
        temp_value /= 10
        multiplier += 1
    while temp_value < 10:
        temp_value *= 10
        multiplier -= 1
    
    if 10 <= temp_value < 100:
        digit1 = int(temp_value // 10)
        digit2 = int(temp_value % 10)
        band1 = next(c for c, v in colors.items() if v["digit"] == digit1)
        band2 = next(c for c, v in colors.items() if v["digit"] == digit2)
        band3 = next(c for c, v in colors.items() if v["multiplier"] == 10**multiplier)
        band4 = "золотой"
        band5 = "нет"
        return [band1, band2, band3, band4, band5], None
    
    multiplier = 0
    temp_value = value
    while temp_value >= 1000:
        temp_value /= 10
        multiplier += 1
    while temp_value < 100:
        temp_value *= 10
        multiplier -= 1
    
    if 100 <= temp_value < 1000:
        digit1 = int(temp_value // 100)
        digit2 = int((temp_value // 10) % 10)
        digit3 = int(temp_value % 10)
        band1 = next(c for c, v in colors.items() if v["digit"] == digit1)
        band2 = next(c for c, v in colors.items() if v["digit"] == digit2)
        band3 = next(c for c, v in colors.items() if v["digit"] == digit3)
        band4 = next(c for c, v in colors.items() if v["multiplier"] == 10**multiplier)
        band5 = "золотой"
        return [band1, band2, band3, band4, band5], None
    
    return None, "Ошибка: невозможно представить значение с 4 или 5 полосками."

def calculate_smd_value(code):
    code = code.strip().upper()
    if "R" in code:
        try:
            value = float(code.replace("R", "."))
            if value >= 10**6:
                return f"{value / 10**6:.2f} МОм"
            elif value >= 10**3:
                return f"{value / 10**3:.2f} кОм"
            else:
                return f"{value:.2f} Ом"
        except ValueError:
            return "Ошибка: неверный формат кода с R."
    if len(code) == 3 and code.isdigit():
        try:
            digits = int(code[:2])
            multiplier = 10 ** int(code[2])
            value = digits * multiplier
            if value >= 10**6:
                return f"{value / 10**6:.2f} МОм"
            elif value >= 10**3:
                return f"{value / 10**3:.2f} кОм"
            else:
                return f"{value:.2f} Ом"
        except ValueError:
            return "Ошибка: неверный трёхзначный код."
    if len(code) == 4 and code.isdigit():
        try:
            digits = int(code[:3])
            multiplier = 10 ** int(code[3])
            value = digits * multiplier
            if value >= 10**6:
                return f"{value / 10**6:.2f} МОм"
            elif value >= 10**3:
                return f"{value / 10**3:.2f} кОм"
            else:
                return f"{value:.2f} Ом"
        except ValueError:
            return "Ошибка: неверный четырёхзначный код."
    return "Ошибка: неверный формат кода (примеры: 103, 1002, 4R7)."

class ResistorApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.Electric") 
        self.combo_boxes = []
        self.color_rows = []
        self.selected_colors = [color_list[0]] * 5

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Калькулятор резисторов")
        window.set_default_size(400, 550)
       
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        window.set_child(box)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(350, 100)
        box.append(self.drawing_area)
        self.drawing_area.set_draw_func(self.draw_resistor, None)

        value_label = Gtk.Label(label="Введите номинал (Ом):")
        value_label.set_halign(Gtk.Align.START)
        self.value_entry = Gtk.Entry()
        self.value_entry.set_placeholder_text("Например, 220 или 1200")
        self.value_entry.connect("activate", self.on_value_entered)
        box.append(value_label)
        box.append(self.value_entry)

        self.color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.append(self.color_box)

        self.result_label = Gtk.Label(label="Выберите цвета или введите номинал")
        self.result_label.set_halign(Gtk.Align.START)
        self.result_label.set_max_width_chars(40)  # Ограничиваем ширину
        self.result_label.set_ellipsize(gi.repository.Pango.EllipsizeMode.END)  # Обрезка текста с точками
        box.append(self.result_label)

        calc_button = Gtk.Button(label="Рассчитать")
        calc_button.connect("clicked", self.on_calculate_clicked)
        box.append(calc_button)

        smd_label = Gtk.Label(label="SMD-резистор (введите код):")
        smd_label.set_halign(Gtk.Align.START)
        self.smd_entry = Gtk.Entry()
        self.smd_entry.set_placeholder_text("Например, 103, 1002, 4R7")
        self.smd_entry.connect("activate", self.on_smd_entered)
        self.smd_result_label = Gtk.Label(label="Номинал SMD: -")
        self.smd_result_label.set_halign(Gtk.Align.START)
        self.smd_result_label.set_max_width_chars(40)  # Ограничиваем ширину
        self.smd_result_label.set_ellipsize(gi.repository.Pango.EllipsizeMode.END)  # Обрезка текста с точками
        box.append(smd_label)
        box.append(self.smd_entry)
        box.append(self.smd_result_label)

        self.update_color_inputs()
        window.present()

    def draw_resistor(self, area, cr, width, height, data):
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(50, 20, width - 100, height - 40)
        cr.fill()

        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(0, height / 2 - 5, 50, 10)
        cr.rectangle(width - 50, height / 2 - 5, 50, 10)
        cr.fill()

        band_width = 20
        spacing = 10
        start_x = 70
        bands_to_draw = 4 if self.selected_colors[4] == "нет" else 5
        for i in range(4):
            color_name = self.selected_colors[i]
            rgb = colors[color_name]["rgb"]
            cr.set_source_rgb(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
            cr.rectangle(start_x + i * (band_width + spacing), 20, band_width, height - 40)
            cr.fill()
        
        if bands_to_draw == 5:
            color_name = self.selected_colors[4]
            rgb = colors[color_name]["rgb"]
            cr.set_source_rgb(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
            cr.rectangle(start_x + 4 * (band_width + spacing) + 30, 20, band_width, height - 40)
            cr.fill()

    def update_color_inputs(self):
        for row in self.color_rows:
            self.color_box.remove(row)
        self.combo_boxes.clear()
        self.color_rows.clear()

        for i in range(5):
            label = Gtk.Label(label=f"Полоска {i+1}:")
            label.set_halign(Gtk.Align.START)
            combo = Gtk.ComboBoxText()
            for color in color_list:
                combo.append_text(color)
            combo.set_active(color_list.index(self.selected_colors[i]))
            combo.connect("changed", self.on_color_changed, i)
            self.combo_boxes.append(combo)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.append(label)
            hbox.append(combo)
            self.color_box.append(hbox)
            self.color_rows.append(hbox)
        
        self.color_box.show()

    def on_color_changed(self, combo, index):
        self.selected_colors[index] = combo.get_active_text()
        self.drawing_area.queue_draw()
        self.result_label.set_text("Нажмите 'Рассчитать' для проверки")

    def on_calculate_clicked(self, button):
        result = calculate_resistor_value(self.selected_colors)
        self.result_label.set_text(result)

    def on_value_entered(self, entry):
        try:
            value = float(entry.get_text())
            new_colors, error = get_colors_from_value(value)
            if error:
                self.result_label.set_text(error)
            else:
                self.selected_colors = new_colors
                self.update_color_inputs()
                self.drawing_area.queue_draw()
                self.result_label.set_text(calculate_resistor_value(self.selected_colors))
        except ValueError:
            self.result_label.set_text("Ошибка: введите число (например, 220 или 1200)")

    def on_smd_entered(self, entry):
        code = entry.get_text()
        result = calculate_smd_value(code)
        self.smd_result_label.set_text(f"Номинал SMD: {result}")

def main():
    app = ResistorApp()
    app.run()

if __name__ == "__main__":
    main()
