from models import Person, Record, AgeCategories
from windows import App

if __name__ == "__main__":
    Person.create_table()
    Record.create_table()
    AgeCategories.create_table()

    app = App()
    app.mainloop()
