import tkinter as tk
class input_bool(object):
    def __init__(self,Titre, demande):
        self.Titre = Titre
        self.demande = demande
    def message_bool(self):
        window = tk.Tk()
        window.title(self.Titre)
        window.geometry("800x100")
        htLabel = tk.Label(window, text=self.demande)
        htLabel.pack() 
        bo = tk.StringVar()
        bo.set
        saisieBO = tk.Entry(window, textvariable=bo, width = 20)
        saisieBO.pack()
        bouton1 = tk.Button(window, text="Ok", width = 20, command=window.quit)
        bouton1.pack()
        window.mainloop()
        return bo 