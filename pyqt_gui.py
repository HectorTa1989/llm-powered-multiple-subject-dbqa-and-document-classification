from PyQt5 import QtCore, QtGui, QtWidgets
from src import qa_api, db_retriever, update_requests, classification_api
import time

class Worker(QtCore.QObject):
    ask_question_finished = QtCore.pyqtSignal(str)
    generate_documents_finished = QtCore.pyqtSignal(dict)
    save_documents_finished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)

    def ask_question(self, question, topic, subject_name):
        # time the process
        start_time = time.time()
        # get answer
        answer, cost = qa_api.ask_question(question, topic, subject_name)
        # get time
        end_time = time.time()
        time_taken = end_time - start_time
        final_answer = answer + "\n\n" + "Time: " + str(time_taken)
        self.ask_question_finished.emit(final_answer)

    def generate_documents(self, topic, path):
        # generate documents
        doc_subject_dict = classification_api.generate_documents(topic, path)
        if doc_subject_dict is None:
            doc_subject_dict = {}
            doc_subject_dict["error"] = True
        self.generate_documents_finished.emit(doc_subject_dict)

    def save_documents(self, topic, path, file_dict):
        classification_api.save_documents(topic, path, file_dict)
        self.save_documents_finished.emit()


class Runnable(QtCore.QRunnable):
    def __init__(self, worker, question, topic, subject_name= "All Subjects"):
        super(Runnable, self).__init__()
        self.worker = worker
        self.question = question
        self.subject_name = subject_name
        self.topic = topic

    def run(self):
        self.worker.ask_question(self.question, self.topic, self.subject_name)

# runnable for document classification
class Runnable2(QtCore.QRunnable):
    def __init__(self, worker, topic, path):
        super(Runnable2, self).__init__()
        self.worker = worker
        self.topic = topic
        self.path = path

    def run(self):
        self.worker.generate_documents(self.topic, self.path)

