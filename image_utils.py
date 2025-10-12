import os
import uuid
from config import IMAGE_DIR

os.makedirs(IMAGE_DIR, exist_ok=True)

def save_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(IMAGE_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path
