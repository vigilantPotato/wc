import sqlite3                  #database
import tkinter                  #GUI
import tkinter.simpledialog     #GUI(dialog)
import webbrowser
import pyperclip


def open_db():
    conn = sqlite3.connect(
        "ClipWords.db",
        isolation_level=None
        )
    return conn


class WordClipButton(tkinter.Button):

    swap_count_int = 0
    button_count_int = 0
    swap_title_1 = ""
    swap_title_2 = ""

    def __init__(self, master, delete_var, swap_var, data):
        super().__init__(
            master,
            text=data[0],
            width=15,
            command=self.button_clicked
            )
        WordClipButton.button_count_int += 1
        self.title = data[0]
        self.clipword = data[1]
        self.url = data[2]
        self.delete_var = delete_var
        self.swap_var = swap_var
        self.master = master
        self.update_db_number(self.title, WordClipButton.button_count_int)
        self.pack()

    def button_clicked(self):
        if self.delete_var.get():
            self.delete_item_from_db(self.title)

        elif self.swap_var.get():
            if WordClipButton.swap_count_int == 0:
                WordClipButton.swap_count_int += 1
                WordClipButton.swap_title_1 = self.title
            else:
                WordClipButton.swap_title_2 = self.title
                WordClipButton.swap_count_int = 0
                self.swap_items_in_db(
                    WordClipButton.swap_title_1,
                    WordClipButton.swap_title_2
                    )

        else:
            self.clip_word_and_open_link()
 

    def clip_word_and_open_link(self):
        if self.clipword != "":
            pyperclip.copy(self.clipword)

        if self.url != "":
            webbrowser.open(self.url)

    def delete_item_from_db(self, title):
        sql = "DELETE FROM Clipword WHERE title=?"
        conn = open_db()
        conn.execute(sql, (title,))
        conn.close()
        self.clear_and_resume()

    def swap_items_in_db(self, swap_title_1, swap_title_2):
        conn = open_db()
        c = conn.cursor()

        sql_select = "SELECT number FROM Clipword WHERE title = ?"
        c.execute(sql_select, (swap_title_1,))
        swap_number_1 = c.fetchone()    
        c.execute(sql_select, (swap_title_2,))
        swap_number_2 = c.fetchone()

        sql_update = "UPDATE Clipword SET number = ? WHERE title = ?"
        conn.execute(sql_update, (swap_number_1[0], swap_title_2))
        conn.execute(sql_update, (swap_number_2[0], swap_title_1))
        conn.close()
        self.clear_and_resume()

    def update_db_number(self, title, number):
        conn = open_db()
        sql_update = "UPDATE Clipword SET number = ? WHERE title = ?"
        conn.execute(sql_update, (number, title))
        conn.close()

    def clear_and_resume(self):
        self.master.destroy()
        main()


class DeleteCheckButton(tkinter.Checkbutton):

    def __init__(self, master, delete_var):
        super().__init__(
            master,
            text="Delete",
            width=15,
            variable=delete_var,
        )
        self.deleete_var = delete_var
        self.master = master
        self.pack()


class SwapCheckButton(tkinter.Checkbutton):

    def __init__(self, master, swap_var):
        super().__init__(
            master,
            text="Swap",
            width=15,
            variable=swap_var
        )

        self.master = master
        self.pack()


class CreateNewButton(tkinter.Button):

    def __init__(self, master):
        super().__init__(
            master,
            text="--create new--",
            width=15,
            bg="lightblue",
            command=self.create_new_item_to_db
            )
        self.master = master
        self.pack()

    def create_new_item_to_db(self):
        title = tkinter.simpledialog.askstring(
            'input title',
            'please input title'
            )

        if(title == None or title == ''):
            return

        clip_word = tkinter.simpledialog.askstring(
            'input clipword',
            'please input clipword'
            )
        
        link = tkinter.simpledialog.askstring(
            'input URL',
            'please input URL'
            )
        
        self.add_item_to_db(title, clip_word, link)
        self.master.destroy()
        main()

    def add_item_to_db(self, title, clip_word, link):
        conn = open_db()
        c = conn.cursor()
        sql = "SELECT MAX(number) FROM Clipword"
        c.execute(sql)
        
        max_n_cursor = c.fetchone()[0]
        
        if max_n_cursor:
            max_number = max_n_cursor + 1
        else:
            max_number = 1

        sql = """
        REPLACE INTO Clipword(title, clipword, link, number)
        VALUES (?, ?, ?, ?)
        """

        data = (title, clip_word, link, max_number)
        conn.execute(sql, data)
        conn.close()


class main():
    def __init__(self):
        root = tkinter.Tk()
        root.title("WordClipper")
        
        delete_boolean_var = tkinter.BooleanVar(root)
        swap_boolean_var = tkinter.BooleanVar(root)

        x = 130
        w = root.winfo_screenwidth()
        root.geometry('+%d+%d' % (w-x, 0))
 
        conn = open_db()
        c = conn.cursor()
        c.execute("SELECT * FROM Clipword ORDER BY number")
        db_info = c.fetchall()
        conn.close()

        WordClipButton.button_count_int = 0
        for row in db_info:
            cb = WordClipButton(root, delete_boolean_var, swap_boolean_var, row)
        
        b1 = CreateNewButton(root)
        b2 = DeleteCheckButton(root, delete_boolean_var)
        b3 = SwapCheckButton(root, swap_boolean_var)
        b4 = ShowDatabaseButton(root)

        root.mainloop()


class ShowDatabaseButton(tkinter.Button):
    def __init__(self, master):
        super().__init__(
            master,
            text="Show DB",
            width=15,
            command=self.print_database,
        )
    
        self.pack()

    def print_database(self):
        conn = open_db()
        sql = "SELECT * From Clipword ORDER BY number"
        c = conn.cursor()
        c.execute(sql)
        for row in c:
            print(row)
        conn.close()


if __name__ == "__main__":
    conn = open_db()
    sql = """
    CREATE TABLE IF NOT EXISTS Clipword (
        title VARCHAR(20) PRIMARY KEY,
        clipword VARCHAR(20),
        link VARCHAR(300),
        number INTEGER
    );
    """

    conn.execute(sql)
    conn.close()

    main()