import io
from datetime import datetime
from tkinter import filedialog
import matplotlib.pyplot as plt

import librosa
import ttkbootstrap as tb
from pydub import AudioSegment
from ttkbootstrap.tableview import Tableview

from models import Person, Record, ReferenceValues
from params import calc_params
import customtkinter as ctk

from PIL import Image, ImageTk
from PIL import ImageEnhance

ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.open_button = None
        self.create_button = None
        self.delete_button = None
        self.table = None
        self.toplevel_window = None

        self.config()
        self.init()
        self.pack()

    def update_table(self):
        return [[person.id, person.name, person.surname, person.category_id] for person in
                list(Person.select().execute())]

    def create_callbck(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Popup(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

    def open_callbck(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            selected = self.table.get_rows(selected=True)
            patient_id = selected[0].values[0]
            self.toplevel_window = RecordsList(self, patient_id)
        else:
            self.toplevel_window.focus()

    def delete_callbck(self):
        selected = self.table.get_rows(selected=True)

        patient_id = selected[0].values[0]
        Delete(self, pt_id=patient_id)

    def config(self):
        self.eval('tk::PlaceWindow . center')
        self.wait_visibility()
        self.title("VoiceApp")
        self.resizable(False, False)

    def init(self):
        Person.create_table()
        coldata = ["ID", "Имя", "Фамилия", "Возрастная категория"]
        self.table = Tableview(master=self, coldata=coldata, rowdata=self.update_table(), searchable=True)
        self.create_button = ctk.CTkButton(self, text="Создать", command=self.create_callbck)
        self.delete_button = ctk.CTkButton(self, text="Удалить", command=self.delete_callbck)
        self.open_button = ctk.CTkButton(self, text="Выбрать", command=self.open_callbck)

    def pack(self):
        self.table.grid(row=0, column=0, columnspan=3)
        self.create_button.grid(row=1, column=1, padx=20, pady=20)
        self.delete_button.grid(row=1, column=2, padx=20, pady=20)
        self.open_button.grid(row=1, column=0, padx=20, pady=20)


class Delete(ctk.CTkToplevel):
    def __init__(self, parent, pt_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient_id = pt_id
        self.parent = parent
        self.delete_user()

    def delete_user(self):
        person = Person.get(Person.id == self.patient_id)
        person.delete_by_id(person.id)
        self.parent.table.delete_row(self.patient_id)
        self.parent.update()
        self.destroy()


class Popup(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel_button = None
        self.save_button = None
        self.surname_entry_label = None
        self.surname_entry = None
        self.name_entry_label = None
        self.name_entry = None
        self.category_id_entry_label = None
        self.category_id_entry = None
        self.name = tb.StringVar(value="")
        self.surname = tb.StringVar(value="")
        self.category_id = tb.StringVar(value="")
        self.parent = parent
        x = parent.winfo_x() + parent.winfo_width() // 2 - parent.winfo_width() // 2
        y = parent.winfo_y() + parent.winfo_height() // 2 - parent.winfo_height() // 2
        self.geometry(f"+{x}+{y}")
        self.title("Новый пациент")
        self.resizable(False, False)
        self.init()
        self.pack()

    def init(self):
        self.name_entry = ctk.CTkEntry(self, textvariable=self.name)
        self.name_entry_label = ctk.CTkLabel(self, text="Имя")
        self.surname_entry = ctk.CTkEntry(self, textvariable=self.surname)
        self.surname_entry_label = ctk.CTkLabel(self, text="Фамилия")
        self.category_id_entry = ctk.CTkEntry(self, textvariable=self.category_id)
        self.category_id_entry_label = ctk.CTkLabel(self, text="Возрастная категория")
        self.save_button = ctk.CTkButton(self, text="Создать", command=self.save_user)
        self.cancel_button = ctk.CTkButton(self, text="Отменить", command=self.cancel)

    def pack(self):
        self.name_entry.grid(row=1, column=2, pady=10, padx=10)
        self.name_entry_label.grid(row=1, column=1)
        self.surname_entry.grid(row=2, column=2, pady=10, padx=10)
        self.surname_entry_label.grid(row=2, column=1)
        self.category_id_entry.grid(row=4, column=2, pady=10, padx=10)
        self.category_id_entry_label.grid(row=4, column=1)
        self.save_button.grid(row=5, column=1, sticky="E")
        self.cancel_button.grid(row=5, column=2, pady=10)

    def save_user(self):
        person = Person(name=self.name.get(), surname=self.surname.get(), category_id=int(self.category_id.get()))
        person.save()
        self.parent.table.insert_row("end", values=[person.id, person.name, person.surname, person.category_id])
        self.parent.update()
        self.destroy()

    def cancel(self):
        self.destroy()


class ProfileFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label1 = ctk.CTkLabel(self, text="Имя", anchor="w")
        self.label11 = ctk.CTkLabel(self, text=self.master.person.name, anchor="w")
        self.label2 = ctk.CTkLabel(self, text="Фамилия", anchor="w")
        self.label22 = ctk.CTkLabel(self, text=self.master.person.surname, anchor="w")
        self.label4 = ctk.CTkLabel(self, text="Возрастная категория", anchor="w")
        self.label44 = ctk.CTkLabel(self, text=self.master.person.category_id, anchor="w")

        self.label1.grid(row=0, column=0, padx=20)
        self.label11.grid(row=0, column=1)
        self.label2.grid(row=1, column=0, padx=20)
        self.label22.grid(row=1, column=1)
        self.label4.grid(row=3, column=0, padx=20)
        self.label44.grid(row=3, column=1)


selected_points = []


def onclick(event):
    print(f"Selected time (seconds): {event.xdata:.2f}")
    if event.xdata is not None:
        selected_points.append(event.xdata)


class RecordFrame(ctk.CTkFrame):
    def __init__(self, master, row_data, **kwargs):
        super().__init__(master, **kwargs)
        self.chosen_file = None
        self.audio_path = None
        self.master = master
        coldata = ["ID", "Дата записи"]
        self.label = Tableview(self, coldata=coldata, rowdata=row_data)
        self.label.grid(row=0, column=0, padx=20, columnspan=3, pady=20)
        self.open_button = ctk.CTkButton(self, text="Открыть", command=self.open_record)
        self.create_button = ctk.CTkButton(self, text="Новая запись", command=self.add_record)
        self.delete_button = ctk.CTkButton(self, text="Удалить запись", command=self.delete_record)
        self.open_button.grid(row=1, column=0)
        self.create_button.grid(row=1, column=1)
        self.delete_button.grid(row=1, column=2)

    def trim_audio(self):
        start_index = int(min(selected_points) * 1000)
        end_index = int(max(selected_points) * 1000)
        i = len(Record.select().where(Record.person_id == self.master.person.id).execute()) + 14
        self.chosen_file = 'resources/H' + str(self.master.person.id) + '-' + str(i + 1) + '-trimmed.wav'
        audio_file = AudioSegment.from_file(self.audio_path)
        trimmed_audio = audio_file[start_index:end_index]
        trimmed_audio.export(self.chosen_file, format="wav")
        return trimmed_audio

    def add_record(self):
        self.audio_path = filedialog.askopenfilename(initialdir="/",
                                                     title="Select a File",
                                                     filetypes=(("WAV files",
                                                                 "*.wav*"),
                                                                ("all files",
                                                                "*.*")))
        audio, sr = librosa.load(self.audio_path, sr=22050)
        print("Audio Duration:", librosa.get_duration(y=audio, sr=sr))
        fig, ax = plt.subplots(figsize=(10, 4))
        librosa.display.waveshow(audio, sr=sr, ax=ax, color="blue")
        plt.xlabel('Время (секунды)')
        plt.ylabel('Амплитуда')
        plt.title('Аудиограмма')

        plt.gcf().canvas.mpl_connect('button_press_event', onclick)

        plt.show()

        self.trim_audio()

        if self.chosen_file != '':
            with open(self.chosen_file, "rb") as fh:
                buf = io.BytesIO(fh.read())

            F0, std_F, Jloc, Sloc = calc_params(self.chosen_file)
            record = Record(person_id=self.master.person.id, create_date=datetime.now(),
                            record=buf.getvalue(), info="",
                            F0=F0, std_F=std_F, Jloc=Jloc, Sloc=Sloc)
            record.save()
            iw = ImageWork("resources/initial_image.png")
            iw.count_progress(record.person_id)

    def delete_record(self):
        selected = self.label.get_rows(selected=True)
        record_id = selected[0].values[0]

        DeleteRecord(rec_id=record_id)

    def open_record(self):
        try:
            selected = self.label.get_rows(selected=True)
            record_id = selected[0].values[0]
            print(record_id)
            self.toplevel_window = ShowRecord(self, record_id)
            self.toplevel_window.focus()
        except IndexError:
            print("Выберите запись")


class DeleteRecord:
    def __init__(self, rec_id):
        self.record_id = rec_id
        self.delete_record()

    def delete_record(self):
        record = Record.get(Record.id == self.record_id)
        record.delete_by_id(record.id)


class RecordsList(ctk.CTkToplevel):
    def __init__(self, parent, patient_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.config()
        self.person = Person.get(Person.id == patient_id)
        self.rowdata = []
        for record in Record.select().where(Record.person_id == patient_id).execute():
            self.rowdata.append([record.id, record.create_date])
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.my_frame1 = ProfileFrame(master=self)
        self.my_frame1.grid(row=0, column=0, padx=20, pady=20)
        self.my_frame2 = RecordFrame(master=self, row_data=self.rowdata)
        self.my_frame2.grid(row=0, column=1, padx=20, pady=20)

    def config(self):
        self.geometry("800x600")
        self.resizable(False, False)
        self.title("Записи пациента")


class ShowRecord(ctk.CTkToplevel):
    def __init__(self, parent, record_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person_id = None
        self.record_id = record_id
        self.parent = parent
        self.config()
        self.init()
        self.pack()
        self.show_image()

    def init(self):
        self.record = Record.get(Record.id == self.record_id)
        self.person_id = self.record.person_id
        self.label1 = ctk.CTkLabel(self, text="F0, Гц", anchor="w")
        self.label11 = ctk.CTkLabel(self, text=self.record.F0, anchor="w")
        self.label2 = ctk.CTkLabel(self, text="StD частот основного тона, Гц", anchor="w")
        self.label22 = ctk.CTkLabel(self, text=self.record.std_F, anchor="w")
        self.label3 = ctk.CTkLabel(self, text="Джиттер, %", anchor="w")
        self.label33 = ctk.CTkLabel(self, text=self.record.Jloc, anchor="w")
        self.label4 = ctk.CTkLabel(self, text="Шиммер", anchor="w")
        self.label44 = ctk.CTkLabel(self, text=self.record.Sloc, anchor="w")

    def pack(self):
        self.label1.grid(row=0, column=0, padx=20)
        self.label11.grid(row=0, column=1, padx=20)
        self.label2.grid(row=1, column=0, padx=20)
        self.label22.grid(row=1, column=1, padx=20)
        self.label3.grid(row=2, column=0, padx=20)
        self.label33.grid(row=2, column=1, padx=20)
        self.label4.grid(row=3, column=0, padx=20)
        self.label44.grid(row=3, column=1, padx=20)

    def show_image(self):
        image = Image.open("resources/progress_image_" + str(self.person_id) + "_"
                           + str(self.record_id) + ".png")
        image.show()

    def config(self):
        self.resizable(False, False)
        self.title("Характеристики записи")


class ImageWork:
    def __init__(self, image_path):
        self.image_path = image_path

    def adjust_saturation(self, factor, person_id, record_id):
        image = Image.open(self.image_path)

        enhancer = ImageEnhance.Color(image)
        enhanced_image = enhancer.enhance(factor)
        enhanced_image.show()
        enhanced_image.save("resources/progress_image_" + str(person_id) + "_" + str(record_id) + ".png")

    def count_progress(self, person_id):
        person = Person.select().where(Person.id == person_id).execute()[0]
        category_id = person.category_id
        records = list(Record.select().where(Record.person_id == person_id).execute())
        ref = list(ReferenceValues.select().where(ReferenceValues.category_id == category_id).execute())

        rec1, rec2 = records[-1], ref[0]
        dif_f0 = rec2.F0 - rec1.F0
        dif_std = rec2.std_F - rec1.std_F
        dif_j = rec2.Jloc - rec1.Jloc
        dif_s = rec2.Sloc - rec1.Sloc

        dist = pow(
            pow(dif_f0, 2) + pow(dif_std, 2) + pow(dif_j, 2) + pow(dif_s, 2),
            0.5)
        self.adjust_saturation(dist / 1000, person_id, records[-1].id)