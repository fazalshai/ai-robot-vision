## 🧠 Methodology: Eliminating the Train/Test Loop
## 🎥 Demo Video
[Click here to watch the demo video](./demo_preview.mp4)
Traditional computer vision pipelines (like YOLO or Faster R-CNN) rely on a rigid, labor-intensive supervised learning cycle:
1.  **Data Collection:** Gathering thousands of images.
2.  **Annotation:** Manually drawing bounding boxes for specific classes (e.g., "car", "person").
3.  **Training:** burning GPU hours to fit weights.
4.  **Testing:** Validating on a hold-out set.

**This project eliminates that entire pipeline.**

By leveraging the **Gemini 1.5 Pro Vision-Language Model (VLM)**, we utilize a "Zero-Shot" inference approach. The model has already "learned" the world during its pre-training phase. Instead of retraining for new objects, we simply change the text prompt.

### ⚔️ Comparison: Traditional vs. VLM Approach

| Feature | Traditional CV (YOLO/CNN) | **My VLM Approach (Gemini 1.5)** |
| :--- | :--- | :--- |
| **New Object Setup** | Weeks (Collect -> Label -> Train) | **Seconds** (Update Text Prompt) |
| **Data Requirement** | Thousands of Labeled Images | **Zero** (No Data Needed) |
| **Flexibility** | Fixed Classes (Closed Set) | **Open Vocabulary** (Can detect anything) |
| **Context** | Label only ("Person") | Semantic Understanding ("Person running safely") |

This architecture shifts the engineering focus from **Data Munging** to **Prompt Engineering and System Architecture**, allowing for rapid prototyping of autonomous perception systems that can adapt to unstructured environments instantly.
