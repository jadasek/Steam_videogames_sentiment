import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import webbrowser
import tkinter.messagebox


class App:
    def __init__(self, master):
        self.master = master
        self.step = 1
        self.game_name = ""
        self.game_id = 0
        self.review_num = 0
        self.tags = ""
        self.summarize = False
        self.sentiment = False
        self.create_step1()

    def create_step1(self):
        self.step1_frame = ttk.Frame(self.master)
        self.step1_frame.pack()
        ttk.Label(self.step1_frame, text="Krok 1: Wprowadź nazwę gry z platformy Steam").pack()
        self.entry1 = ttk.Entry(self.step1_frame)
        self.entry1.insert(0, self.game_name)
        self.entry1.pack()
        ttk.Button(self.step1_frame, text="Wyszukaj", command=self.search).pack()
        ttk.Button(self.step1_frame, text="Otwórz nowe okno", command=self.open_new_window).pack(pady=10)
        self.listbox = tk.Listbox(self.step1_frame, height=0, width=0)
        self.listbox.pack()
        self.listbox.bind("<Double-Button-1>", self.open_link)
        ttk.Separator(self.step1_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.step1_frame, text="Wpisz nazwę gry, a program spróbuje znaleźć ją w sklepie Steam. Następnie wybierz ze zwróconych wartości te grę, której szukasz. Możesz kliknąć dwukrotnie na rekord, a zostaniesz przeniesiony na stronę produktu.").pack()
        ttk.Label(self.step1_frame, text="Jeżeli gra nie wyświetla się na liście kliknij przycisk 'Gra nie wyświetla się na liście'").pack()
        ttk.Button(self.step1_frame, text="Dalej", command=self.next_step).pack()

    def open_new_window(self):
        # Tworzenie nowego okna
        new_window = tk.Toplevel(self.master)

        ttk.Label(new_window, text="Wprowadź id gry:").pack()
        # Dodanie pola do wprowadzenia wartości
        value_entry = ttk.Entry(new_window)
        value_entry.pack()
        
        # Dodanie przycisku do zamknięcia okna i przejścia do następnego kroku
        ttk.Button(new_window, text="Zamknij i przejdź dalej", command=lambda: self.close_new_window(new_window)).pack()
        ttk.Button(new_window, text="Anuluj", command=new_window.destroy).pack()

    def close_new_window(self, new_window):
        # Pobranie wartości z pola Entry w nowym oknie
        value = new_window.winfo_children()[1].get()
        
        self.new_window_value = value
        self.game_id = int(value)
        # Zamknięcie nowego okna
        new_window.destroy()
        
        # Przejście do następnego kroku
        self.next_step()

    def search(self):
        # Clear the Listbox
        self.listbox.delete(0, tk.END)

        # Run the Python code in a separate file and display the results in the Listbox
        import subprocess
        game_name = self.entry1.get()
        result = subprocess.check_output(["python", r"C:\Users\tymot\Desktop\import requests.py", game_name])
        result = result.decode("utf-8").strip().split("\n")
        for item in result:
            self.listbox.insert(tk.END, item)

    def open_link(self, event):
        selection = self.listbox.curselection()
        if selection:
            link = self.listbox.get(selection[0]).split()[-1]
            if link.startswith("http"):
                webbrowser.open(link)

    def create_step2(self):
        self.step2_frame = ttk.Frame(self.master)
        self.step2_frame.pack()
        ttk.Label(self.step2_frame, text="Krok 2: Wprowadź liczbę z zakresu od 1 do liczby recenzji jakie są dostępne dla gry podanej w kroku 1").pack()
        self.entry2 = ttk.Spinbox(self.step2_frame, from_=1, to=100) # zakładając, że maksymalna liczba recenzji to 100
        if self.review_num != 0:
            self.entry2.delete(0, "end")
            self.entry2.insert(0, str(self.review_num)) # ustawienie wartości pola Entry na podstawie zmiennej przechowującej informację wprowadzoną przez użytkownika
        self.entry2.pack()
        ttk.Button(self.step2_frame, text="Dalej", command=self.next_step).pack()
        ttk.Button(self.step2_frame, text="Cofnij", command=self.prev_step).pack()

    def create_step3(self):
        self.step3_frame = ttk.Frame(self.master)
        self.step3_frame.pack()
        ttk.Label(self.step3_frame, text="Krok 3: Wprowadź tagi jakie potem będą wyszukiwane w tekście przy użyciu one-hot encodingu").pack()
        self.entry3 = ttk.Entry(self.step3_frame)
        self.entry3.insert(0, self.tags) # ustawienie wartości pola Entry na podstawie zmiennej przechowującej informację wprowadzoną przez użytkownika
        self.entry3.pack()
        ttk.Button(self.step3_frame, text="Dalej", command=self.next_step).pack()
        ttk.Button(self.step3_frame, text="Cofnij", command=self.prev_step).pack()

    def create_step4(self):
        self.step4_frame = ttk.Frame(self.master)
        self.step4_frame.pack()
        ttk.Label(self.step4_frame, text="Wybierz opcje:").pack()
        self.summarize_var = tk.BooleanVar()
        self.sentiment_var = tk.BooleanVar()
        ttk.Checkbutton(self.step4_frame, text="Użyj streszczania", variable=self.summarize_var).pack()
        ttk.Checkbutton(self.step4_frame, text="Sprawdź sentyment", variable=self.sentiment_var).pack()
        ttk.Button(self.step4_frame, text="Dalej", command=self.next_step).pack()
        ttk.Button(self.step4_frame, text="Cofnij", command=self.prev_step).pack()

    def next_step(self):
        if self.step == 1:
            # Sprawdzenie, czy użytkownik wprowadził wartość w nowym oknie
            if not hasattr(self, 'new_window_value'):
                self.game_name = self.entry1.get()
                self.selection = self.listbox.curselection()
                if not self.game_name:
                    tk.messagebox.showerror("Błąd", "Musisz wprowadzić nazwę gry")
                    return
                if not self.selection:
                    tk.messagebox.showerror("Błąd", "Musisz wybrać grę z listy")
                    return
            print(self.listbox.get(self.selection[0])) #Wartość jaką użytkownik wybrał w liście z kroku 1
            print(self.game_id) #Wartość jaką użytkownik wybrał w liście z kroku 1
            self.step1_frame.pack_forget()
            self.create_step2()
            self.step += 1
        elif self.step == 2:
            try:
                review_num = int(self.entry2.get())
                if review_num < 1 or review_num > 100: # zakładając, że maksymalna liczba recenzji to 100
                    raise ValueError
                else:
                    self.review_num = review_num
            except ValueError:
                tk.messagebox.showerror("Błąd", "Musisz wprowadzić poprawną liczbę recenzji")
                return
            self.step2_frame.pack_forget()
            self.create_step3()
            self.step += 1
        elif self.step == 3:
            tags = self.entry3.get()
            if not tags:
                tk.messagebox.showerror("Błąd", "Musisz wprowadzić tagi")
                return
            else:
                self.tags = tags
            self.step3_frame.pack_forget()
            self.create_step4()
            self.step += 1
        elif self.step == 4:
            self.summarize = self.summarize_var.get()
            self.sentiment = self.sentiment_var.get()
            # Tutaj możesz dodać kod, który będzie wykonywany na podstawie wprowadzonych informacji i wybranych opcji
            print(f"Nazwa gry: {self.game_name}")
            print(f"Liczba recenzji: {self.review_num}")
            print(f"Tagi: {self.tags}")
            print(f"Użyj streszczania: {self.summarize}")
            print(f"Sprawdź sentyment: {self.sentiment}")

    def prev_step(self):
        if self.step == 2:
            self.step2_frame.pack_forget()
            self.create_step1()
            self.step -= 1
        elif self.step == 3:
            self.step3_frame.pack_forget()
            self.create_step2()
            self.step -= 1
        elif self.step == 4:
            self.step4_frame.pack_forget()
            self.create_step3()
            self.step -= 1

root = tk.Tk()
style = Style(theme="darkly")
app = App(root)
root.mainloop()
