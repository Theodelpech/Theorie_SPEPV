import tkinter as tk
class input(object):
    def __init__(self,Titre, demande):
        self.Titre = Titre
        self.demande = demande
    
    def message(self):
        window = tk.Tk()
        window.title(self.Titre)
        window.geometry("500x100")
        htLabel = tk.Label(window, text=self.demande)
        htLabel.pack() 
        ht = tk.DoubleVar()
        ht.set(ht)
        saisieHT = tk.Entry(window, textvariable=ht, width = 15)
        saisieHT.pack()
        bouton1 = tk.Button(window, text="Ok", width = 10, command=window.destroy)
        bouton1.pack()
        window.mainloop()
        return ht
   
