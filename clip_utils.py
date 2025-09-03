from imports import *
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
import platform
import subprocess



def show_top_results(results, image_folder, top_n=5):
    top_results = results[:top_n]
    fig, axs = plt.subplots(1, len(top_results), figsize=(15, 5))

    for ax, (filename, score) in zip(axs, top_results):
        image_path = os.path.join(image_folder, filename)
        image = Image.open(image_path)
        ax.imshow(image)
        ax.set_title(f"{filename}\n{score:.2f}")
        ax.axis("off")

    plt.tight_layout()
    plt.show()

def show_top_results_ui(self, results, image_folder, top_n=3):
    top_results = results[:top_n]
    labels = [self.result_1, self.result_2, self.result_3]  

    for i, (filename, score) in enumerate(top_results):
        image_path = os.path.join(image_folder, filename)
        pixmap = QPixmap(image_path)
        labels[i].setProperty("filename", filename)

        if not pixmap.isNull():
            # Optionally scale the pixmap to fit the label
            scaled_pixmap = pixmap.scaled(labels[i].width(), labels[i].height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            labels[i].setPixmap(scaled_pixmap)
            labels[i].setToolTip(f"{filename} — Score: {score:.2f}")
        else:
            labels[i].setText("Image not found")

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-L/14", device=device)
    return model, preprocess, device

def load_cache(cache_path, IMAGE_FOLDER, device, model, preprocess):
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        print(f"Loaded cache with {len(cache)} items.")
    else:
        #os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        cache = {}
        print("⚠️ No cache found. Starting fresh.")

        process_image(IMAGE_FOLDER, cache, device, model, preprocess)  # Process images to populate the cache
        save_cache(cache, cache_path)  # Save the newly created cache
    return cache

def clean_cache(cache, image_folder):
    existing_files = set(os.listdir(image_folder))
    keys_to_remove = [filename for filename in cache if filename not in existing_files]

    for key in keys_to_remove:
        del cache[key]

    if keys_to_remove:
        print(f"🧹 Removed {len(keys_to_remove)} cache entries for deleted files.")
    else:
        print(" Cache is clean. No missing files.")
    
    return cache

def save_cache(cache, cache_path):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump(cache, f)

def process_image(image_folder, embedding_cache, device, model, preprocess):
    #processing an entire batch of images 
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic"))] # getting all of the image files that are in the folder - using the listdir() method : gives list of all files and directories in the specified directory
    new_count = 0

    for filename in image_files:
        if filename in embedding_cache:
            continue

        image_path = os.path.join(image_folder, filename) #getting the path of the image inside the image folder using the join method

        try:
            image = Image.open(image_path).convert("RGB") #convert the image to RGB because CLIP only accepts images in this format 
            image_tensor = preprocess(image).unsqueeze(0).to(device) #unsqueeze Returns a new tensor with a dimension of size one inserted at the specified position. - preprocess applies CLIP's required preprocessing (resizing, cropping, normalizing)
            #we do the unsqueeze because CLIP expects a batch of images, even if it's just one image
            with torch.no_grad():
                embedding = model.encode_image(image_tensor).cpu().numpy().flatten() # Passes the image through CLIP’s vision encoder. – Returns a vector (e.g. 512 dimensions) that represents the semantic content of the image.
                # Moves the tensor to CPU (in case it was on GPU) – Converts it to a NumPy array – flatten() ensures it’s a 1D array instead of 2D (shape [512] instead of [1, 512]).
                embedding = embedding / np.linalg.norm(embedding)  # Normalize for cosine similarity - so that the comparison is only dependent on the direcction of the vectors and not on the magnitude
            
            embedding_cache[filename] = embedding # storing the embedding in the cache with the filename as the key - which will be later loaded in the pickle file 
            new_count += 1

            if new_count % 10 == 0: # print progress every 10 images
                print(f"{new_count} new images processed...")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    return new_count, embedding_cache

def process_save_image(image_path, device, model, preprocess, embedding_cache, CACHE_PATH):
    #processing a single image and saving it to the cache 
    try:
        filename = os.path.basename(image_path)
        image =Image.open(image_path).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            embedding = model.encode_image(image_input).cpu().numpy().flatten()
            embedding = embedding / np.linalg.norm(embedding)
        embedding_cache[filename] = embedding

        save_cache(embedding_cache, CACHE_PATH)
        print(f"new file {filename} processed and cahced")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def encode_prompt(device, model, prompt):
    with torch.no_grad():
        text_tokens = clip.tokenize([prompt]).to(device)
        text_embedding = model.encode_text(text_tokens).cpu().numpy().flatten() # encode_text is CLIP's encoder - the tokenized text goes through CLIP’s text encoder (based on a Transformer), producing a high-dimensional vector (typically 512-d) that captures the semantic meaning of the input.
        text_embedding = text_embedding / np.linalg.norm(text_embedding)  # normalize the embedding 
        return text_embedding 

def similarity_comparison(embedding_cache, text_embedding, prompt):
    results = [] # a list to store each filename and its similarity score 
    for filename, image_embedding in embedding_cache.items(): #where filenme is the actual name with which the image is saved in the folder and the embedding is the CLIP embedding 
        similarity = np.dot(text_embedding, image_embedding)  # cosine similarity 
        results.append((filename, similarity))

    # Sort and show top results
    results.sort(key=lambda x: x[1], reverse=True) # we are sorting based on the second element of each tuple i.e. x[1] (the similarity score) - and we want highest similarity first

    top_n = 3 
    print(f"\nTop {top_n} matches for: '{prompt}'\n")
    for filename, score in results[:top_n]:
        print(f"{filename}  (score: {score:.4f})")
    return results, top_n

def reveal_file_in_explorer(image_path):
    system = platform.system()
    if system == "Windows":
        subprocess.run(f'explorer /select,"{os.path.normpath(image_path)}"')
    elif system == "Darwin":  # macOS
        subprocess.run(["open", "-R", image_path])
    else:  # Linux
        subprocess.run(["xdg-open", os.path.dirname(image_path)])

