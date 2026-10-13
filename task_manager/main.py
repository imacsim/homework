from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit,
    QRadioButton, QButtonGroup, QCheckBox, QPushButton
)


app = QApplication([])
tasks = []

window = QMainWindow()
window.setWindowTitle("Task Manager")
window.resize(500, 500)

central_widget = QWidget()
main_layout = QVBoxLayout(central_widget)

task_name = QLineEdit()
task_description = QTextEdit()

task_info_layout = QGridLayout()
task_info_layout.addWidget(QLabel("Task:"), 0, 0)
task_info_layout.addWidget(task_name, 0, 1)
task_info_layout.addWidget(QLabel("Description:"), 1, 0)
task_info_layout.addWidget(task_description, 1, 1)
main_layout.addLayout(task_info_layout)

low_radio = QRadioButton("Low")
medium_radio = QRadioButton("Medium")
high_radio = QRadioButton("High")

priority_group = QButtonGroup()
priority_group.addButton(low_radio)
priority_group.addButton(medium_radio)
priority_group.addButton(high_radio)
medium_radio.setChecked(True)

priority_layout = QHBoxLayout()
priority_layout.addWidget(low_radio)
priority_layout.addWidget(medium_radio)
priority_layout.addWidget(high_radio)
main_layout.addLayout(priority_layout)

important_checkbox = QCheckBox("Important")
notification_checkbox = QCheckBox("Send notification")

additional_settings_layout = QHBoxLayout()
additional_settings_layout.addWidget(important_checkbox)
additional_settings_layout.addWidget(notification_checkbox)
main_layout.addLayout(additional_settings_layout)


def create_task():
    name = task_name.text()
    description = task_description.toPlainText()

    selected_radio = priority_group.checkedButton()
    if selected_radio is None:
        priority = "Not selected"
    else:
        priority = selected_radio.text()

    important = "Yes" if important_checkbox.isChecked() else "No"
    notification = "Yes" if notification_checkbox.isChecked() else "No"

    result_string = (
        f"Task: {name}\nDescription: {description}\n\nPriority: {priority}"
        f"\nImportant: {important}\nNotification: {notification}"
    )
    tasks.append(result_string)
    result.setPlainText(f"{result_string}\n\nCreated tasks: {len(tasks)}")


def clear_form():
    task_name.clear()
    task_description.clear()
    medium_radio.setChecked(True)
    important_checkbox.setChecked(False)
    notification_checkbox.setChecked(False)


create_task_btn = QPushButton("Create task")
clear_btn = QPushButton("Clear")
create_task_btn.clicked.connect(create_task)
clear_btn.clicked.connect(clear_form)

btn_layout = QHBoxLayout()
btn_layout.addWidget(create_task_btn)
btn_layout.addWidget(clear_btn)
main_layout.addLayout(btn_layout)

result = QTextEdit()
result.setReadOnly(True)
main_layout.addWidget(QLabel("Result:"))
main_layout.addWidget(result)

window.setCentralWidget(central_widget)
window.show()
app.exec()
