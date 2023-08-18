def script_method(fn, _rcb=None):
    return fn
def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj    
import torch.jit
torch.jit.script_method = script_method 
torch.jit.script = script


import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import webbrowser
import subprocess
import os
import pandas as pd
import threading
from tkinter import filedialog
from queue import Queue
import sys
import torch
import requests
import io

sys.stderr = open('error.txt', 'w')
sys.stdout = open('output.txt', 'w')

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if value in val:
            return key
    return None

class App:
    def __init__(self, master):
        self.languages_codes = {'angielski': ('en', 'english'), 'arabski': ('ar', 'arabic'), 'bułgarski': ('bg', 'bulgarian'), 'chiński uproszczony': ('zh-CN', 'schinese'), 'chiński tradycyjny': ('zh-TW', 'tchinese'), 'czeski': ('cs', 'czech'),'duński': ('da', 'danish'),'niderlandzki': ('nl', 'dutch'),'fiński': ('fi', 'finnish'),'francuski': ('fr', 'french'),'niemiecki': ('de', 'german'),'grecki': ('el', 'greek'),'węgierski': ('hu', 'hungarian'),'włoski': ('it', 'italian'),'japoński': ('ja', 'japanese'),'koreański': ('ko', 'koreana'),'norweski': ('no', 'norwegian'),'polski': ('pl', 'polish'),'portugalski': ('pt', 'portuguese'),'rumuński': ('ro', 'romanian'),'rosyjski': ('ru', 'russian'),'hiszpański': ('es', 'spanish'),'hiszpański latynoamerykański': ('es-419', 'latam'),'szwedzki': ('sv', 'swedish'),'tajski': ('th', 'thai'),'turecki': ('tr', 'turkish'),'ukraiński': ('uk', 'ukrainian'),'wietnamski': ('vn','vietnamese')}

        self.master = master
        self.threads_done = 0
        self.step = 1
        self.entries = {}
        self.game_name = ""
        self.game_id = 0
        self.tags = tk.StringVar()
        self.review_num = 0
        self.selected_languages = []
        self.tagging = False
        self.tags = ""
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

    def search_steam(self, game_name):
        print('test')
        from difflib import get_close_matches
        url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
        result = []
        response = requests.get(url)
        data = response.json()
        apps = data["applist"]["apps"]
        app_names = [app["name"] for app in apps]
        closest_matches = get_close_matches(game_name, app_names, n=10, cutoff=0.6)
        for match in closest_matches:
            for app in apps:
                if app["name"] == match:
                    result.append(f'Nazwa gry: {app["name"]}, ID gry: {app["appid"]}, Link do strony gry na Steam: https://store.steampowered.com/app/{app["appid"]}')
                    break
        return result

    def search(self):
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        # Run the Python code in a separate file and display the results in the Listbox
        game_name = self.entry1.get()
        results = self.search_steam(game_name)
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

    def get_review_count(self, game_name: str, languages: list) -> list:
        review_count = []
        for lang in languages:
            url = f"https://store.steampowered.com/appreviews/{game_name}?json=1&language={lang}"
            response = requests.get(url)
            data = response.json()
            review_count.append(data["query_summary"]["total_reviews"])
        return review_count


    def create_step3(self):
        self.step3_frame = ttk.Frame(self.master)
        self.step3_frame.pack()
        self.step3_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        languages = [self.languages_codes[language][1] for language in self.selected_languages]
        results = self.get_review_count(str(self.game_id), languages)
        lang_num = dict(zip(languages, results))

        self.language_frames = []
        self.current_language = 0
        for language, max_reviews in lang_num.items():
            custom_scale = tk.IntVar()
            custom_scale.set(100 if max_reviews > 100 else max_reviews)
            frame = ttk.Frame(self.step3_frame)
            if max_reviews > 0:
                ttk.Label(frame, text=f"Dla języka {find_key_by_value(self.languages_codes, language)}:").grid(row=0,column=0, columnspan=4)
                tk.Scale(frame, from_=1, to=max_reviews, orient='horizontal', variable=custom_scale, length=400, resolution= 1).grid(row=1,column=1,columnspan=1,pady=10, padx=10)
                custom_entry = ttk.Entry(frame, textvariable=custom_scale)
                custom_entry.grid(row=1,column=3,columnspan=1,pady=10)
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
        self.step4_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.is_tagging = tk.BooleanVar()

        ttk.Checkbutton(self.step4_frame, text="Chcę skorzystać z wyszukiwania po tagach (UWAGA MOŻE ZAJĄĆ BARDZO DUŻO CZASU!):", variable=self.is_tagging).grid(column=0, row=0)
        self.tags_text = tk.Text(self.step4_frame, width=80, height=10, wrap='word')
        self.tags_text.grid(ipady=3, row=1, column=0, rowspan=4)

        ttk.Button(self.step4_frame, text="Dalej", command=self.next_step).grid(row=5,column=1)
        ttk.Button(self.step4_frame, text="Cofnij", command=self.prev_step).grid(row=5,column=0)

    def create_step5(self):
        self.step5_frame = ttk.Frame(self.master)
        self.step5_frame.pack()
        self.step5_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step5_frame, text="Wybierz opcje dodatkowe:").pack()
        self.summarize_var = tk.BooleanVar()
        self.sentiment_var = tk.BooleanVar()
        self.spam_filter = tk.BooleanVar()
        ttk.Checkbutton(self.step5_frame, text="Użyj zaawansowanego filtra spamu (ZALECANE)", variable=self.spam_filter).pack(pady=5)
        ttk.Checkbutton(self.step5_frame, text="Użyj streszczania opinii dłuższych niż 300 znaków", variable=self.summarize_var).pack(pady=5)
        ttk.Checkbutton(self.step5_frame, text="Sprawdź sentyment", variable=self.sentiment_var).pack(pady=5)

        ttk.Button(self.step5_frame, text="Dalej", command=self.next_step).pack()
        ttk.Button(self.step5_frame, text="Cofnij", command=self.prev_step).pack()


    def create_step6(self):
        self.step6_frame = ttk.Frame(self.master)
        self.step6_frame.pack()
        self.step6_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        from Modules.scraper import get_steam_reviews
        ttk.Label(self.step6_frame, text='Trwa pobieranie opinii').grid(column=0,row=0,columnspan=2)
        pb = ttk.Progressbar(self.step6_frame, orient="horizontal", mode="determinate", length=280)
        pb.grid(column=0, row=1, columnspan=2, padx=10, pady=20)

        total = sum(int(value) for value in self.entries.values())
        total_var = tk.StringVar(self.step6_frame, value="Pozostały czas: ")

        ttk.Label(self.step6_frame, textvariable=total_var).grid(column=0,row=2,columnspan=2)
        total_time = 0.0
        
        
        def update_progressbar(value, time):
            pb['value'] += value
            pb.update_idletasks()
            nonlocal total_time
            total_time += time
            
            avg_time_per_unit = total_time / pb['value']
            # Calculate the remaining progress
            remaining_progress = 100 - pb['value']
            # Estimate the remaining time
            remaining_time = avg_time_per_unit * remaining_progress

            if remaining_time < 31:
                total_var.set("Już prawie skończone")
            else:
                remaining_minutes = round(remaining_time / 60)
                total_var.set(f"Pozostały czas: około {remaining_minutes} minut")

        self.file_path = filedialog.askdirectory(title="Select folder")
        
        def on_threads_finished(file_path):
            # This function will be called after all threads have finished
            # Add your code here to process the files
            files = [f for f in os.listdir(file_path) if f.endswith('.xlsx')]
            data = []
            print(files)

            for file in files:
                file_path2 = f'{file_path}/{file}'
                print(file_path2)
                df = pd.read_excel(file_path2)
                data.append(df)
                os.remove(file_path2)

            # Concatenate all data into a single DataFrame
            combined_data = pd.concat(data)
            # Write the combined data to the output file
            combined_data.to_excel(f'{file_path}/output.xlsx', index=False)
            self.next_step()


        if self.file_path:
            print(self.file_path)
            threads =[]
            for i, j in self.entries.items():
                t = threading.Thread(target=get_steam_reviews, args=(self.file_path, update_progressbar, total, self.game_id, i, j))
                t.start()
                threads.append(t)
            
            # Wait for all threads to finish without blocking the main thread
            def check_threads():
                if all(not t.is_alive() for t in threads):
                    # All threads have finished
                    self.threads_done = 1
                    on_threads_finished(self.file_path)
                else:
                    # Not all threads have finished, check again after some time
                    self.master.after(1000, check_threads)

            # Start checking if all threads have finished
            check_threads()

    def create_step7(self):
        if any(x != 'english' for x in self.entries.keys()):
            self.threads_done = 0
            self.step7_frame = ttk.Frame(self.master)
            self.step7_frame.pack()
            self.step7_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            from Modules.translator import translate_content
            file_location = f'{self.file_path}/output.xlsx'
            ttk.Label(self.step7_frame, text='Trwa tłumaczenie opinii').grid(column=0,row=0,columnspan=2)
            pb = ttk.Progressbar(self.step7_frame, orient="horizontal", mode="determinate", length=280)
            pb.grid(column=0, row=1, columnspan=2, padx=10, pady=20)

            total_var = tk.StringVar(self.step7_frame, value="Pozostały czas: ")

            ttk.Label(self.step7_frame, textvariable=total_var).grid(column=0,row=2,columnspan=2)

            done = tk.StringVar(self.step7_frame, value=" ")

            ttk.Label(self.step7_frame, textvariable=done).grid(column=0,row=3,columnspan=2)
            total_time = 0.0

            df = pd.read_excel(file_location)
            num_to_translate = len(df[(df['language'] != 'english') & (df['content'].str.len() >= 3)])

            total = 0

            def update_progressbar(value, time):
                pb['value'] += value
                pb.update_idletasks()
                nonlocal total_time
                nonlocal total
                total_time += time
                total += 1
                
                avg_time_per_unit = total_time / pb['value']
                # Calculate the remaining progress
                remaining_progress = 100 - pb['value']
                # Estimate the remaining time
                remaining_time = avg_time_per_unit * remaining_progress
                
                done.set(f"{total}/{num_to_translate}")
                
                if remaining_time < 31:
                    total_var.set("Już prawie skończone")
                else:
                    remaining_minutes = round(remaining_time / 60)
                    total_var.set(f"Pozostały czas: około {remaining_minutes} minut")

            queue = Queue()
            threads =[]
            t = threading.Thread(target=translate_content, args=(df, update_progressbar,num_to_translate,queue))
            t.start()
            threads.append(t)

            def check_threads():
                if all(not t.is_alive() for t in threads):
                    self.threads_done = 1
                    print('tutaj')
                    result = pd.concat(list(queue.queue))
                    print('tu')
                    result.to_excel(f'{self.file_path}/output.xlsx', index=False)
                    print('nie bo tu')
                    self.next_step()
                else:
                    # Not all threads have finished, check again after some time
                    print('jeszcze nie')
                    print(threads)
                    self.master.after(1000, check_threads)
            
            check_threads()
        else:
            self.next_step()

    def create_step8(self):
        self.step8_frame = ttk.Frame(self.master)
        self.step8_frame.pack()
        self.threads_done = 0
        file_location = f'{self.file_path}/output.xlsx'
        self.step8_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step8_frame, text='Trwa odrzucanie spamu').grid(column=0,row=0,columnspan=2)
        pb = ttk.Progressbar(self.step8_frame, orient="horizontal", mode="determinate", length=280)
        pb.grid(column=0, row=1, columnspan=2, padx=10, pady=20)
        from Modules.API import spam_remover

        queue = Queue()
        threads =[]

        total_var = tk.StringVar(self.step8_frame, value="Pozostały czas: ")

        ttk.Label(self.step8_frame, textvariable=total_var).grid(column=0,row=2,columnspan=2)
        total_time = 0.0

        def update_progressbar(value, time):
            pb['value'] += value
            pb.update_idletasks()
            nonlocal total_time
            total_time += time
            print(time,total_time)
            avg_time_per_unit = total_time / pb['value']
            # Calculate the remaining progress
            remaining_progress = 100 - pb['value']
            # Estimate the remaining time
            remaining_time = avg_time_per_unit * remaining_progress
            
            if remaining_time < 31:
                total_var.set("Już prawie skończone")
            else:
                remaining_minutes = round(remaining_time / 60)
                total_var.set(f"Pozostały czas: około {remaining_minutes} minut")

        df = pd.read_excel(file_location)
        total = df.shape[0]
        t = threading.Thread(target=spam_remover, args=(df,queue,update_progressbar,total))
        t.start()

        threads.append(t)

        def check_threads():
            if all(not t.is_alive() for t in threads):
                self.threads_done = 1
                result = pd.concat(list(queue.queue))
                result.to_excel(f'{self.file_path}/output.xlsx', index=False)
                self.next_step()
            else:
                # Not all threads have finished, check again after some time
                self.master.after(1000, check_threads)
        
        check_threads()

    def create_step9(self):
        self.step9_frame = ttk.Frame(self.master)
        self.step9_frame.pack()
        self.threads_done = 0
        from Modules.API import sentiment
        file_location = f'{self.file_path}/output.xlsx'
        self.step9_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step9_frame, text='Trwa sprawdzanie sentymentu').grid(column=0,row=0,columnspan=2)
        pb = ttk.Progressbar(self.step9_frame, orient="horizontal", mode="determinate", length=280)
        pb.grid(column=0, row=1, columnspan=2, padx=10, pady=20)

        queue = Queue()
        threads =[]

        total_var = tk.StringVar(self.step9_frame, value="Pozostały czas: ")

        ttk.Label(self.step9_frame, textvariable=total_var).grid(column=0,row=2,columnspan=2)
        total_time = 0.0

        def update_progressbar(value, time):
            pb['value'] += value
            pb.update_idletasks()
            nonlocal total_time
            total_time += time
            
            avg_time_per_unit = total_time / pb['value']
            # Calculate the remaining progress
            remaining_progress = 100 - pb['value']
            # Estimate the remaining time
            remaining_time = avg_time_per_unit * remaining_progress
            
            if remaining_time < 31:
                total_var.set("Już prawie skończone")
            else:
                remaining_minutes = round(remaining_time / 60)
                total_var.set(f"Pozostały czas: około {remaining_minutes} minut")

        df = pd.read_excel(file_location)
        total = df.shape[0]

        t = threading.Thread(target=sentiment, args=(df,queue,update_progressbar,total))
        t.start()
        threads.append(t)

        def check_threads():
            if all(not t.is_alive() for t in threads):
                self.threads_done = 1
                result = pd.concat(list(queue.queue))
                result.to_excel(f'{self.file_path}/output.xlsx', index=False)
                self.next_step()
            else:
                # Not all threads have finished, check again after some time
                self.master.after(1000, check_threads)
        
        check_threads()

    def create_step10(self):
        self.step10_frame = ttk.Frame(self.master)
        self.step10_frame.pack()
        self.threads_done = 0
        from Modules.API import summary
        file_location = f'{self.file_path}/output.xlsx'
        self.step10_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step10_frame, text='Trwa streszczanie opinii dłużych niż 300 znaków').grid(column=0,row=0,columnspan=2)
        pb = ttk.Progressbar(self.step10_frame, orient="horizontal", mode="determinate", length=280)
        pb.grid(column=0, row=1, columnspan=2, padx=10, pady=20)

        queue = Queue()
        threads =[]

        total_var = tk.StringVar(self.step10_frame, value="Pozostały czas: ")

        ttk.Label(self.step10_frame, textvariable=total_var).grid(column=0,row=2,columnspan=2)
        total_time = 0.0

        def update_progressbar(value, time):
            pb['value'] += value
            pb.update_idletasks()
            nonlocal total_time
            total_time += time
            
            avg_time_per_unit = total_time / pb['value']
            # Calculate the remaining progress
            remaining_progress = 100 - pb['value']
            # Estimate the remaining time
            remaining_time = avg_time_per_unit * remaining_progress
            
            if remaining_time < 31:
                total_var.set("Już prawie skończone")
            else:
                remaining_minutes = round(remaining_time / 60)
                total_var.set(f"Pozostały czas: około {remaining_minutes} minut")
        
        df = pd.read_excel(file_location)
        total = (df['translated'].str.len() > 100).sum()

        t = threading.Thread(target=summary, args=(df,queue,update_progressbar,total))
        t.start()
        threads.append(t)

        def check_threads():
            if all(not t.is_alive() for t in threads):
                self.threads_done = 1
                result = pd.concat(list(queue.queue))
                result.to_excel(f'{self.file_path}/output.xlsx', index=False)
                self.next_step()
            else:
                # Not all threads have finished, check again after some time
                self.master.after(1000, check_threads)

        check_threads()

    def create_step11(self):
        self.step11_frame = ttk.Frame(self.master)
        self.step11_frame.pack()
        self.threads_done = 0
        from Modules.API import tagger
        file_location = f'{self.file_path}/output.xlsx'
        self.step11_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step11_frame, text='Trwa przeszukiwanie treści w poszkiwaniu tagów').grid(column=0,row=0,columnspan=2)
        pb = ttk.Progressbar(self.step11_frame, orient="horizontal", mode="determinate", length=280)
        pb.grid(column=0, row=1, columnspan=2, padx=10, pady=20)

        queue = Queue()
        threads =[]

        total_var = tk.StringVar(self.step11_frame, value="Pozostały czas: ")

        ttk.Label(self.step11_frame, textvariable=total_var).grid(column=0,row=2,columnspan=2)
        total_time = 0.0

        def update_progressbar(value, time):
            pb['value'] += value
            pb.update_idletasks()
            nonlocal total_time
            total_time += time
            
            avg_time_per_unit = total_time / pb['value']
            # Calculate the remaining progress
            remaining_progress = 100 - pb['value']
            # Estimate the remaining time
            remaining_time = avg_time_per_unit * remaining_progress
            
            if remaining_time < 31:
                total_var.set("Już prawie skończone")
            else:
                remaining_minutes = round(remaining_time / 60)
                total_var.set(f"Pozostały czas: około {remaining_minutes} minut")
        
        
        df = pd.read_excel(file_location)
        total = df.shape[0]

        t = threading.Thread(target=tagger, args=(df,queue,update_progressbar,total, self.tags))
        t.start()
        threads.append(t)

        def check_threads():
            if all(not t.is_alive() for t in threads) & (self.threads_done == 0):
                self.threads_done = 1
                result = pd.concat(list(queue.queue))
                result.to_excel(f'{self.file_path}/output.xlsx', index=False)
                self.next_step()
            else:
                # Not all threads have finished, check again after some time
                self.master.after(1000, check_threads)

        check_threads()

    def create_step12(self):
        self.step12_frame = ttk.Frame(self.master)
        self.step12_frame.pack()
        self.step12_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(self.step12_frame, text='Koniec').grid(column=0,row=0,columnspan=2)
           

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
            languages_with_more_than_0 = {}
            for name,amount in self.entries.items():
                if type(amount) != int and amount.get() != 0:
                    languages_with_more_than_0[name] = amount.get()
            print(languages_with_more_than_0)
            self.entries = languages_with_more_than_0
            self.step3_frame.destroy()
            self.create_step4()
            self.step += 1

        elif self.step == 4:
            if self.is_tagging.get() == 1:
                self.tags = self.tags_text.get('0.0','end')
                print(self.tags)
            else:
                self.tags = "N/A"
                print(self.tags)
            self.step4_frame.destroy()
            self.create_step5()
            self.step += 1

        elif self.step == 5:
            self.step5_frame.destroy()
            self.create_step6()
            self.step += 1

        elif self.step == 6:
            self.step6_frame.destroy()
            self.create_step7()
            self.step += 1

        elif self.step == 7:
            self.step7_frame.destroy()
            if self.spam_filter.get():
                self.create_step8()
                self.step += 1
            else:
                self.step += 1
                self.next_step()

        elif self.step == 8:
            if hasattr(self, 'step8_frame'):
                self.step8_frame.destroy()
            if self.sentiment_var.get():
                self.create_step9()
                self.step += 1
            else:
                self.step += 1
                self.next_step()
            

        elif self.step == 9:
            print(self.summarize_var.get())
            if hasattr(self, 'step9_frame'):
                self.step9_frame.destroy()
            if self.summarize_var.get():
                self.create_step10()
                self.step += 1
            else:
                self.step += 1
                self.next_step()
            

        elif self.step == 10:
            if hasattr(self, 'step10_frame'):
                self.step10_frame.destroy()
            if self.is_tagging.get():
                self.create_step11()
                self.step += 1
            else:
                self.step += 1
                self.next_step()
            
        
        elif self.step == 11:
            if hasattr(self, 'step11_frame'):
                self.step11_frame.destroy()
            self.create_step12()
 

        # elif self.step == 11:
        #     if hasattr(self, 'step11_frame'):
        #         self.step11_frame.destroy()
        #     if self.is_tagging.get():
        #         self.create_step12()
        #         self.step += 1
        #     else:
        #         self.step += 1
        #         self.next_step()
        #     self.step += 1

            
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
