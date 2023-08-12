import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import webbrowser
import tkinter.messagebox
import subprocess

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if value in val:
            return key
    return None

class App:
    def __init__(self, master):
        self.languages_codes = {'angielski': ('en', 'english'), 'arabski': ('ar', 'arabic'), 'bułgarski': ('bg', 'bulgarian'), 'chiński uproszczony': ('zh-CN', 'schinese'), 'chiński tradycyjny': ('zh-TW', 'tchinese'), 'czeski': ('cs', 'czech'),'duński': ('da', 'danish'),'niderlandzki': ('nl', 'dutch'),'fiński': ('fi', 'finnish'),'francuski': ('fr', 'french'),'niemiecki': ('de', 'german'),'grecki': ('el', 'greek'),'węgierski': ('hu', 'hungarian'),'włoski': ('it', 'italian'),'japoński': ('ja', 'japanese'),'koreański': ('ko', 'koreana'),'norweski': ('no', 'norwegian'),'polski': ('pl', 'polish'),'portugalski': ('pt', 'portuguese'),'portugalski brazylijski': ('pt-BR', 'brazilian'),'rumuński': ('ro', 'romanian'),'rosyjski': ('ru', 'russian'),'hiszpański': ('es', 'spanish'),'hiszpański latynoamerykański': ('es-419', 'latam'),'szwedzki': ('sv', 'swedish'),'tajski': ('th', 'thai'),'turecki': ('tr', 'turkish'),'ukraiński': ('uk', 'ukrainian'),'wietnamski': ('vn','vietnamese')}

        self.master = master
        self.step = 1
        self.game_name = ""
        self.game_id = 0
        self.review_num = 0
        self.selected_languages = []
        self.tags = ""
        self.summarize = False
        self.sentiment = False
        self.create_step1()

    def create_step1(self):
        self.step1_frame = ttk.Frame(self.master)
        self.step1_frame.pack()
        self.step1_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step1_frame, text="Krok 1: Wprowadź nazwę gry z platformy Steam").pack()
        self.entry1 = ttk.Entry(self.step1_frame, width=98)
        self.entry1.insert(0, self.game_name)
        self.entry1.pack()
        ttk.Button(self.step1_frame, text="Wyszukaj", command=self.search).pack()
        ttk.Button(self.step1_frame, text="Gra nie wyświetla się na liście", command=self.open_new_window).pack(pady=10)

        # Create a Treeview widget to display the data in a table format
        self.treeview = ttk.Treeview(self.step1_frame, columns=("Nazwa gry", "ID gry", "Link do strony gry na Steam"), show="headings")
        self.treeview.column('Link do strony gry na Steam',width=400)
        self.treeview.column('ID gry',width=50)
        self.treeview.column('Nazwa gry',width=150)
        self.treeview.bind("<Double-Button-1>", self.open_link)
        self.treeview.heading("Nazwa gry", text="Nazwa gry")
        self.treeview.heading("ID gry", text="ID gry")
        self.treeview.heading("Link do strony gry na Steam", text="Link do strony gry na Steam")
        self.treeview.pack()

        ttk.Separator(self.step1_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.step1_frame, text="Wpisz nazwę gry, a program spróbuje znaleźć ją w sklepie Steam. Następnie wybierz ze zwróconych wartości te grę, której szukasz. Możesz kliknąć dwukrotnie na rekord, a zostaniesz przeniesiony na stronę produktu.").pack()
        ttk.Label(self.step1_frame, text="Jeżeli gra nie wyświetla się na liście kliknij przycisk 'Gra nie wyświetla się na liście'").pack()
        ttk.Button(self.step1_frame, text="Dalej", command=self.next_step).pack()


    def open_new_window(self):
        # Tworzenie nowego okna
        new_window = tk.Toplevel(self.master)
        new_window.grab_set()
        new_window.minsize(width=250, height=120)

        ttk.Label(new_window, text="Wprowadź id gry:").pack()
        # Dodanie pola do wprowadzenia wartości
        self.value_entry = ttk.Entry(new_window)
        self.value_entry.pack()
        
        # Dodanie przycisku do zamknięcia okna i przejścia do następnego kroku
        ttk.Button(new_window, text="Zamknij i przejdź dalej", command=lambda: self.close_new_window(new_window)).pack()
        ttk.Button(new_window, text="Anuluj", command=new_window.destroy).pack()

    def close_new_window(self, new_window):
        # Pobranie wartości z pola Entry w nowym oknie
        value = new_window.winfo_children()[1].get()
        if not value:
            tk.messagebox.showerror("Błąd", "Pole nie może być puste")
            return
        try:
            self.new_window_value = value
            self.game_id = int(value)
        except ValueError:
            tk.messagebox.showerror("Błąd", "Upewnij się, że wpisujesz tylko liczby")
            return
        # Zamknięcie nowego okna
        new_window.destroy()
        
        # Przejście do następnego kroku
        self.next_step()

    def search(self):
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        # Run the Python code in a separate file and display the results in the Listbox
        game_name = self.entry1.get()
        results = subprocess.check_output(["python", r"C:\Users\tymot\Desktop\Projekty\Twitter_videogames_sentiment\Modules\games_finder.py", game_name])
        results = results.decode("utf-8").strip().split("\n")
        for result in results:
            game_name, game_id, game_link = result.split(", ")
            game_name = game_name.split(": ")[1]
            game_id = game_id.split(": ")[1]
            game_link = game_link.split(": ")[1]
            self.treeview.insert("", "end", values=(game_name, game_id, game_link))

    def open_link(self, event):
        # Get the selected item in the Treeview widget
        selection = self.treeview.selection()
        if selection:
            # Get the game link from the selected item
            item = self.treeview.item(selection[0])
            game_link = item["values"][2]
            if game_link.startswith("http"):
                webbrowser.open(game_link)


    def create_step2(self):
        self.step2_frame = ttk.Frame(self.master)
        self.step2_frame.pack()
        self.step2_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step2_frame, text="Krok 2: Wybierz języki").grid(row=0, column=0, columnspan=3)
        options = self.languages_codes.keys()
        options = sorted(options)
        
        self.checkboxes = {}
        num_columns = 3
        num_rows = len(options)//num_columns+1
        for i, option in enumerate(options):
            self.checkboxes[option] = tk.BooleanVar()
            checkbutton = tk.Checkbutton(self.step2_frame, text=option, variable=self.checkboxes[option])
            checkbutton.grid(row=(i)%num_rows+1, column=(i)//num_rows, sticky="w")

        ttk.Button(self.step2_frame, text="Dalej", command=self.next_step).grid(row=len(options)//3+2, column=1)
        ttk.Button(self.step2_frame, text="Cofnij", command=self.prev_step).grid(row=len(options)//3+3, column=1)

    def create_step3(self):
        self.step3_frame = ttk.Frame(self.master)
        self.step3_frame.pack()
        self.step3_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        languages = ','.join([self.languages_codes[language][1] for language in self.selected_languages])
        results = subprocess.check_output(["python", r"C:\Users\tymot\Desktop\Projekty\Twitter_videogames_sentiment\Modules\review_counter.py", str(self.game_id), languages])
        results = results.decode("utf-8").strip().split("\n")
        keys = eval(results[0].strip())
        values = eval(str(results[1]))
        lang_num = dict(zip(keys, values))


        self.language_frames = []
        self.entries = {}
        self.current_language = 0
        for language, max_reviews in lang_num.items():
            custom_scale = tk.IntVar()
            custom_scale.set(0)
            frame = ttk.Frame(self.step3_frame)
            if max_reviews > 0:
                ttk.Label(frame, text=f"Dla języka {find_key_by_value(self.languages_codes, language)}:").grid(row=0,column=0, columnspan=4)
                tk.Scale(frame, from_=1, to=max_reviews, orient='horizontal', variable=custom_scale, length=400, resolution= 1).grid(row=1,column=1,columnspan=1,pady=10, padx=10)
                custom_entry = ttk.Entry(frame, textvariable=custom_scale)
                custom_entry.grid(row=1,column=3,columnspan=1,pady=10)
                custom_entry.insert(0, 100 if max_reviews > 100 else max_reviews)
                self.entries[language] = custom_entry
                self.language_frames.append(frame)
            else:
                ttk.Label(frame, text=f"Dla języka {find_key_by_value(self.languages_codes, language)} nie ma żadnych opinii").grid(row=0,column=0, columnspan=4)
                self.entries[language] = 0
                self.language_frames.append(frame)
        self.show_language_frame(self.current_language)

    def show_language_frame(self, index):
        for i, frame in enumerate(self.language_frames):
            if i == index:
                if len(self.language_frames) == 1:
                    ttk.Button(frame, text="Następny krok", command=self.next_step).grid(row=2,column=2,columnspan=1)
                    ttk.Button(frame, text="Wróć do poprzedniego kroku", command=self.prev_step).grid(row=2,column=1,columnspan=1)
                elif self.current_language == 0:
                    ttk.Button(frame, text="Następny język", command=self.next_language).grid(row=2,column=2,columnspan=1)
                    ttk.Button(frame, text="Wróć do poprzedniego kroku", command=self.prev_step).grid(row=2,column=1,columnspan=1)
                elif self.current_language != len(self.language_frames)-1:
                    ttk.Button(frame, text="Następny język", command=self.next_language).grid(row=2,column=2,columnspan=1)
                    ttk.Button(frame, text="Poprzedni język", command=self.prev_language).grid(row=2,column=3,columnspan=1)
                    ttk.Button(frame, text="Wróć do poprzedniego kroku", command=self.prev_step).grid(row=2,column=1,columnspan=1)
                else:
                    ttk.Button(frame, text="Poprzedni język", command=self.prev_language).grid(row=2,column=3,columnspan=1)
                    ttk.Button(frame, text="Następny krok", command=self.next_step).grid(row=2,column=2,columnspan=1)
                    ttk.Button(frame, text="Wróć do poprzedniego kroku", command=self.prev_step).grid(row=2,column=1,columnspan=1)
                frame.grid()
            else:
                frame.grid_remove()

    def next_language(self):
        if self.current_language != len(self.language_frames):
            self.current_language += 1
            self.show_language_frame(self.current_language)
        else:
            tk.messagebox.showerror("Błąd", "Nie ma już więcej języków")

    def prev_language(self):
        if self.current_language != 0:
            self.current_language -= 1
            self.show_language_frame(self.current_language)
        else:
            tk.messagebox.showerror("Błąd", "Jesteś na początku")

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
            # Check if the user entered a value in the new window
            if not hasattr(self, 'new_window_value'):
                self.game_name = self.entry1.get()
                self.selection = self.treeview.selection()
                if not self.game_name:
                    tk.messagebox.showerror("Błąd", "Musisz wprowadzić nazwę gry")
                    return
                if not self.selection:
                    tk.messagebox.showerror("Błąd", "Musisz wybrać grę z listy")
                    return
                item = self.treeview.item(self.selection[0])
                self.game_id = item['values'][1]
            print(self.game_id)
            self.step1_frame.destroy()
            self.create_step2()
            self.step += 1
        elif self.step == 2:
            try:
                self.selected_languages = [option for option, var in self.checkboxes.items() if var.get()]
                if not self.selected_languages:
                    raise ValueError
            except ValueError:
                tk.messagebox.showerror("Błąd", "Musisz wybrać przynajmniej jeden język")
                return
            print(self.selected_languages)    
            self.step2_frame.destroy()
            self.create_step3()
            self.step += 1
        elif self.step == 3:
            for i in self.entries.values():
                try:
                    print(i.get())
                except:
                    pass
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
            self.step2_frame.destroy()
            self.create_step1()
            self.step -= 1
        elif self.step == 3:
            self.step3_frame.destroy()
            self.create_step2()
            self.step -= 1
        elif self.step == 4:
            self.step4_frame.destroy()
            self.create_step3()
            self.step -= 1

root = tk.Tk()
root.minsize(width=1280, height=720)
style = Style(theme="darkly")
app = App(root)
root.mainloop()
