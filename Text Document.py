import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import platform

root = tk.Tk()
root.title('ne')
root.geometry('1200x600')
root.resizable(False, False)

root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(1, weight=0)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(0, weight=1)
frame1 = tk.Frame(root, bg='white', relief='solid', borderwidth=1)
frame2 = tk.Frame(root, bg='white', relief='solid', borderwidth=1)
frame3 = tk.Frame(root, bg='white', relief='solid', borderwidth=1)
frame1.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
frame2.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
frame3.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

pil_image = Image.open(r"C:\Users\Data-14\Desktop\itb-101-Hnikov-Shperling\server_imgs\0.jpg")
resized_image = pil_image.resize((400, 500), Image.Resampling.LANCZOS)
img = ImageTk.PhotoImage(resized_image)
image_label = tk.Label(frame1, image=img)
image_label.pack()
image_label.image = img
method_lbl = tk.Label(
    frame1,
    text='Олег',
    bg='white',
    font=('Helvetica', 10),
    height=1
)
method_lbl.pack(padx=5, pady=5, expand=False)
method_lbl = tk.Label(
   frame1,
    text='Username',
    bg='white',
    font=('Helvetica', 10),
    height=1
)
method_lbl.pack(padx=5, pady=3)
method_lbl = tk.Label(
   frame1,
    text='Post',
    bg='white',
    font=('Helvetica', 10),
    height=1
)
method_lbl.pack(padx=5, pady=5)
desc = scrolledtext.ScrolledText(frame2, width=40, height=33)
desc.grid(column=1, row=1)
btn = tk.Button(
    frame2,
    text='Изменить описание',
    font=('Helvetica', 16),
    command=''
)
btn.grid(row=2, column=1)
import tkinter as tk

frame3.grid_rowconfigure(1, weight=1) # Делаем ряд с холстом растягиваемым
frame3.grid_columnconfigure(0, weight=1) # Делаем колонку с холстом растягиваемой


label_title = tk.Label(frame3, text='Бумаги', font=('Arial', 14, 'bold'), bg='white')
label_title.grid(row=0, column=0, columnspan=2, pady=5)

canvas = tk.Canvas(frame3, bg='white')
scrollbar = tk.Scrollbar(frame3, orient='vertical', command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg='white')

def on_frame_configure(e):
    canvas.configure(scrollregion=canvas.bbox('all'))

scrollable_frame.bind('Configure', on_frame_configure)

canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
canvas.configure(yscrollcommand=scrollbar.set)


canvas.grid(row=1, column=0, sticky='nsew')
scrollbar.grid(row=1, column=1, sticky='ns')

def on_mousewheel(event):
    if platform.system() == 'Windows':
        canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
    elif platform.system() == 'Darwin':
        canvas.yview_scroll(int(-1 * event.delta), 'units')
    else:
        if event.num == 4:
            canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            canvas.yview_scroll(1, 'units')

root.bind_all('MouseWheel', on_mousewheel)
root.bind_all('Button-4', on_mousewheel)
root.bind_all('Button-5', on_mousewheel)

for i in range(30):
    tk.Button(
        scrollable_frame,
        text=f'Кнопка {i}',
        width=53,
        height=2
    ).pack(pady=5, padx=10, fill='x')
# миша замени это говно сверху👍

root.mainloop()
