from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from clip_utils import process_save_image, load_model

class MyEventHandler(FileSystemEventHandler):
    def __init__(self, model, preprocess, device, embedding_cache, cache_path, image_folder):
        super().__init__()
        self.model = model
        self.preprocess = preprocess
        self.device = device
        self.embedding_cache = embedding_cache
        self.cache_path = cache_path
        self.image_folder = image_folder
    def on_created(self, event):
        if not event.is_directory: #if True the event was a folder, if false it was a file - we are interested in the addition of files
            print(f"A New file was added: {event.src_path}")
            #so we embed it and cahe it with CLIP
            process_save_image(event.src_path, self.device, self.model, self.preprocess, self.embedding_cache,  self.cache_path)
        


