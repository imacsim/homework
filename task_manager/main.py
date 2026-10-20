import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit,
    QRadioButton, QButtonGroup, QCheckBox, QPushButton,
    QListWidget, QMessageBox, QDialog
)


class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QPushButton {
                background-color: orange;
                padding: 8px 12px;
            }

            QPushButton:hover {
                background-color: purple;
                color: white;
            }

            QPushButton:disabled {
                background-color: grey;
                color: black;
            }

            QLineEdit, QTextEdit, QListWidget {
                background-color: grey;
                color: white;
            }
        """)

        self.tasks_list = QListWidget()

        self.setWindowTitle("Task Manager")
        self.resize(500, 500)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        self.task_name = QLineEdit()
        self.task_char_count_label = QLabel("Characters: 0")
        self.task_name.textChanged.connect(self.update_char_len)

        self.task_description = QTextEdit()

        task_info_layout = QGridLayout()
        task_info_layout.addWidget(QLabel("Task:"), 0, 0)
        task_info_layout.addWidget(self.task_name, 0, 1)
        task_info_layout.addWidget(QLabel("Description:"), 1, 0)
        task_info_layout.addWidget(self.task_description, 1, 1)
        task_info_layout.addWidget(self.task_char_count_label, 2, 0)
        main_layout.addLayout(task_info_layout)

        low_radio = QRadioButton("Low")
        self.medium_radio = QRadioButton("Medium")
        high_radio = QRadioButton("High")

        self.priority_group = QButtonGroup(self)
        self.priority_group.addButton(low_radio)
        self.priority_group.addButton(self.medium_radio)
        self.priority_group.addButton(high_radio)
        self.medium_radio.setChecked(True)

        priority_layout = QHBoxLayout()
        priority_layout.addWidget(low_radio)
        priority_layout.addWidget(self.medium_radio)
        priority_layout.addWidget(high_radio)
        main_layout.addLayout(priority_layout)

        self.important_checkbox = QCheckBox("Important")
        self.notification_checkbox = QCheckBox("Send notification")

        additional_settings_layout = QHBoxLayout()
        additional_settings_layout.addWidget(self.important_checkbox)
        additional_settings_layout.addWidget(self.notification_checkbox)
        main_layout.addLayout(additional_settings_layout)

        create_task_btn = QPushButton("Create task")
        clear_fields_btn = QPushButton("Clear fields")
        clear_tasks_btn = QPushButton("Clear tasks")

        create_task_btn.clicked.connect(self.create_task)
        clear_fields_btn.clicked.connect(self.clear_form)
        clear_tasks_btn.clicked.connect(self.clear_tasks_list)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(create_task_btn)
        btn_layout.addWidget(clear_fields_btn)
        btn_layout.addWidget(clear_tasks_btn)
        main_layout.addLayout(btn_layout)

        self.delete_task_btn = QPushButton("Delete selected")
        self.delete_task_btn.setEnabled(False)
        self.delete_task_btn.clicked.connect(self.delete_selected_task)
        self.tasks_list.itemSelectionChanged.connect(self.update_delete_button_state)

        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about_dialog)

        extra_buttons_layout = QHBoxLayout()
        extra_buttons_layout.addWidget(self.delete_task_btn)
        extra_buttons_layout.addWidget(about_btn)
        main_layout.addLayout(extra_buttons_layout)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        main_layout.addWidget(QLabel("Result:"))
        main_layout.addWidget(self.result)
        main_layout.addWidget(self.tasks_list)

        self.tasks_count_label = QLabel("Tasks: 0")
        main_layout.addWidget(self.tasks_count_label)

        self.setCentralWidget(central_widget)

    def create_task(self):
        name = self.task_name.text().strip()
        if name == "":
            QMessageBox.warning(
                self,
                "Ошибка ввода",
                "Введите название задачи"
            )
            return

        description = self.task_description.toPlainText()

        selected_radio = self.priority_group.checkedButton()
        if selected_radio is None:
            priority = "Not selected"
        else:
            priority = selected_radio.text()

        important = "Yes" if self.important_checkbox.isChecked() else "No"
        notification = "Yes" if self.notification_checkbox.isChecked() else "No"

        result_string = (
            f"Task: {name}\nDescription: {description}\n\nPriority: {priority}"
            f"\nImportant: {important}\nNotification: {notification}"
        )
        self.tasks_list.addItem(result_string)
        self.result.setPlainText(result_string)
        self.tasks_count_label.setText(f"Tasks: {self.tasks_list.count()}")
        self.clear_form()

    def clear_form(self):
        self.task_name.clear()
        self.task_description.clear()
        self.medium_radio.setChecked(True)
        self.important_checkbox.setChecked(False)
        self.notification_checkbox.setChecked(False)

    def update_char_len(self, text: str):
        self.task_char_count_label.setText(f"Characters: {len(text)}")

    def clear_tasks_list(self):
        answer = QMessageBox.question(
            self,
            "Очистка списка",
            "Удалить все задачи?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.tasks_list.clear()
            self.result.clear()
            self.tasks_count_label.setText("Tasks: 0")
            self.update_delete_button_state()

    def update_delete_button_state(self):
        has_selection = bool(self.tasks_list.selectedItems())
        self.delete_task_btn.setEnabled(has_selection)

    def delete_selected_task(self):
        selected_items = self.tasks_list.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        answer = QMessageBox.question(
            self,
            "Удаление задачи",
            "Удалить выбранную задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        row = self.tasks_list.row(selected_item)
        self.tasks_list.takeItem(row)
        self.tasks_count_label.setText(f"Tasks: {self.tasks_list.count()}")
        self.result.clear()
        self.update_delete_button_state()

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("О программе")

        dialog_layout = QVBoxLayout(dialog)
        info_label = QLabel("Task Manager 2.0\nПриложение для создания задач.")
        dialog_layout.addWidget(info_label)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        dialog_layout.addWidget(close_btn)

        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManagerWindow()
    window.show()
    sys.exit(app.exec())