# runnable for saving documents
class Runnable3(QtCore.QRunnable):
    def __init__(self, worker, topic, path, file_dict):
        super(Runnable3, self).__init__()
        self.worker = worker
        self.topic = topic
        self.file_dict = file_dict
        self.path = path

    def run(self):
        self.worker.save_documents(self.topic, self.path, self.file_dict)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1197, 869)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.general_page_frame = QtWidgets.QFrame(self.centralwidget)
        self.general_page_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.general_page_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.general_page_frame.setObjectName("general_page_frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.general_page_frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.stackedWidget = QtWidgets.QStackedWidget(self.general_page_frame)
        self.stackedWidget.setStyleSheet("background-color: rgb(170, 170, 255);")
        self.stackedWidget.setObjectName("stackedWidget")
        self.main_page = QtWidgets.QWidget()
        self.main_page.setObjectName("main_page")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.main_page)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.classification_button = QtWidgets.QPushButton(self.main_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classification_button.sizePolicy().hasHeightForWidth())
        self.classification_button.setSizePolicy(sizePolicy)
        self.classification_button.setMaximumSize(QtCore.QSize(200, 200))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.classification_button.setFont(font)
        self.classification_button.setTabletTracking(False)
        self.classification_button.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.classification_button.setStyleSheet("background-color: rgb(112, 150, 255);")
        self.classification_button.setObjectName("classification_button")
        self.horizontalLayout_3.addWidget(self.classification_button)
        self.dbqa_button = QtWidgets.QPushButton(self.main_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbqa_button.sizePolicy().hasHeightForWidth())
        self.dbqa_button.setSizePolicy(sizePolicy)
        self.dbqa_button.setMaximumSize(QtCore.QSize(200, 200))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.dbqa_button.setFont(font)
        self.dbqa_button.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.dbqa_button.setStyleSheet("background-color: rgb(112, 150, 255);")
        self.dbqa_button.setObjectName("dbqa_button")
        self.horizontalLayout_3.addWidget(self.dbqa_button)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.stackedWidget.addWidget(self.main_page)
        self.dbqa_page = QtWidgets.QWidget()
        self.dbqa_page.setStyleSheet("")
        self.dbqa_page.setObjectName("dbqa_page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dbqa_page)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_menu_button_3 = QtWidgets.QPushButton(self.dbqa_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_menu_button_3.sizePolicy().hasHeightForWidth())
        self.main_menu_button_3.setSizePolicy(sizePolicy)
        self.main_menu_button_3.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.main_menu_button_3.setFont(font)
        self.main_menu_button_3.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.main_menu_button_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.main_menu_button_3.setStyleSheet("background-color: rgb(234, 255, 189);")
        self.main_menu_button_3.setObjectName("main_menu_button_3")
        self.verticalLayout.addWidget(self.main_menu_button_3)
        self.topic_subject_frame = QtWidgets.QFrame(self.dbqa_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topic_subject_frame.sizePolicy().hasHeightForWidth())
        self.topic_subject_frame.setSizePolicy(sizePolicy)
        self.topic_subject_frame.setMaximumSize(QtCore.QSize(1000000, 100))
        self.topic_subject_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.topic_subject_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.topic_subject_frame.setObjectName("topic_subject_frame")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.topic_subject_frame)
        self.verticalLayout_7.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.topic_subject_layout = QtWidgets.QVBoxLayout()
        self.topic_subject_layout.setContentsMargins(-1, -1, -1, 0)
        self.topic_subject_layout.setObjectName("topic_subject_layout")
        self.topic_subject_text_layout = QtWidgets.QHBoxLayout()
        self.topic_subject_text_layout.setSpacing(50)
        self.topic_subject_text_layout.setObjectName("topic_subject_text_layout")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.topic_subject_frame)
        self.textBrowser_2.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.textBrowser_2.setFont(font)
        self.textBrowser_2.setStyleSheet("background-color: rgb(255, 242, 210);")
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.topic_subject_text_layout.addWidget(self.textBrowser_2)
        self.textBrowser = QtWidgets.QTextBrowser(self.topic_subject_frame)
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textBrowser.setFont(font)
        self.textBrowser.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.textBrowser.setStyleSheet("background-color: rgb(255, 242, 210);")
        self.textBrowser.setObjectName("textBrowser")
        self.topic_subject_text_layout.addWidget(self.textBrowser)
        self.topic_subject_layout.addLayout(self.topic_subject_text_layout)
        self.topic_subject_combo_frame = QtWidgets.QHBoxLayout()
        self.topic_subject_combo_frame.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.topic_subject_combo_frame.setContentsMargins(-1, -1, 0, -1)
        self.topic_subject_combo_frame.setSpacing(30)
        self.topic_subject_combo_frame.setObjectName("topic_subject_combo_frame")
        self.topics_combo_box = QtWidgets.QComboBox(self.topic_subject_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topics_combo_box.sizePolicy().hasHeightForWidth())
        self.topics_combo_box.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.topics_combo_box.setFont(font)
        self.topics_combo_box.setEditable(False)
        self.topics_combo_box.setObjectName("topics_combo_box")
        self.topics_combo_box.addItem("")
        self.topic_subject_combo_frame.addWidget(self.topics_combo_box)
        self.subjects_combo_box = QtWidgets.QComboBox(self.topic_subject_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.subjects_combo_box.sizePolicy().hasHeightForWidth())
        self.subjects_combo_box.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.subjects_combo_box.setFont(font)
        self.subjects_combo_box.setObjectName("subjects_combo_box")
        self.subjects_combo_box.addItem("")
        self.topic_subject_combo_frame.addWidget(self.subjects_combo_box)
        self.topic_subject_layout.addLayout(self.topic_subject_combo_frame)
        self.verticalLayout_7.addLayout(self.topic_subject_layout)
        self.verticalLayout.addWidget(self.topic_subject_frame)
        self.qa_answer_p1 = QtWidgets.QTextBrowser(self.dbqa_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qa_answer_p1.sizePolicy().hasHeightForWidth())
        self.qa_answer_p1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.qa_answer_p1.setFont(font)
        self.qa_answer_p1.setStyleSheet("background-color: rgb(228, 255, 252);")
        self.qa_answer_p1.setObjectName("qa_answer_p1")
        self.verticalLayout.addWidget(self.qa_answer_p1)
        self.query_frame = QtWidgets.QFrame(self.dbqa_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.query_frame.sizePolicy().hasHeightForWidth())
        self.query_frame.setSizePolicy(sizePolicy)
        self.query_frame.setMaximumSize(QtCore.QSize(10000, 100))
        self.query_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.query_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.query_frame.setObjectName("query_frame")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.query_frame)
        self.horizontalLayout_6.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.question_button_layout = QtWidgets.QHBoxLayout()
        self.question_button_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.question_button_layout.setObjectName("question_button_layout")
        self.qa_button = QtWidgets.QPushButton(self.query_frame)
        self.qa_button.setMaximumSize(QtCore.QSize(16777215, 30))
        self.qa_button.setMouseTracking(False)
        self.qa_button.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.qa_button.setAutoFillBackground(False)
        self.qa_button.setStyleSheet("background-color: rgb(255, 85, 0);")
        self.qa_button.setText("")
        self.qa_button.setAutoDefault(False)
        self.qa_button.setDefault(True)
        self.qa_button.setFlat(False)
        self.qa_button.setObjectName("qa_button")
        self.question_button_layout.addWidget(self.qa_button)
        self.query_text = QtWidgets.QPlainTextEdit(self.query_frame)
        self.query_text.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.query_text.setFont(font)
        self.query_text.setStyleSheet("background-color: rgb(144, 144, 144);")
        self.query_text.setPlainText("")
        self.query_text.setObjectName("query_text")
        self.question_button_layout.addWidget(self.query_text)
        self.horizontalLayout_6.addLayout(self.question_button_layout)
        self.verticalLayout.addWidget(self.query_frame)
        self.stackedWidget.addWidget(self.dbqa_page)
        self.classification_page = QtWidgets.QWidget()
        self.classification_page.setObjectName("classification_page")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.classification_page)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.classification_layout_1 = QtWidgets.QVBoxLayout()
        self.classification_layout_1.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.classification_layout_1.setContentsMargins(-1, -1, -1, 0)
        self.classification_layout_1.setObjectName("classification_layout_1")
        self.classification_frame_1 = QtWidgets.QFrame(self.classification_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classification_frame_1.sizePolicy().hasHeightForWidth())
        self.classification_frame_1.setSizePolicy(sizePolicy)
        self.classification_frame_1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.classification_frame_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.classification_frame_1.setObjectName("classification_frame_1")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.classification_frame_1)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.path_topic_frame = QtWidgets.QFrame(self.classification_frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.path_topic_frame.sizePolicy().hasHeightForWidth())
        self.path_topic_frame.setSizePolicy(sizePolicy)
        self.path_topic_frame.setMaximumSize(QtCore.QSize(16777215, 100))
        self.path_topic_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.path_topic_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.path_topic_frame.setObjectName("path_topic_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.path_topic_frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.path_topic_input_frame = QtWidgets.QFrame(self.path_topic_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.path_topic_input_frame.sizePolicy().hasHeightForWidth())
        self.path_topic_input_frame.setSizePolicy(sizePolicy)
        self.path_topic_input_frame.setMaximumSize(QtCore.QSize(300, 150))
        self.path_topic_input_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.path_topic_input_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.path_topic_input_frame.setObjectName("path_topic_input_frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.path_topic_input_frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.textBrowser_3 = QtWidgets.QTextBrowser(self.path_topic_input_frame)
        self.textBrowser_3.setMaximumSize(QtCore.QSize(400, 40))
        self.textBrowser_3.setStyleSheet("background-color: rgb(85, 170, 255);")
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.verticalLayout_9.addWidget(self.textBrowser_3)
        self.file_explorer_button = QtWidgets.QPushButton(self.path_topic_input_frame)
        self.file_explorer_button.setMaximumSize(QtCore.QSize(300, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.file_explorer_button.setFont(font)
        self.file_explorer_button.setStyleSheet("background-color: rgb(170, 170, 127);")
        self.file_explorer_button.setObjectName("file_explorer_button")
        self.verticalLayout_9.addWidget(self.file_explorer_button)
        self.verticalLayout_6.addLayout(self.verticalLayout_9)
        self.horizontalLayout.addWidget(self.path_topic_input_frame)
        self.path_topic_text_frame = QtWidgets.QFrame(self.path_topic_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.path_topic_text_frame.sizePolicy().hasHeightForWidth())
        self.path_topic_text_frame.setSizePolicy(sizePolicy)
        self.path_topic_text_frame.setMaximumSize(QtCore.QSize(300, 150))
        self.path_topic_text_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.path_topic_text_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.path_topic_text_frame.setObjectName("path_topic_text_frame")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.path_topic_text_frame)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.textBrowser_4 = QtWidgets.QTextBrowser(self.path_topic_text_frame)
        self.textBrowser_4.setMaximumSize(QtCore.QSize(300, 40))
        self.textBrowser_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.textBrowser_4.setStyleSheet("background-color: rgb(85, 170, 255);")
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.verticalLayout_13.addWidget(self.textBrowser_4)
        self.classification_topic_text_1 = QtWidgets.QPlainTextEdit(self.path_topic_text_frame)
        self.classification_topic_text_1.setMaximumSize(QtCore.QSize(300, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.classification_topic_text_1.setFont(font)
        self.classification_topic_text_1.setStyleSheet("background-color: rgb(255, 240, 247);")
        self.classification_topic_text_1.setPlainText("")
        self.classification_topic_text_1.setObjectName("classification_topic_text_1")
        self.verticalLayout_13.addWidget(self.classification_topic_text_1)
        self.verticalLayout_11.addLayout(self.verticalLayout_13)
        self.horizontalLayout.addWidget(self.path_topic_text_frame)
        self.classification_generate_button = QtWidgets.QPushButton(self.path_topic_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classification_generate_button.sizePolicy().hasHeightForWidth())
        self.classification_generate_button.setSizePolicy(sizePolicy)
        self.classification_generate_button.setMaximumSize(QtCore.QSize(100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.classification_generate_button.setFont(font)
        self.classification_generate_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.classification_generate_button.setStyleSheet("background-color: rgb(170, 255, 127);")
        self.classification_generate_button.setObjectName("classification_generate_button")
        self.horizontalLayout.addWidget(self.classification_generate_button)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_12.addWidget(self.path_topic_frame)
        self.document_list_frame = QtWidgets.QFrame(self.classification_frame_1)
        self.document_list_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.document_list_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.document_list_frame.setObjectName("document_list_frame")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.document_list_frame)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.document_list_layout = QtWidgets.QVBoxLayout()
        self.document_list_layout.setObjectName("document_list_layout")
        self.generated_document_list = QtWidgets.QListWidget(self.document_list_frame)
        self.generated_document_list.setStyleSheet("background-color: rgb(210, 226, 255);")
        self.generated_document_list.setObjectName("generated_document_list")
        self.document_list_layout.addWidget(self.generated_document_list)
        self.verticalLayout_14.addLayout(self.document_list_layout)
        self.verticalLayout_12.addWidget(self.document_list_frame)
        self.classification_buttons_frame = QtWidgets.QFrame(self.classification_frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classification_buttons_frame.sizePolicy().hasHeightForWidth())
        self.classification_buttons_frame.setSizePolicy(sizePolicy)
        self.classification_buttons_frame.setMaximumSize(QtCore.QSize(16777215, 60))
        self.classification_buttons_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.classification_buttons_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.classification_buttons_frame.setObjectName("classification_buttons_frame")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.classification_buttons_frame)
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.classification_buttons_layout = QtWidgets.QHBoxLayout()
        self.classification_buttons_layout.setSpacing(50)
        self.classification_buttons_layout.setObjectName("classification_buttons_layout")
        self.accept_generation_button = QtWidgets.QPushButton(self.classification_buttons_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accept_generation_button.sizePolicy().hasHeightForWidth())
        self.accept_generation_button.setSizePolicy(sizePolicy)
        self.accept_generation_button.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.accept_generation_button.setFont(font)
        self.accept_generation_button.setStyleSheet("background-color: rgb(170, 255, 127);")
        self.accept_generation_button.setObjectName("accept_generation_button")
        self.classification_buttons_layout.addWidget(self.accept_generation_button)
        self.regenerate_button = QtWidgets.QPushButton(self.classification_buttons_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.regenerate_button.sizePolicy().hasHeightForWidth())
        self.regenerate_button.setSizePolicy(sizePolicy)
        self.regenerate_button.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.regenerate_button.setFont(font)
        self.regenerate_button.setStyleSheet("background-color: rgb(170, 102, 93);")
        self.regenerate_button.setObjectName("regenerate_button")
        self.classification_buttons_layout.addWidget(self.regenerate_button)
        self.horizontalLayout_11.addLayout(self.classification_buttons_layout)
        self.verticalLayout_12.addWidget(self.classification_buttons_frame)
        self.classification_layout_1.addWidget(self.classification_frame_1)
        self.menu_button_4 = QtWidgets.QPushButton(self.classification_page)
        self.menu_button_4.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menu_button_4.sizePolicy().hasHeightForWidth())
        self.menu_button_4.setSizePolicy(sizePolicy)
        self.menu_button_4.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.menu_button_4.setFont(font)
        self.menu_button_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.menu_button_4.setStyleSheet("background-color: rgb(234, 255, 189);")
        self.menu_button_4.setObjectName("menu_button_4")
        self.classification_layout_1.addWidget(self.menu_button_4)
        self.verticalLayout_10.addLayout(self.classification_layout_1)
        self.stackedWidget.addWidget(self.classification_page)
        self.verticalLayout_5.addWidget(self.stackedWidget)
        self.verticalLayout_4.addWidget(self.general_page_frame)
        self.verticalLayout_2.addLayout(self.verticalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1197, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.classification_button.setText(_translate("MainWindow", "Document Classification"))
        self.dbqa_button.setText(_translate("MainWindow", "Document QA"))
        self.main_menu_button_3.setText(_translate("MainWindow", "Main Menu"))
        self.textBrowser_2.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Topic</span></p></body></html>"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Subject (s)</p></body></html>"))
        self.topics_combo_box.setItemText(0, _translate("MainWindow", "Not Selected"))
        self.subjects_combo_box.setItemText(0, _translate("MainWindow", "All Subjects"))
        self.qa_answer_p1.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Times New Roman\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">Answer</span></p></body></html>"))
        self.textBrowser_3.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Path</span></p></body></html>"))
        self.file_explorer_button.setText(_translate("MainWindow", "Browse"))
        self.textBrowser_4.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Topic</span></p></body></html>"))
        self.classification_generate_button.setText(_translate("MainWindow", "Generate"))
        self.accept_generation_button.setText(_translate("MainWindow", "Accept"))
        self.regenerate_button.setText(_translate("MainWindow", "Try Again"))
        self.menu_button_4.setText(_translate("MainWindow", "Main Menu"))

        # additions

        # variables
        self.accepted_file_dict = {}

        self.accept_connected = False
        self.regenerate_connected = False

        # set classification path
        self.classification_path = ""

        # set button actions
        self.classification_button.clicked.connect(self.classification_button_clicked)
        self.dbqa_button.clicked.connect(self.dbqa_button_clicked)
        self.main_menu_button_3.clicked.connect(self.main_menu_button_clicked)
        self.menu_button_4.clicked.connect(self.main_menu_button_clicked)
        self.classification_generate_button.clicked.connect(self.classification_generate_button_clicked)
        self.accept_generation_button.clicked.connect(self.accept_generation_button_clicked)
        self.regenerate_button.clicked.connect(self.classification_generate_button_clicked)
        self.file_explorer_button.clicked.connect(self.file_explorer_button_clicked)
        # dbqa button
        self.qa_button.clicked.connect(self.qa_button_clicked)

        # retrieve all topics
        topics_arr = update_requests.get_all_topics_str()

        # add topics to the combo box
        self.topics_combo_box.addItems(topics_arr)

        # add action to the combo box
        self.topics_combo_box.currentIndexChanged.connect(self.topics_combo_box_changed)

        # set thread
        self.worker = Worker()
        self.worker.ask_question_finished.connect(self.handle_ask_question_worker_finished)
        self.worker.generate_documents_finished.connect(self.handle_generate_documents_worker_finished)
        self.worker.save_documents_finished.connect(self.handle_save_documents_worker_finished)

    # additions
    def classification_button_clicked(self):
        self.stackedWidget.setCurrentIndex(2)

        # visible generate button
        self.classification_generate_button.show()

        # clear the list
        self.generated_document_list.clear()

        # clear text fields
        self.classification_topic_text_1.clear()

        # clear the path
        self.classification_path = ""

        # hide accept and regenerate buttons
        self.accept_generation_button.hide()
        self.regenerate_button.hide()

    def accept_generation_button_clicked(self):

        
        topic = self.classification_topic_text_1.toPlainText()

        path = self.classification_path
        
        # check if the topic or path is empty
        if topic == "" or path == "":
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Please fill the topic and path fields!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            return
        

        # get the dictionary of documents and subjects from checkbox
        file_dict = {}
        for i in range(self.generated_document_list.count()):
            item = self.generated_document_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                file_dict[item.text()] = self.accepted_file_dict[item.text()]
        print("dict: ")
        print(file_dict)      
        
        # if selected documents is empty warn the user, pop up a message box
        if len(file_dict) == 0:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Please select at least one document!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            return
        
        # if selected document number is more than 16 warn the user, pop up a message box
        if len(file_dict) > 16:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Limit is 16!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            return
        
        # disable ui
        self.disable_ui()

        # call the thread
        runnable = Runnable3(self.worker, topic, path, file_dict)
        QtCore.QThreadPool.globalInstance().start(runnable)

    def dbqa_button_clicked(self):
        # update the combo box
        self.topics_combo_box_update()
        self.stackedWidget.setCurrentIndex(1)

        # clear the text
        self.qa_answer_p1.clear()
        self.query_text.clear()
        

    def main_menu_button_clicked(self):
        self.stackedWidget.setCurrentIndex(0)

    def qa_button_clicked(self):

        # remove leading and trailing spaces
        self.query_text.setPlainText(self.query_text.toPlainText().strip())

        # check if the query is empty
        if self.query_text.toPlainText() == "":
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Please enter a question!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            return

        # get the question
        question = self.query_text.toPlainText()

        # disable ui
        self.disable_ui()

        # set the text browser
        self.qa_answer_p1.setText("Generating answer...")

        # get the document name
        topic = self.topics_combo_box.currentText()

        # get the subject
        subject = self.subjects_combo_box.currentText()

        # if topic is not selected warn the user, pop up a message box
        if topic == "Not Selected":
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Please select a topic!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            self.qa_answer_p1.clear()
            msg.exec_()

            # enable ui
            self.enable_ui()
            return
        
        # create a QRunnable and start the task in a separate thread
        if subject == "All Subjects":
            runnable = Runnable(self.worker, question, topic)
        else:
            runnable = Runnable(self.worker, question, topic, subject)

        QtCore.QThreadPool.globalInstance().start(runnable)

    def topics_combo_box_update(self):
        # get all topics
        topics_arr = update_requests.get_all_topics_str()

        # clear the combo box
        self.topics_combo_box.clear()

        # add all topics
        self.topics_combo_box.addItem("Not Selected")

        # add the topics
        self.topics_combo_box.addItems(topics_arr)

        # set the first item as current
        self.topics_combo_box.setCurrentIndex(0)

    def classification_generate_button_clicked(self):
        topic = self.classification_topic_text_1.toPlainText()

        # remove leading and trailing spaces
        topic = topic.strip()

        # get the path
        path = self.classification_path
        
        # check if the topic or path is empty
        if topic == "" or path == "":
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Please fill the topic and and select the directory path")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            return
        
        # disable ui
        self.disable_ui()

        # call the thread
        runnable = Runnable2(self.worker, topic, path)
        QtCore.QThreadPool.globalInstance().start(runnable)

    def file_explorer_button_clicked(self):
        # open the file explorer
        path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)
        self.classification_path = path

    def handle_ask_question_worker_finished(self, answer):
        # set the answer
        self.qa_answer_p1.setText(answer)

        # enable ui
        self.enable_ui()

    def handle_generate_documents_worker_finished(self, doc_subject_dict):
        
        # check error
        if doc_subject_dict is None or doc_subject_dict.get("error") is True:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Please fill the path field correctly!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            self.enable_ui()
            return
        # generated_documents = ["doc1", "doc2", "doc3"]
        generated_documents = list(doc_subject_dict.keys())
        # clear the list
        self.generated_document_list.clear()

        # add documents as checkboxes
        for document in generated_documents:
            item = QtWidgets.QListWidgetItem(document)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.generated_document_list.addItem(item)

        # set the dictionary
        self.accepted_file_dict = doc_subject_dict

        # hide the generate button
        self.classification_generate_button.hide()

        if len(generated_documents) != 0:
            # visible accept and regenerate buttons
            self.accept_generation_button.show()

        self.regenerate_button.show()

        self.enable_ui()


    def handle_save_documents_worker_finished(self):
        # inform about the generation
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Information")
        msg.setText("Documents are classified!")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.exec_()

        # clear the dictionary
        self.accepted_file_dict.clear()

        # clear list, topic and path
        self.classification_topic_text_1.clear()

        self.generated_document_list.clear()

        # visible generate button
        self.classification_generate_button.show()

        # hide accept and regenerate buttons
        self.accept_generation_button.hide()
        self.regenerate_button.hide()

        # enable ui
        self.enable_ui()

    def disable_ui(self):
        self.qa_button.setEnabled(False)
        self.query_text.setEnabled(False)
        self.main_menu_button_3.setEnabled(False)
        self.topics_combo_box.setEnabled(False)
        self.subjects_combo_box.setEnabled(False)
        self.classification_generate_button.setEnabled(False)
        self.accept_generation_button.setEnabled(False)
        self.regenerate_button.setEnabled(False)
        self.classification_topic_text_1.setEnabled(False)
        self.file_explorer_button.setEnabled(False)
        self.generated_document_list.setEnabled(False)
        self.menu_button_4.setEnabled(False)

    def enable_ui(self):
        self.qa_button.setEnabled(True)
        self.query_text.setEnabled(True)
        self.main_menu_button_3.setEnabled(True)
        self.topics_combo_box.setEnabled(True)
        self.subjects_combo_box.setEnabled(True)
        self.classification_generate_button.setEnabled(True)
        self.accept_generation_button.setEnabled(True)
        self.regenerate_button.setEnabled(True)
        self.classification_topic_text_1.setEnabled(True)
        self.file_explorer_button.setEnabled(True)
        self.generated_document_list.setEnabled(True)
        self.menu_button_4.setEnabled(True)


    def topics_combo_box_changed(self):
        # get the document name
        topic = self.topics_combo_box.currentText()

        # get all subjects
        subjects_arr = update_requests.get_all_subjects_str(topic)

        # clear the combo box
        self.subjects_combo_box.clear()

        # add all subjects
        self.subjects_combo_box.addItem("All Subjects")

        # add the subjects
        self.subjects_combo_box.addItems(subjects_arr)

        # set the first item as current
        self.subjects_combo_box.setCurrentIndex(0)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
