import sys
import json
import os
import requests
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QComboBox,
    QCheckBox, QMessageBox, QListWidgetItem, QSpinBox, QStackedWidget,
    QFormLayout, QDateEdit, QFileDialog, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CourseManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Czy powinienem iść na zajęcia?")
        self.setGeometry(100, 100, 1000, 700)

        # Inicjalizacja danych
        self.courses = []
        self.current_style = "Windows XP"
        self.user_data = {
            "name": "",
            "profile_pic": "",
            "city": ""
        }
        self.weather_data = {}
        self.load_data()

        # Główne widgety
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Inicjalizacja interfejsu
        self.init_ui()
        self.apply_style(self.current_style)

    def init_ui(self):
        # Lewe menu
        self.create_left_menu()

        # Główny obszar
        self.main_area = QWidget()
        self.main_area_layout = QVBoxLayout()
        self.main_area.setLayout(self.main_area_layout)

        # Stacked widget dla różnych widoków
        self.stacked_widget = QStackedWidget()

        # Strona główna
        self.create_home_page()

        # Profil
        self.create_profile_page()

        # Edytuj przedmioty
        self.create_courses_page()

        # Dodaj oceny
        self.create_grades_page()

        # Dodaj widżety do stacked widget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.profile_page)
        self.stacked_widget.addWidget(self.courses_page)
        self.stacked_widget.addWidget(self.grades_page)

        self.main_area_layout.addWidget(self.stacked_widget)

        # Przycisk analizy na dole
        self.analyze_btn = QPushButton("Czy powinienem iść na zajęcia?")
        self.analyze_btn.clicked.connect(self.analyze_attendance)
        self.analyze_btn.setFixedHeight(40)
        self.main_area_layout.addWidget(self.analyze_btn)

        self.main_layout.addWidget(self.main_area, stretch=4)

        # Aktualizacja danych
        self.update_home_page()
        self.update_courses_list()

    def create_left_menu(self):
        self.left_menu = QWidget()
        self.left_menu.setFixedWidth(200)
        left_menu_layout = QVBoxLayout()
        self.left_menu.setLayout(left_menu_layout)

        # Logo/avatar
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(80, 80)
        self.profile_pic_label.setAlignment(Qt.AlignCenter)
        self.update_profile_pic()

        left_menu_layout.addWidget(self.profile_pic_label, alignment=Qt.AlignCenter)

        # Przyciski menu
        menu_buttons = [
            ("Strona główna", self.show_home_page),
            ("Profil", self.show_profile_page),
            ("Edytuj przedmioty", self.show_courses_page),
            ("Dodaj oceny", self.show_grades_page)
        ]

        for text, callback in menu_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(callback)
            left_menu_layout.addWidget(btn)

        left_menu_layout.addStretch()

        # Style selector
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Windows XP", "Sakura Pink"])
        self.style_combo.setCurrentText(self.current_style)
        self.style_combo.currentTextChanged.connect(self.apply_style)
        left_menu_layout.addWidget(self.style_combo)

        self.main_layout.addWidget(self.left_menu)

    def create_home_page(self):
        self.home_page = QWidget()
        home_layout = QVBoxLayout()
        self.home_page.setLayout(home_layout)

        # Nagłówek
        self.greeting_label = QLabel()
        self.greeting_label.setFont(QFont("Arial", 16, QFont.Bold))
        home_layout.addWidget(self.greeting_label)

        # Mood section
        mood_group = QGroupBox("Jak się dziś czujesz?")
        mood_layout = QHBoxLayout()

        self.mood_input = QSpinBox()
        self.mood_input.setMinimum(1)
        self.mood_input.setMaximum(10)
        self.mood_input.setFixedWidth(60)

        mood_layout.addWidget(QLabel("Samopoczucie (1-10):"))
        mood_layout.addWidget(self.mood_input)
        mood_layout.addStretch()

        mood_group.setLayout(mood_layout)
        home_layout.addWidget(mood_group)

        # Weather section
        self.weather_group = QGroupBox("Pogoda")
        weather_layout = QVBoxLayout()

        self.weather_city_label = QLabel()
        self.weather_info_label = QLabel()
        self.weather_temp_label = QLabel()
        self.weather_icon_label = QLabel()
        self.weather_icon_label.setFixedSize(50, 50)

        weather_layout.addWidget(self.weather_city_label)
        weather_layout.addWidget(self.weather_info_label)
        weather_layout.addWidget(self.weather_temp_label)
        weather_layout.addWidget(self.weather_icon_label, alignment=Qt.AlignCenter)

        self.weather_group.setLayout(weather_layout)
        home_layout.addWidget(self.weather_group)

        # Today's courses
        self.today_courses_group = QGroupBox("Dzisiejsze zajęcia")
        self.today_courses_layout = QVBoxLayout()

        self.today_courses_widget = QWidget()
        self.today_courses_widget.setLayout(self.today_courses_layout)

        self.today_courses_group.setLayout(QVBoxLayout())
        self.today_courses_group.layout().addWidget(self.today_courses_widget)
        home_layout.addWidget(self.today_courses_group)

        home_layout.addStretch()

    def create_profile_page(self):
        self.profile_page = QWidget()
        profile_layout = QVBoxLayout()
        self.profile_page.setLayout(profile_layout)

        # Profile picture
        self.profile_pic_edit_label = QLabel()
        self.profile_pic_edit_label.setFixedSize(150, 150)
        self.profile_pic_edit_label.setAlignment(Qt.AlignCenter)
        self.update_profile_pic_edit()

        self.change_pic_btn = QPushButton("Zmień zdjęcie")
        self.change_pic_btn.clicked.connect(self.change_profile_pic)

        profile_layout.addWidget(self.profile_pic_edit_label, alignment=Qt.AlignCenter)
        profile_layout.addWidget(self.change_pic_btn, alignment=Qt.AlignCenter)

        # Form
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setText(self.user_data["name"])
        self.name_input.textChanged.connect(lambda: self.user_data.update({"name": self.name_input.text()}))

        self.city_input = QLineEdit()
        self.city_input.setText(self.user_data["city"])
        self.city_input.textChanged.connect(self.update_city)

        form.addRow("Imię:", self.name_input)
        form.addRow("Miasto:", self.city_input)

        profile_layout.addLayout(form)
        profile_layout.addStretch()

    def create_courses_page(self):
        self.courses_page = QWidget()
        courses_layout = QVBoxLayout()
        self.courses_page.setLayout(courses_layout)

        # Course form
        self.course_form = QGroupBox("Dodaj/edytuj przedmiot")
        form_layout = QVBoxLayout()

        # Course name
        self.name_label = QLabel("Nazwa przedmiotu:")
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_input)

        # Course days
        self.days_label = QLabel("Dni zajęć (np. pon, śr):")
        self.days_input = QLineEdit()
        form_layout.addWidget(self.days_label)
        form_layout.addWidget(self.days_input)

        # Lecturer
        self.lecturer_label = QLabel("Prowadzący (opcjonalnie):")
        self.lecturer_input = QLineEdit()
        form_layout.addWidget(self.lecturer_label)
        form_layout.addWidget(self.lecturer_input)

        # Max absences
        self.absences_label = QLabel("Maksymalna liczba nieobecności:")
        self.absences_input = QSpinBox()
        self.absences_input.setMinimum(0)
        self.absences_input.setMaximum(100)
        form_layout.addWidget(self.absences_label)
        form_layout.addWidget(self.absences_input)

        # Current absences
        self.current_absences_label = QLabel("Aktualna liczba nieobecności:")
        self.current_absences_input = QSpinBox()
        self.current_absences_input.setMinimum(0)
        self.current_absences_input.setMaximum(100)
        form_layout.addWidget(self.current_absences_label)
        form_layout.addWidget(self.current_absences_input)

        # Mandatory checkbox
        self.mandatory_check = QCheckBox("Przedmiot obowiązkowy")
        form_layout.addWidget(self.mandatory_check)

        # Add course button
        self.add_course_btn = QPushButton("Dodaj/Zaktualizuj przedmiot")
        self.add_course_btn.clicked.connect(self.add_course)
        form_layout.addWidget(self.add_course_btn)

        self.course_form.setLayout(form_layout)
        courses_layout.addWidget(self.course_form)

        # Courses list
        self.courses_list = QListWidget()
        self.courses_list.itemClicked.connect(self.load_course_for_edit)
        courses_layout.addWidget(self.courses_list)

    def create_grades_page(self):
        self.grades_page = QWidget()
        grades_layout = QVBoxLayout()
        self.grades_page.setLayout(grades_layout)

        # Course selection
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.update_grades_form)
        grades_layout.addWidget(QLabel("Wybierz przedmiot:"))
        grades_layout.addWidget(self.course_combo)

        # Grade form
        self.grade_form = QGroupBox("Dodaj ocenę")
        form_layout = QVBoxLayout()

        # Grade value
        self.grade_value_label = QLabel("Ocena:")
        self.grade_value_input = QLineEdit()
        form_layout.addWidget(self.grade_value_label)
        form_layout.addWidget(self.grade_value_input)

        # Grade note
        self.grade_note_label = QLabel("Notatka (za co jest ocena):")
        self.grade_note_input = QLineEdit()
        form_layout.addWidget(self.grade_note_label)
        form_layout.addWidget(self.grade_note_input)

        # Date
        self.grade_date_label = QLabel("Data (opcjonalnie):")
        self.grade_date_input = QDateEdit()
        self.grade_date_input.setDate(QDate.currentDate())
        self.grade_date_input.setCalendarPopup(True)
        form_layout.addWidget(self.grade_date_label)
        form_layout.addWidget(self.grade_date_input)

        # Add grade button
        self.add_grade_btn = QPushButton("Dodaj ocenę")
        self.add_grade_btn.clicked.connect(self.add_grade)
        form_layout.addWidget(self.add_grade_btn)

        self.grade_form.setLayout(form_layout)
        grades_layout.addWidget(self.grade_form)

        # Grades list
        self.grades_list = QListWidget()
        grades_layout.addWidget(self.grades_list)

    def update_home_page(self):
        # Update greeting
        name = self.user_data.get("name", "Użytkowniku")
        self.greeting_label.setText(f"Cześć {name}!")

        # Update weather
        self.update_weather()

        # Update today's courses
        self.update_today_courses()

    def update_profile_pic(self):
        try:
            if self.user_data.get("profile_pic") and os.path.exists(self.user_data["profile_pic"]):
                pixmap = QPixmap(self.user_data["profile_pic"])
                pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.profile_pic_label.setPixmap(pixmap)
            else:
                self.profile_pic_label.setText("Brak zdjęcia")
        except Exception as e:
            logging.error(f"Błąd aktualizacji zdjęcia profilowego: {e}")
            self.profile_pic_label.setText("Błąd zdjęcia")

    def update_profile_pic_edit(self):
        try:
            if self.user_data.get("profile_pic") and os.path.exists(self.user_data["profile_pic"]):
                pixmap = QPixmap(self.user_data["profile_pic"])
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.profile_pic_edit_label.setPixmap(pixmap)
            else:
                self.profile_pic_edit_label.setText("Brak zdjęcia")
        except Exception as e:
            logging.error(f"Błąd aktualizacji zdjęcia profilowego (edycja): {e}")
            self.profile_pic_edit_label.setText("Błąd zdjęcia")

    def update_city(self):
        city = self.city_input.text().strip()
        self.user_data["city"] = city
        self.save_data()
        self.update_weather()

    def update_weather(self):
        city = self.user_data.get("city", "").strip()
        if not city:
            self.weather_city_label.setText("Nie ustawiono miasta")
            self.weather_info_label.setText("")
            self.weather_temp_label.setText("")
            self.weather_icon_label.clear()
            return

        self.weather_city_label.setText(f"Pogoda w: {city}")

        try:
            api_key = os.getenv("OPENWEATHERMAP_API_KEY", "dda747e2109d0a5935b8f8f418d84b41")
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric",
                "lang": "pl"
            }

            response = requests.get(base_url, params=params, timeout=5)
            data = response.json()

            if response.status_code == 200:
                self.weather_data = data
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"].capitalize()
                icon_code = data["weather"][0]["icon"]

                self.weather_info_label.setText(desc)
                self.weather_temp_label.setText(f"Temperatura: {temp}°C")

                icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
                response = requests.get(icon_url, timeout=5)
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.weather_icon_label.setPixmap(pixmap)
            else:
                error_msg = data.get("message", "Nieznany błąd")
                self.weather_info_label.setText(f"Błąd: {error_msg}")
                self.weather_temp_label.setText("")
                self.weather_icon_label.clear()
        except Exception as e:
            logging.error(f"Błąd pobierania pogody: {e}")
            self.weather_info_label.setText("Błąd pobierania pogody")
            self.weather_temp_label.setText("")
            self.weather_icon_label.clear()

    def update_today_courses(self):
        while self.today_courses_layout.count():
            child = self.today_courses_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        days_pl = ["pon", "wt", "śr", "czw", "pt", "sob", "niedz"]
        today = QDate.currentDate().dayOfWeek() - 1
        today_day = days_pl[today]

        today_courses = []
        for course in self.courses:
            try:
                if today_day in [d.strip() for d in course["days"].split(",") if d.strip()]:
                    today_courses.append(course)
            except KeyError as e:
                logging.error(f"Pominięto kurs z brakującymi danymi: {e}")
                continue

        if not today_courses:
            self.today_courses_layout.addWidget(QLabel("Brak zajęć na dziś"))
            return

        for course in today_courses:
            try:
                course_widget = QWidget()
                course_layout = QVBoxLayout()
                course_widget.setLayout(course_layout)

                name_label = QLabel(f"<b>{course['name']}</b>")
                lecturer_label = QLabel(f"Prowadzący: {course.get('lecturer', 'Brak')}")
                absences_label = QLabel(f"Nieobecności: {course['current_absences']}/{course['max_absences']}")
                mandatory_label = QLabel(f"Obowiązkowy: {'Tak' if course['mandatory'] else 'Nie'}")

                course_layout.addWidget(name_label)
                course_layout.addWidget(lecturer_label)
                course_layout.addWidget(absences_label)
                course_layout.addWidget(mandatory_label)

                self.today_courses_layout.addWidget(course_widget)
            except KeyError as e:
                logging.error(f"Błąd wyświetlania kursu {course.get('name', 'Unknown')}: {e}")
                continue

        self.today_courses_widget.update()

    def update_courses_list(self):
        self.courses_list.clear()
        self.course_combo.clear()
        for course in self.courses:
            try:
                item = QListWidgetItem(course["name"])
                item.setData(Qt.UserRole, course)
                self.courses_list.addItem(item)
                self.course_combo.addItem(course["name"], course)
            except KeyError as e:
                logging.error(f"Pominięto kurs z brakującymi danymi: {e}")
                continue
        logging.info(f"Zaktualizowano listę kursów: {len(self.courses)} kursów")
        self.courses_list.update()
        self.course_combo.update()

    def update_grades_form(self):
        self.grades_list.clear()
        index = self.course_combo.currentIndex()
        if index == -1:
            return

        course = self.course_combo.itemData(index)
        if not course:
            logging.warning("Brak kursu dla wybranego indeksu")
            return

        if "grades" not in course:
            course["grades"] = []
            self.save_data()

        for grade in course["grades"]:
            try:
                if not isinstance(grade, dict):
                    logging.error(f"Pominięto nieprawidłowy wpis oceny: {grade} (oczekiwano słownika)")
                    continue
                text = f"{grade['value']}"
                if grade.get("note"):
                    text += f" - {grade['note']}"
                if grade.get("date"):
                    text += f" ({grade['date']})"

                item = QListWidgetItem(text)
                self.grades_list.addItem(item)
            except (KeyError, TypeError) as e:
                logging.error(f"Błąd przetwarzania oceny: {e}, wpis: {grade}")
                continue

        self.grades_list.update()

    def add_course(self):
        name = self.name_input.text().strip()
        days = self.days_input.text().strip()
        lecturer = self.lecturer_input.text().strip()
        max_absences = self.absences_input.value()
        current_absences = self.current_absences_input.value()
        mandatory = self.mandatory_check.isChecked()

        if not name:
            QMessageBox.warning(self, "Błąd", "Nazwa przedmiotu jest wymagana!")
            return

        existing_index = -1
        for i, course in enumerate(self.courses):
            if course["name"].lower() == name.lower():
                existing_index = i
                break

        course_data = {
            "name": name,
            "days": days,
            "lecturer": lecturer,
            "max_absences": max_absences,
            "current_absences": current_absences,
            "mandatory": mandatory,
            "grades": []
        }

        if existing_index >= 0:
            course_data["grades"] = self.courses[existing_index].get("grades", [])
            self.courses[existing_index] = course_data
        else:
            self.courses.append(course_data)

        self.save_data()
        self.update_courses_list()
        self.update_today_courses()

        self.name_input.clear()
        self.days_input.clear()
        self.lecturer_input.clear()
        self.absences_input.setValue(0)
        self.current_absences_input.setValue(0)
        self.mandatory_check.setChecked(False)
        logging.info(f"Dodano/Zaktualizowano kurs: {name}")

    def load_course_for_edit(self, item):
        try:
            course = item.data(Qt.UserRole)
            self.name_input.setText(course["name"])
            self.days_input.setText(course["days"])
            self.lecturer_input.setText(course.get("lecturer", ""))
            self.absences_input.setValue(course["max_absences"])
            self.current_absences_input.setValue(course["current_absences"])
            self.mandatory_check.setChecked(course["mandatory"])
        except KeyError as e:
            logging.error(f"Błąd ładowania kursu do edycji: {e}")
            QMessageBox.warning(self, "Błąd", "Nie można załadować kursu do edycji")

    def add_grade(self):
        index = self.course_combo.currentIndex()
        if index == -1:
            QMessageBox.warning(self, "Błąd", "Wybierz przedmiot!")
            return

        course = self.course_combo.itemData(index)
        value = self.grade_value_input.text().strip()
        note = self.grade_note_input.text().strip()
        date = self.grade_date_input.date().toString("yyyy-MM-dd")

        if not value:
            QMessageBox.warning(self, "Błąd", "Wprowadź ocenę!")
            return

        grade = {
            "value": value,
            "note": note,
            "date": date
        }

        if "grades" not in course:
            course["grades"] = []
        course["grades"].append(grade)

        self.save_data()
        self.update_grades_form()

        self.grade_value_input.clear()
        self.grade_note_input.clear()
        self.grade_date_input.setDate(QDate.currentDate())
        logging.info(f"Dodano ocenę dla kursu: {course['name']}")

    def change_profile_pic(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz zdjęcie profilowe", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            self.user_data["profile_pic"] = file_path
            self.save_data()
            self.update_profile_pic()
            self.update_profile_pic_edit()
            logging.info(f"Zmieniono zdjęcie profilowe na: {file_path}")

    def analyze_attendance(self):
        if not self.courses:
            QMessageBox.warning(self, "Błąd", "Najpierw dodaj jakieś przedmioty!")
            return

        mood = self.mood_input.value()
        analysis = "<h3>Analiza:</h3>"

        # Weather impact
        if self.weather_data:
            try:
                weather_id = self.weather_data["weather"][0]["id"]
                if weather_id < 600:
                    analysis += "<p>Uwaga: Dzisiaj pada. Rozważ zabranie parasola lub ubranie się odpowiednio do pogody.</p>"
                elif weather_id == 800:
                    analysis += "<p>Pogoda jest ładna, to dobry dzień na zajęcia!</p>"
                elif weather_id > 800:
                    analysis += "<p>Dzisiaj jest pochmurno, ale to nie powinno wpłynąć na Twoją obecność.</p>"
            except KeyError as e:
                logging.error(f"Błąd analizy pogody: {e}")
                analysis += "<p>Błąd analizy pogody.</p>"

        # Mood analysis
        if mood < 3:
            analysis += "<p style='color: red;'>Twoje samopoczucie jest bardzo słabe. Jeśli to możliwe, rozważ pozostanie w domu i odpoczynek.</p>"
        elif mood < 5:
            analysis += "<p style='color: orange;'>Twoje samopoczucie jest słabe. Jeśli przedmioty nie są obowiązkowe, możesz rozważyć nieobecność.</p>"
        elif mood < 7:
            analysis += "<p>Twoje samopoczucie jest w porządku. Powinieneś być w stanie pójść na zajęcia.</p>"
        else:
            analysis += "<p style='color: green;'>Twoje samopoczucie jest bardzo dobre! To świetny dzień na naukę.</p>"

        # Courses analysis
        days_pl = ["pon", "wt", "śr", "czw", "pt", "sob", "niedz"]
        today = QDate.currentDate().dayOfWeek() - 1
        today_day = days_pl[today]

        today_courses = []
        for course in self.courses:
            try:
                if today_day in [d.strip() for d in course["days"].split(",") if d.strip()]:
                    today_courses.append(course)
            except KeyError as e:
                logging.error(f"Pominięto kurs w analizie: {e}")
                continue

        if not today_courses:
            analysis += "<p>Dzisiaj nie masz żadnych zajęć. Możesz odpocząć!</p>"
        else:
            analysis += "<h4>Dzisiejsze zajęcia:</h4>"

            for course in today_courses:
                try:
                    course_analysis = f"<p><b>{course['name']}</b><br>"

                    if course['mandatory']:
                        course_analysis += "- <span style='color: red;'>Obowiązkowe: Musisz iść na zajęcia</span><br>"
                    else:
                        course_analysis += "- Nieobowiązkowe: Możesz rozważyć nieobecność<br>"

                    absence_percentage = (course['current_absences'] / course['max_absences']) * 100 if course['max_absences'] > 0 else 0
                    if absence_percentage > 80:
                        course_analysis += "- <span style='color: red;'>Uwaga! Masz już prawie wyczerpany limit nieobecności</span><br>"
                    elif absence_percentage > 50:
                        course_analysis += "- Masz wykorzystaną ponad połowę nieobecności<br>"
                    else:
                        course_analysis += "- Masz jeszcze sporo nieobecności do wykorzystania<br>"

                    if course.get('grades'):
                        numeric_grades = []
                        for grade in course['grades']:
                            try:
                                numeric_grade = float(grade['value'])
                                numeric_grades.append(numeric_grade)
                            except (ValueError, KeyError):
                                continue

                        if numeric_grades:
                            avg_grade = sum(numeric_grades) / len(numeric_grades)
                            if avg_grade >= 4.0:
                                course_analysis += "- Twoje oceny są dobre, możesz sobie pozwolić na nieobecność<br>"
                            elif avg_grade >= 3.0:
                                course_analysis += "- Twoje oceny są średnie, lepiej idź na zajęcia<br>"
                            else:
                                course_analysis += "- <span style='color: red;'>Twoje oceny są słabe, koniecznie idź na zajęcia</span><br>"
                        else:
                            course_analysis += "- Brak ocen liczbowych do analizy<br>"
                    else:
                        course_analysis += "- Brak ocen do analizy<br>"

                    analysis += course_analysis + "</p>"
                except KeyError as e:
                    logging.error(f"Błąd analizy kursu {course.get('name', 'Unknown')}: {e}")
                    continue

        mandatory_courses = [c for c in today_courses if c.get('mandatory', False)]
        if mandatory_courses:
            analysis += "<h3 style='color: red;'>Rekomendacja: Musisz iść na zajęcia (przedmioty obowiązkowe)</h3>"
        elif mood < 3:
            analysis += "<h3 style='color: orange;'>Rekomendacja: Zostań w domu i odpocznij</h3>"
        elif mood < 5:
            analysis += "<h3 style='color: orange;'>Rekomendacja: Możesz zostać w domu, ale rozważ pójście na zajęcia</h3>"
        else:
            analysis += "<h3 style='color: green;'>Rekomendacja: Idź na zajęcia</h3>"

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Analiza obecności")
        dialog.setTextFormat(Qt.RichText)
        dialog.setText(analysis)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()

    def apply_style(self, style_name):
        self.current_style = style_name
        self.user_data["style"] = style_name
        self.save_data()

        # Definicja stylów
        styles = {
            "Sakura Pink": {
                "bg_color": "#ffe4ec",
                "text_color": "#5a0032",
                "button_color": "#ffb6c1",
                "button_text": "#5a0032",
                "list_color": "#ffd1dc",
                "group_color": "#ffecf1",
                "menu_color": "#ffc0cb"
            },
            "Windows XP": {
                "bg_color": "#e4ecf5",
                "text_color": "#003366",
                "button_color": "#d7e3f2",
                "button_text": "#003366",
                "list_color": "#c6d9f1",
                "group_color": "#e8f1fb",
                "menu_color": "#c6d9f1"
            }
        }

        style_config = styles.get(style_name, styles["Windows XP"])
        style = f"""
            QWidget {{
                background-color: {style_config['bg_color']};
                color: {style_config['text_color']};
                font-family: Arial;
            }}
            QPushButton {{
                background-color: {style_config['button_color']};
                color: {style_config['button_text']};
                border: 1px solid {style_config['text_color']};
                padding: 5px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {style_config['list_color']};
            }}
            QLineEdit, QSpinBox, QComboBox, QDateEdit, QTextEdit {{
                background-color: white;
                color: {style_config['text_color']};
                border: 1px solid {style_config['text_color']};
            }}
            QListWidget {{
                background-color: {style_config['list_color']};
                color: {style_config['text_color']};
            }}
            QGroupBox {{
                background-color: {style_config['group_color']};
                border: 1px solid {style_config['text_color']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
            }}
            #left_menu {{
                background-color: {style_config['menu_color']};
                border-right: 2px solid {style_config['text_color']};
            }}
        """

        self.setStyleSheet(style)
        self.left_menu.setStyleSheet(style)
        logging.info(f"Zastosowano styl: {style_name}")

    def save_data(self):
        data = {
            "courses": self.courses,
            "user_data": self.user_data,
            "style": self.current_style
        }
        try:
            with open("course_data.json", "w") as f:
                json.dump(data, f, indent=4)
            logging.info("Zapisano dane do course_data.json")
        except Exception as e:
            logging.error(f"Błąd zapisu danych: {e}")
            QMessageBox.warning(self, "Błąd", "Nie udało się zapisać danych!")

    def load_data(self):
        if os.path.exists("course_data.json"):
            try:
                with open("course_data.json", "r") as f:
                    data = json.load(f)
                    self.courses = data.get("courses", [])
                    self.user_data = data.get("user_data", {
                        "name": "", "profile_pic": "", "city": ""
                    })
                    self.current_style = data.get("style", "Windows XP")

                    # Walidacja kursów
                    for course in self.courses:
                        course.setdefault("name", "Unnamed Course")
                        course.setdefault("days", "")
                        course.setdefault("lecturer", "")
                        course.setdefault("max_absences", 0)
                        course.setdefault("current_absences", 0)
                        course.setdefault("mandatory", False)
                        course.setdefault("grades", [])
                        
                        # Walidacja i naprawa ocen
                        validated_grades = []
                        for grade in course["grades"]:
                            if isinstance(grade, dict):
                                grade.setdefault("value", "")
                                grade.setdefault("note", "")
                                grade.setdefault("date", "")
                                validated_grades.append(grade)
                            elif isinstance(grade, str):
                                # Konwersja stringa na słownik
                                logging.warning(f"Konwertuję nieprawidłową ocenę (string): {grade}")
                                validated_grades.append({
                                    "value": grade,
                                    "note": "",
                                    "date": ""
                                })
                            else:
                                logging.error(f"Pominięto nieprawidłowy wpis oceny: {grade}")
                                continue
                        course["grades"] = validated_grades

                    self.save_data()
                    logging.info("Załadowano i zwalidowano dane")
            except Exception as e:
                logging.error(f"Błąd ładowania danych: {e}")
                self.courses = []
                self.user_data = {"name": "", "profile_pic": "", "city": ""}
                self.current_style = "Windows XP"
                QMessageBox.warning(self, "Błąd", "Błąd ładowania danych. Ustawiono domyślne wartości.")
    def show_home_page(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_home_page()

    def show_profile_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_courses_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_grades_page(self):
        self.stacked_widget.setCurrentIndex(3)

    def closeEvent(self, event):
        self.save_data()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CourseManagerApp()
    window.show()
    sys.exit(app.exec_())