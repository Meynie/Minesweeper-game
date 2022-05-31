import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror

from mybutton import MyButton

color_text = {
    1: '#0006b3',
    2: '#0046d1',
    3: '#00ff6e',
    4: '#ff7b00',
    5: '#10524d',
    6: '#630326',
    7: '#b8b35e',
    8: '#59361f',
}


class MineSweeper:

    ROW = 3
    COLUMN = 3
    window = tk.Tk()
    window.geometry('500x200')
    MINES = 3
    FLAG = MINES
    NOT_MINE = (ROW * COLUMN) - MINES
    IS_GAME_OVER = False
    IS_GAME_WIN = False
    IS_FIRST_CLICK = True

    def __init__(self):
        # инициализация игры
        self.buttons = []

        for i in range(MineSweeper.ROW + 2):
            temp = []
            for j in range(MineSweeper.COLUMN + 2):
                btn = MyButton(MineSweeper.window, x=i, y=j, number=0)
                btn.config(command=lambda button=btn: self.click(button))  # lambda - посредник для вызова self.click
                btn.bind('<Button-3>', self.flag)  # нажатие правой кнопки мыши
                temp.append(btn)
            self.buttons.append(temp)

        statusbar = tk.Label(self.window, text=f"Мины {MineSweeper.FLAG}", bd=1,
                             relief=tk.SUNKEN, anchor=tk.W)

        statusbar.grid(row=0, column=1)
        #statusbar = s

    def flag(self, event): # реализация правого клика
        cur_button = event.widget

        if MineSweeper.IS_GAME_OVER:
            return

        if cur_button['state'] == 'normal':
            cur_button['state'] = 'disabled'
            cur_button['text'] = '🚩'
            cur_button['disabledforeground'] = 'red'

        elif cur_button['text'] == '🚩':
            cur_button['text'] = ''
            cur_button['state'] = 'normal'

    def click(self, clicked_button: MyButton):
        counter = 0

        if MineSweeper.IS_GAME_OVER:
            return None

        if MineSweeper.IS_GAME_WIN:
            return None

        if MineSweeper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_button()
            self.print_buttons()
            MineSweeper.IS_FIRST_CLICK = False

        if clicked_button.is_mine:
            clicked_button.config(text='*', background='red', disabledforeground='black')
            clicked_button.is_open = True
            MineSweeper.IS_GAME_OVER = True
            showinfo('Game over', 'Вы проиграли.')
            for i in range(1, MineSweeper.ROW + 1): # показывает, где были бомбы
                for j in range(1, MineSweeper.COLUMN + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '*'

        else:
            color = color_text.get(clicked_button.count_mine, 'black')

            if clicked_button.count_mine:
                clicked_button.config(text=clicked_button.count_mine, disabledforeground=color)
                clicked_button.is_open = True

            else:
                self.breadth_first_search(clicked_button)
        clicked_button.config(state='disabled')  # нельзя нажать второй раз
        clicked_button.config(relief=tk.SUNKEN)  # кнопка нажата

        # проверка выигрыша
        for i in range(1, MineSweeper.ROW + 1):  # показывает, где были бомбы
            for j in range(1, MineSweeper.COLUMN + 1):
                btn = self.buttons[i][j]
                if btn.is_open:
                    counter += 1
                    if counter == self.NOT_MINE:
                        MineSweeper.IS_GAME_WIN = True
                        showinfo('You are winner', 'Вы выиграли!')

    def breadth_first_search(self, btn: MyButton):

        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            color = color_text.get(cur_btn.count_mine, 'black')
            if cur_btn.count_mine:
                cur_btn.config(text=cur_btn.count_mine, disabledforeground=color)
            else:
                cur_btn.config(text='', disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state='disabled')  # нельзя нажать второй раз
            cur_btn.config(relief=tk.SUNKEN)  # кнопка нажата
            if cur_btn.count_mine == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        # if not abs(dx - dy) == 1:
                        # continue

                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= MineSweeper.ROW and \
                                1 <= next_btn.y <= MineSweeper.COLUMN and next_btn not in queue:
                            queue.append(next_btn)

    def reload(self):
        """
        Перезапуск игры
        """
        [child.destroy() for child in self.window.winfo_children()]  # очищение окна
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False
        MineSweeper.IS_GAME_WIN = False

    def create_set_window(self):
        set_window = tk.Toplevel(self.window)
        set_window.wm_title('Настройки')

        tk.Label(set_window, text='Количество строк:').grid(row=0, column=0)
        row_entry = tk.Entry(set_window)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)

        tk.Label(set_window, text='Количество колонок:').grid(row=1, column=0)
        column_entry = tk.Entry(set_window)
        column_entry.insert(0, MineSweeper.COLUMN)
        column_entry.grid(row=1, column=1, padx=20, pady=20)

        tk.Label(set_window, text='Количество мин:').grid(row=2, column=0)
        mine_entry = tk.Entry(set_window)
        mine_entry.insert(0, MineSweeper.MINES)
        mine_entry.grid(row=2, column=1, padx=20, pady=20)

        save_btn = tk.Button(set_window, text='Применить',
                             command=lambda: self.save_set(row_entry, column_entry, mine_entry))
        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def save_set(self, row: tk.Entry, column: tk.Entry, mine: tk.Entry):

        # Ограничение вводимых величин
        try:
            int(row.get()), int(column.get()), int(mine.get())
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильное значение')
            return

        if int(row.get()) <= 0 or int(column.get()) <= 0 or int(mine.get()) <= 0:
            showerror('Ошибка', 'Величины должны быть больше 0')
            return

        if int(row.get()) * int(column.get()) <= int(mine.get()):
            showerror('Ошибка', 'Мин должно быть меньше, чем клеток')
            return

        if int(row.get()) > 20 or int(column.get()) > 20:
            showerror('Ошибка', 'Слишком большое поле')
            return

        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMN = int(column.get())
        MineSweeper.MINES = int(mine.get())
        self.reload()

    def create_widgets(self):

        # создаю меню
        menu_bar = tk.Menu(self.window)
        self.window.config(menu=menu_bar)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label='Играть', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_set_window)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menu_bar.add_cascade(label='File', menu=settings_menu)

        count = 1
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMN + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='NWES')
                count += 1

        # для нормального растяжения кнопок по экрану
        for i in range(1, MineSweeper.ROW + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)

        for i in range(1, MineSweeper.COLUMN + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

    def open_all_buttons(self):

        for i in range(MineSweeper.ROW + 2):
            for j in range(MineSweeper.COLUMN + 2):
                btn = self.buttons[i][j]

                if btn.is_mine:
                    btn.config(text='*', background='red', disabledforeground='black')

                elif btn.count_mine in color_text:
                    color = color_text.get(btn.count_mine, 'black')
                    btn.config(text=btn.count_mine, fg=color)

    def start(self):
        self.create_widgets()
        # self.open_all_buttons()

        MineSweeper.window.mainloop()

    def print_buttons(self):
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMN + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B', end='')
                else:
                    print(btn.count_mine, end='')
            print()

    def insert_mines(self, number: int):
        index_mines = self.get_mines_places(number)
        print(index_mines)

        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMN + 1):
                btn = self.buttons[i][j]

                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_button(self):
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMN + 1):
                btn = self.buttons[i][j]
                count_mine = 0
                if not btn.is_mine:
                    # ниже получаю всех соседей кнопок
                    for row_dx in [-1, 0, 1]:
                        for column_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i + row_dx][j + column_dx]
                            if neighbour.is_mine:
                                count_mine += 1

                btn.count_mine = count_mine

    @staticmethod
    def get_mines_places(exclude_num: int):
        indx = list(range(1, MineSweeper.COLUMN * MineSweeper.ROW + 1))
        print(f'Исключаю кнопку номер: {exclude_num}')
        indx.remove(exclude_num)
        shuffle(indx)
        return indx[:MineSweeper.MINES]


game = MineSweeper()
game.start()
