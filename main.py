import tkinter as tk

def on_click():
    label.config(text="Você clicou no botão!")

window = tk.Tk()
window.title("Exemplo com Tkinter")
window.geometry("500x500")

label = tk.Label(window, text="Hello, Tkinter!")
label.pack(pady=10)

button = tk.Button(window, text="Clique aqui", command=on_click)
button.pack(pady=10)

window.mainloop()
