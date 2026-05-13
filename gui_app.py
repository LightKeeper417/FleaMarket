import tkinter as tk
import customtkinter as ctk
import sqlite3
import threading
import subprocess
import sys
import os

# Устанавливаем тему
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BlacklistGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Управление Blacklist Ботом")
        self.geometry("600x500")

        # Настройка сетки
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Верхняя панель ---
        self.top_panel = ctk.CTkFrame(self)
        self.top_panel.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.status_label = ctk.CTkLabel(self.top_panel, text="Статус: Бот выключен", text_color="red")
        self.status_label.pack(side="left", padx=10)

        self.start_btn = ctk.CTkButton(self.top_panel, text="Запустить бота", command=self.run_bot_thread)
        self.start_btn.pack(side="right", padx=10)

        # --- Список слов ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.label_title = ctk.CTkLabel(self.list_frame, text="Запрещенные слова:")
        self.label_title.pack(pady=5)

        self.word_list = tk.Listbox(self.list_frame, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.word_list.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Панель управления словами ---
        self.edit_panel = ctk.CTkFrame(self)
        self.edit_panel.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.entry_word = ctk.CTkEntry(self.edit_panel, placeholder_text="Слово")
        self.entry_word.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_reason = ctk.CTkEntry(self.edit_panel, placeholder_text="Причина")
        self.entry_reason.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.add_btn = ctk.CTkButton(self.edit_panel, text="Добавить", width=100, command=self.add_word)
        self.add_btn.pack(side="left", padx=5)

        self.del_btn = ctk.CTkButton(self.edit_panel, text="Удалить", width=100, fg_color="red", hover_color="#8B0000", command=self.delete_word)
        self.del_btn.pack(side="left", padx=5)

        self.refresh_list()

    def refresh_list(self):
        """Обновляет список слов из БД"""
        self.word_list.delete(0, tk.END)
        try:
            con = sqlite3.connect('blacklist.db')
            cur = con.cursor()
            cur.execute("SELECT Word, reason FROM Words")
            rows = cur.fetchall()
            for row in rows:
                self.word_list.insert(tk.END, f"{row[0]} — {row[1]}")
            con.close()
        except Exception as e:
            print(f"Ошибка БД: {e}")

    def add_word(self):
        word = self.entry_word.get().lower()
        reason = self.entry_reason.get()
        if word:
            con = sqlite3.connect('blacklist.db')
            cur = con.cursor()
            cur.execute("INSERT INTO Words (Word, reason) VALUES (?, ?)", (word, reason))
            con.commit()
            con.close()
            self.refresh_list()
            self.entry_word.delete(0, tk.END)
            self.entry_reason.delete(0, tk.END)

    def delete_word(self):
        selected = self.word_list.get(tk.ACTIVE)
        if selected:
            word = selected.split(" — ")[0]
            con = sqlite3.connect('blacklist.db')
            cur = con.cursor()
            cur.execute("DELETE FROM Words WHERE Word = ?", (word,))
            con.commit()
            con.close()
            self.refresh_list()

    def run_bot_thread(self):
        """Запуск бота в отдельном потоке, чтобы GUI не завис"""
        self.status_label.configure(text="Статус: Бот работает", text_color="green")
        self.start_btn.configure(state="disabled")
        
        # Запускаем main.py как отдельный процесс
        threading.Thread(target=self.start_bot_process, daemon=True).start()

    def start_bot_process(self):
        # Запускаем основной скрипт бота
        # Мы используем sys.executable для запуска через тот же интерпретатор
        os.system(f"{sys.executable} main.py")

if __name__ == "__main__":
    app = BlacklistGUI()
    app.mainloop()