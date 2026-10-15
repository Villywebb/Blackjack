import tkinter as tk

fonster = tk.Tk()
fonster.title("Spelkort")

kort = tk.Label(fonster, text="🂡 🂱 🃁 🃑", font=("Arial",1000))
kort.pack(padx=20, pady=20)

fonster.mainloop()