import tkinter as tk
from tkinter import filedialog

# Скрываем основное окно tkinter
root = tk.Tk()
root.withdraw()

# Открываем диалоговое окно для выбора файла
file_path = filedialog.askopenfilename(filetypes=(("Jpg Files", "*.jpg"), ("Png Files", "*.png"), ('Jpeg Files', '*.jpeg'), ("All Files", "*.*")))

if file_path:
    print(f"Выбранный файл: {file_path}")
else:
    print("Файл не выбран")