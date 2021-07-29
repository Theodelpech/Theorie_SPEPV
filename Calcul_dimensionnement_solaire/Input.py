import tkinter as tk
class input(object):
    def __init__(self,Titre, demande):
        self.Titre = "Titre de la boîte de message"
        self.demande = "Question de la boîte à message"
    def message(self):
        window = tk.Tk()
        window.title(self.Titre)
        htLabel = tk.Label(window, text=self.demande)
        htLabel.pack() 
        ht = tk.IntVar()
        ht.set
        saisieHT = tk.Entry(window, textvariable=ht, width = 10)
        saisieHT.pack()
        bouton1 = tk.Button(window, text="Ok", width = 8, command=window.quit)
        bouton1.pack()
        window.mainloop()
        return ht 