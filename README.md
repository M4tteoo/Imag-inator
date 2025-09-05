# 📸 Imag-inator – Local Semantic Image Retrieval  

**Imag-inator** is a local-first desktop application that enables users to search through their personal image collections using **natural language** or even other **images as queries**.  
Powered by **OpenAI’s CLIP (ViT-L/14)**, Imag-inator aligns images and text in a shared semantic space, making intuitive, zero-shot image retrieval possible — all without relying on cloud services.  

---

## ✨ Features  

- 🔍 **Semantic search** with natural language queries (*e.g., “a cat sitting on a sofa”*)  
- 🖼️ **Image-to-image search**: find similar images by using an image as a query  
- 💻 **Local-first design**: all computation and data stay on your device  
- ⚡ **High efficiency** with embedding cache (skip recomputation)  
- 🖱️ **User-friendly GUI** built with PySide6 (Qt)  
  - Light/Dark mode  
  - Drag-and-drop folder support  
  - Prompt history  
  - Negative prompting (exclude unwanted results)  
- 👀 **Real-time folder monitoring** using Watchdog  

---

## 🚀 Motivation  

Managing and retrieving personal images is increasingly difficult as collections grow.  
Cloud-based solutions often come with trade-offs in **privacy, accessibility, and usability**.  

Imag-inator addresses this by providing:  
- A **local-first AI tool** for secure, offline use  
- A **natural language interface** aligned with how humans think and remember  
- A simple, intuitive GUI for non-technical users  

---

## 🛠️ How It Works  

1. **Preprocessing**  
   - Images are resized and normalized using Pillow + CLIP preprocess  

2. **Embedding**  
   - Images embedded with CLIP’s ViT-L/14 encoder  
   - Text prompts embedded with CLIP’s text encoder  
   - Embeddings cached locally (Pickle dictionary: `{filename: embedding}`)  

3. **Search**  
   - Cosine similarity ranks embeddings in the shared semantic space  
   - Results normalized and displayed instantly in the GUI  

4. **Dual Query Modes**  
   - Text → Image retrieval  
   - Image → Image retrieval  

---

## 📊 Evaluation  

- **Qualitative**: effective on abstract and blurry prompts; struggles with fine-grained details (e.g., species, numbers like “two dogs”)  
- **Quantitative**: strong Top-1 accuracy and MRR across test prompts  
- **Limitations**: gender bias, poor number understanding, and weak performance in highly specialized domains  

---

## Demo Video

![Imag-inator demo](assets/demo_video.gif)  

## 📦 Installation  

### Clone repository
`git clone https://github.com/yourusername/imag-inator.git`
`cd imag-inator`

### Create virtual environment
`python -m venv venv`
source venv/bin/activate   # On Windows: venv\Scripts\activate

### Install dependencies
pip install -r requirements.txt

### Run Imag-inator
python main.py
📋 Requirements
Python 3.9+
PyTorch with CUDA (optional, for GPU acceleration)
PySide6
Pillow
Watchdog
## 🔮 Future Work
Asynchronous processing for smooth GUI responsiveness
Support for other media types (video, documents, audio)
File operations (tagging, moving, sorting results)
Domain-specific CLIP fine-tuning
Integration of Composed Image Retrieval (CIR) for richer multimodal queries

## 🙌 Acknowledgements
OpenAI CLIP – Contrastive Language-Image Pretraining
PySide6 (Qt for Python) – GUI framework
Facebook AI Similarity Search (Faiss) – inspiration for efficient similarity search