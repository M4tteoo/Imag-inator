from PySide6.QtWidgets import QMainWindow, QPushButton, QFrame, QWidget, QLineEdit, QStackedWidget, QApplication, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QSize
from PySide6.QtGui import QIcon, QFontDatabase, QFont

# #other part 
from clip_utils import *
from config import IMAGE_FOLDER, CACHE_PATH

import os

from pillow_heif import register_heif_opener
register_heif_opener()

from watchdog.observers import Observer
from The_watcher import MyEventHandler
import time 


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("themain.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()

        self.setCentralWidget(self.window)
        self.resize(400, 400)
        self.central_widget = self.window.findChild(QWidget, "centralwidget")
        self.stacked_widget = self.window.findChild(QStackedWidget, "stackedWidget")
        self.stacked_widget.setCurrentIndex(0)

        
        # Access widgets
        #results page
        self.results_page = self.window.findChild(QWidget, "results_page")

        #line edit - search bar
        self.line_edit = self.window.findChild(QLineEdit, "lineEdit_positive")
        self.line_edit_2 = self.window.findChild(QLineEdit, "lineEdit_negative")

        #frames
        self.frame = self.window.findChild(QFrame, "frame")
        self.image_search_frame = self.window.findChild(QFrame, "image_search_frame")
        self.select_file_frame = self.window.findChild(QFrame, "select_file_frame")
        self.title_frame = self.window.findChild(QFrame, "title_frame")
        self.results_frame = self.window.findChild(QFrame, "results_frame")
        self.functions_frame = self.window.findChild(QFrame, "functions_frame")
        self.menu_frame = self.window.findChild(QFrame, "menu_frame")
        self.photo_frame = self.window.findChild(QFrame, "photo_frame")
        self.buttons_frame = self.window.findChild(QFrame, "buttons_frame")
        self.scout_frame = self.window.findChild(QFrame, "scout_frame")
        
        #button for showing information
        self.show_button = self.window.findChild(QPushButton, "show_button")
        #button to show results on another window
        self.results_button = self.window.findChild(QPushButton, "results_button")
        #clear button
        self.clear_button = self.window.findChild(QPushButton, "clear_button")
        # night and day button
        self.mode_button = self.window.findChild(QPushButton, "mode_button")
        self.mode_button.setIcon(QIcon("/Users/matteosalami/Desktop/Imaginator/assets/20250511_1325_Lamps Outline Changed_remix_01jtzhd9xtexmt5e3q0aexq833.jpg"))
        # new search button - button to go bacj to the main page
        self.new_search_button = self.window.findChild(QPushButton, "new_search_button")
        # new search button - button to go back to the main page
        self.modify_search_button = self.window.findChild(QPushButton, "modify_search_button")
      
        # select file button
        self.select_file_button = self.window.findChild(QPushButton, "select_file_button")
       
        # history button
        self.history_button = self.window.findChild(QPushButton, "history_button")
        #add images button
        self.add_images_button = self.window.findChild(QPushButton, "add_images_button")
        #select folder button
        self.select_folder_button = self.window.findChild(QPushButton, "select_folder_button")

        #labels containing result images
        self.result_1 = self.window.findChild(QLabel, "photo_1")
        self.result_2 = self.window.findChild(QLabel, "photo_2")
        self.result_3 = self.window.findChild(QLabel, "photo_3")

        #upload label for reference images
        self.upload_label = self.window.findChild(QLabel, "upload_label")

        self.scout_label = self.window.findChild(QLabel, "scout_label")


        #title label
        self.title_label = self.window.findChild(QLabel, "title_label")
        # Load the font
        font_id = QFontDatabase.addApplicationFont("/Users/matteosalami/Desktop/Imaginator/fonts/Cinzel/static/Cinzel-Bold.ttf")
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            font = QFont(family, 17)  
            font.setCapitalization(QFont.AllUppercase)
            
            self.title_label.setFont(font)
        else:
            print('fail')

        for label in [self.result_1, self.result_2, self.result_3]:
            label.setFixedSize(220, 220) 
            label.setScaledContents(False)

        # retrieval buttons
        self.retrieve_button_1 = self.window.findChild(QPushButton, "retrieve_1")
        self.retrieve_button_2 = self.window.findChild(QPushButton, "retrieve_2")
        self.retrieve_button_3 = self.window.findChild(QPushButton, "retrieve_3")

        #initially setting light mode
        self.set_light()
        self.central_widget.setProperty("dark_mode", False)
        self.mode_button.setIcon(QIcon("/Users/matteosalami/Desktop/Imaginator/assets/20250512_1522_Minimalist Lamp Design_remix_01jv2ag2m9e37baznxa7ytf8ee.png"))
        self.mode_button.setIconSize(QSize(24, 24))     
        
        #load model and cache
        self.model, self.preprocess, self.device, self.embedding_cache = self.load()


        self.modify_search_button
        # Connect signals 
        self.line_edit.returnPressed.connect(self.show_results)
        self.line_edit_2.returnPressed.connect(self.show_results)
        self.line_edit.returnPressed.connect(self.app)
        self.line_edit_2.returnPressed.connect(self.app)
        self.mode_button.clicked.connect(self.night_and_day)
        self.results_button.clicked.connect(self.show_results)
        self.results_button.clicked.connect(self.app)
        self.new_search_button.clicked.connect(self.back_to_search)
        self.modify_search_button.clicked.connect(self.modify_search)
        self.clear_button.clicked.connect(self.clear_line_edit)
        self.retrieve_button_1.clicked.connect(lambda: self.get_image( self.result_1.property("filename"))) # we add lambdabecause otherwise the .property would be evaluated immediately but we want it to be evaluated when the button is clicked
        self.retrieve_button_2.clicked.connect(lambda: self.get_image( self.result_2.property("filename")))
        self.retrieve_button_3.clicked.connect(lambda: self.get_image( self.result_3.property("filename")))


    def toggle_label(self):
        self.info_frame.setVisible(not self.info_frame.isVisible())

    def clear_line_edit(self):
        self.line_edit.clear()
        self.line_edit_neg.clear()
        self.line_edit.setFocus()

    def set_light(self):
        with open("light_theme.qss", "r") as f:
            self.central_widget.setStyleSheet(f.read())       
   
    def night_and_day(self):
        dark_mode = self.central_widget.property("dark_mode") or False
        

        if not dark_mode:
            # --- DARK MODE ---
            with open("dark_theme.qss", "r") as f:
                self.central_widget.setStyleSheet(f.read()) 
            self.central_widget.setProperty("dark_mode", True)
            self.mode_button.setIcon(QIcon("/Users/matteosalami/Desktop/Imaginator/assets/20250512_1515_Expanded Lamp Illustration_remix_01jv2a2x66ey09grsxdtbns50y.png"))
            self.mode_button.setIconSize(QSize(24, 24))

        else:
            with open("light_theme.qss", "r") as f:
                self.central_widget.setStyleSheet(f.read()) 

             
            self.central_widget.setProperty("dark_mode", False)
            self.mode_button.setIcon(QIcon("/Users/matteosalami/Desktop/Imaginator/assets/20250512_1522_Minimalist Lamp Design_remix_01jv2ag2m9e37baznxa7ytf8ee.png"))
            self.mode_button.setIconSize(QSize(24, 24))

    def load(self):
        model, preprocess, device = load_model()
        embedding_cache = load_cache(CACHE_PATH, IMAGE_FOLDER, device, model, preprocess)
        embedding_cache = process_image(IMAGE_FOLDER, embedding_cache, device, model, preprocess)[1]  # Process images to populate the cache
        embedding_cache = clean_cache(embedding_cache, IMAGE_FOLDER)
        save_cache(embedding_cache, CACHE_PATH) 


        return model, preprocess, device, embedding_cache

    def app(self):
        if not self.line_edit.text() == "":
            # Prompt from user
            positive_prompt = self.line_edit.text()
            negative_prompt = self.line_edit_2.text()

            self.initial_positive_prompt = positive_prompt
            self.initial_negative_prompt = negative_prompt

            self.line_edit.clear()
            self.line_edit_2.clear()
            positive_embedding = encode_prompt(self.device, self.model, positive_prompt)

            if negative_prompt.strip() != "":
                negative_embedding = encode_prompt(self.device, self.model, negative_prompt)
                # Combine embeddings: "like A, not like B"
                text_embedding = positive_embedding - 0.5 * negative_embedding
            else:
                text_embedding = positive_embedding

            # Compare with image embeddings
            results, top_n = similarity_comparison(self.embedding_cache, text_embedding, positive_prompt)

            show_top_results_ui(self, results, IMAGE_FOLDER, top_n = top_n)

            
        else:
            pass
        
    def show_results(self):
        if not self.line_edit.text() == "":
            self.stacked_widget.setCurrentIndex(1)
        # self.resize(800, 600)
    def back_to_search(self):
        self.stacked_widget.setCurrentIndex(0)
        self.result_1.clear()
        self.result_2.clear()
        self.result_3.clear()
    def quit_app(self):
        QApplication.quit()
    def run(self):
        self.show()    
    def get_image(self, filename):
        image_path = os.path.join(IMAGE_FOLDER, filename)

        reveal_file_in_explorer(image_path)
    def modify_search(self):
        self.stacked_widget.setCurrentIndex(0)
        self.line_edit.setText(self.initial_positive_prompt)
        self.line_edit_2.setText(self.initial_negative_prompt)
        self.result_1.clear()
        self.result_2.clear()
        self.result_3.clear()
