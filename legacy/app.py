import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, 
                             QCheckBox, QMessageBox, QListWidgetItem, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class CourseManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Czy powinienem iść na zajęcia?")
        self.setGeometry(100, 100, 800, 600)
        
        # Inicjalizacja danych
        self.courses = []
        self.current_style = "Windows XP"
        self.load_data()
        
        # Główne widgety
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Inicjalizacja interfejsu
        self.init_ui()
        self.apply_style(self.current_style)
        
    def init_ui(self):
        # Style selector
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Windows XP", "Sakura Pink"])
        self.style_combo.setCurrentText(self.current_style)
        self.style_combo.currentTextChanged.connect(self.apply_style)
        self.main_layout.addWidget(self.style_combo)
        
        # Course form
        self.course_form = QWidget()
        self.course_form_layout = QVBoxLayout()
        self.course_form.setLayout(self.course_form_layout)
        
        # Course name
        self.name_label = QLabel("Nazwa przedmiotu:")
        self.name_input = QLineEdit()
        self.course_form_layout.addWidget(self.name_label)
        self.course_form_layout.addWidget(self.name_input)
        
        # Course days
        self.days_label = QLabel("Dni zajęć (np. pon, śr):")
        self.days_input = QLineEdit()
        self.course_form_layout.addWidget(self.days_label)
        self.course_form_layout.addWidget(self.days_input)
        
        # Max absences
        self.absences_label = QLabel("Maksymalna liczba nieobecności:")
        self.absences_input = QSpinBox()
        self.absences_input.setMinimum(0)
        self.absences_input.setMaximum(100)
        self.course_form_layout.addWidget(self.absences_label)
        self.course_form_layout.addWidget(self.absences_input)
        
        # Grades
        self.grades_label = QLabel("Oceny (oddzielone przecinkami):")
        self.grades_input = QLineEdit()
        self.course_form_layout.addWidget(self.grades_label)
        self.course_form_layout.addWidget(self.grades_input)
        
        # Mandatory checkbox
        self.mandatory_check = QCheckBox("Przedmiot obowiązkowy")
        self.course_form_layout.addWidget(self.mandatory_check)
        
        # Add course button
        self.add_course_btn = QPushButton("Dodaj przedmiot")
        self.add_course_btn.clicked.connect(self.add_course)
        self.course_form_layout.addWidget(self.add_course_btn)
        
        self.main_layout.addWidget(self.course_form)
        
        # Courses list
        self.courses_list = QListWidget()
        self.courses_list.itemClicked.connect(self.show_course_details)
        self.main_layout.addWidget(self.courses_list)
        
        # Mood and weather section
        self.analysis_widget = QWidget()
        self.analysis_layout = QVBoxLayout()
        self.analysis_widget.setLayout(self.analysis_layout)
        
        # Mood
        self.mood_label = QLabel("Twoje samopoczucie (1-10):")
        self.mood_input = QSpinBox()
        self.mood_input.setMinimum(1)
        self.mood_input.setMaximum(10)
        self.analysis_layout.addWidget(self.mood_label)
        self.analysis_layout.addWidget(self.mood_input)
        
        # Weather
        self.weather_label = QLabel("Miasto dla prognozy pogody:")
        self.weather_input = QLineEdit()
        self.weather_btn = QPushButton("Sprawdź pogodę")
        self.weather_btn.clicked.connect(self.check_weather)
        
        weather_hbox = QHBoxLayout()
        weather_hbox.addWidget(self.weather_input)
        weather_hbox.addWidget(self.weather_btn)
        
        self.analysis_layout.addWidget(self.weather_label)
        self.analysis_layout.addLayout(weather_hbox)
        
        # Analyze button
        self.analyze_btn = QPushButton("Czy powinienem iść na zajęcia?")
        self.analyze_btn.clicked.connect(self.analyze_attendance)
        self.analysis_layout.addWidget(self.analyze_btn)
        
        self.main_layout.addWidget(self.analysis_widget)
        
        # Update courses list
        self.update_courses_list()
        
    def add_course(self):
        name = self.name_input.text().strip()
        days = self.days_input.text().strip()
        max_absences = self.absences_input.value()
        grades = [g.strip() for g in self.grades_input.text().split(",") if g.strip()]
        mandatory = self.mandatory_check.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Błąd", "Nazwa przedmiotu jest wymagana!")
            return
            
        course = {
            "name": name,
            "days": days,
            "max_absences": max_absences,
            "current_absences": 0,
            "grades": grades,
            "mandatory": mandatory
        }
        
        self.courses.append(course)
        self.save_data()
        self.update_courses_list()
        
        # Clear form
        self.name_input.clear()
        self.days_input.clear()
        self.absences_input.setValue(0)
        self.grades_input.clear()
        self.mandatory_check.setChecked(False)
        
    def update_courses_list(self):
        self.courses_list.clear()
        for course in self.courses:
            item = QListWidgetItem(course["name"])
            item.setData(Qt.UserRole, course)
            self.courses_list.addItem(item)
            
    def show_course_details(self, item):
        course = item.data(Qt.UserRole)
        details = (
            f"Nazwa: {course['name']}\n"
            f"Dni zajęć: {course['days']}\n"
            f"Nieobecności: {course['current_absences']}/{course['max_absences']}\n"
            f"Oceny: {', '.join(course['grades']) if course['grades'] else 'Brak'}\n"
            f"Obowiązkowy: {'Tak' if course['mandatory'] else 'Nie'}"
        )
        QMessageBox.information(self, "Szczegóły przedmiotu", details)
        
    def check_weather(self):
        city = self.weather_input.text().strip()
        if not city:
            QMessageBox.warning(self, "Błąd", "Wprowadź nazwę miasta!")
            return
            
        # Symulacja sprawdzania pogody
        # W rzeczywistości można by tu użyć API pogodowego
        weather_info = f"Symulacja: W mieście {city} pogoda jest umiarkowana, 18°C, lekki wiatr."
        QMessageBox.information(self, "Prognoza pogody", weather_info)
        
    def analyze_attendance(self):
        if not self.courses:
            QMessageBox.warning(self, "Błąd", "Najpierw dodaj jakieś przedmioty!")
            return
            
        mood = self.mood_input.value()
        analysis = ""
        
        # Analiza samopoczucia
        if mood < 5:
            analysis += "Twoje samopoczucie jest słabe. Możesz rozważyć pozostanie w domu, "
            analysis += "ale jeśli przedmioty są obowiązkowe, spróbuj się zmusić.\n\n"
        else:
            analysis += "Twoje samopoczucie jest w porządku. Powinieneś być w stanie pójść na zajęcia.\n\n"
            
        # Analiza przedmiotów
        for course in self.courses:
            course_analysis = f"Przedmiot: {course['name']}\n"
            
            if course['mandatory']:
                course_analysis += "- Obowiązkowy: Musisz iść na zajęcia\n"
            else:
                course_analysis += "- Nieobowiązkowy: Możesz rozważyć nieobecność\n"
                
            # Analiza nieobecności
            absence_percentage = (course['current_absences'] / course['max_absences']) * 100 if course['max_absences'] > 0 else 0
            if absence_percentage > 80:
                course_analysis += "- Uwaga! Masz już prawie wyczerpany limit nieobecności\n"
            elif absence_percentage > 50:
                course_analysis += "- Masz wykorzystaną ponad połowę nieobecności\n"
            else:
                course_analysis += "- Masz jeszcze sporo nieobecności do wykorzystania\n"
                
            # Analiza ocen
            if course['grades']:
                numeric_grades = []
                for grade in course['grades']:
                    try:
                        numeric_grade = float(grade)
                        numeric_grades.append(numeric_grade)
                    except ValueError:
                        pass
                        
                if numeric_grades:
                    avg_grade = sum(numeric_grades) / len(numeric_grades)
                    if avg_grade >= 4.0:
                        course_analysis += "- Twoje oceny są dobre, możesz sobie pozwolić na nieobecność\n"
                    elif avg_grade >= 3.0:
                        course_analysis += "- Twoje oceny są średnie, lepiej idź na zajęcia\n"
                    else:
                        course_analysis += "- Twoje oceny są słabe, koniecznie idź na zajęcia\n"
                else:
                    course_analysis += "- Brak ocen liczbowych do analizy\n"
            else:
                course_analysis += "- Brak ocen do analizy\n"
                
            analysis += course_analysis + "\n"
            
        QMessageBox.information(self, "Analiza", analysis)
        
    def apply_style(self, style_name):
        self.current_style = style_name
        
        if style_name == "Sakura Pink":
            # Sakura Pink theme
            bg_color = "#ffe4ec"  # Różowe tło
            text_color = "#5a0032"  # Ciemny róż/fiolet
            button_color = "#ffb6c1"  # Jasny róż
            button_text = "#5a0032"
            list_color = "#ffd1dc"  # Średni róż
            
            style = f"""
                QWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: Arial;
                }}
                QPushButton {{
                    background-color: {button_color};
                    color: {button_text};
                    border: 1px solid {text_color};
                    padding: 5px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: #ff8fab;
                }}
                QLineEdit, QSpinBox, QComboBox {{
                    background-color: white;
                    color: {text_color};
                    border: 1px solid {text_color};
                }}
                QListWidget {{
                    background-color: {list_color};
                    color: {text_color};
                }}
                QCheckBox::indicator {{
                    width: 15px;
                    height: 15px;
                }}
            """
        else:  # Windows XP
            # Windows XP theme
            bg_color = "#e4ecf5"  # Niebiesko-szare tło
            text_color = "#003366"  # Granatowy tekst
            button_color = "#d7e3f2"  # Jasnoniebieski
            button_text = "#003366"
            list_color = "#c6d9f1"  # Średni niebieski
            
            style = f"""
                QWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: Arial;
                }}
                QPushButton {{
                    background-color: {button_color};
                    color: {button_text};
                    border: 1px solid {text_color};
                    padding: 5px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: #b8cfea;
                }}
                QLineEdit, QSpinBox, QComboBox {{
                    background-color: white;
                    color: {text_color};
                    border: 1px solid {text_color};
                }}
                QListWidget {{
                    background-color: {list_color};
                    color: {text_color};
                }}
                QCheckBox::indicator {{
                    width: 15px;
                    height: 15px;
                }}
            """
            
        self.setStyleSheet(style)
        
    def save_data(self):
        data = {
            "courses": self.courses,
            "style": self.current_style
        }
        with open("course_data.json", "w") as f:
            json.dump(data, f)
            
    def load_data(self):
        if os.path.exists("course_data.json"):
            try:
                with open("course_data.json", "r") as f:
                    data = json.load(f)
                    self.courses = data.get("courses", [])
                    self.current_style = data.get("style", "Windows XP")
            except:
                self.courses = []
                self.current_style = "Windows XP"
                
    def closeEvent(self, event):
        self.save_data()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CourseManagerApp()
    window.show()
    sys.exit(app.exec_())