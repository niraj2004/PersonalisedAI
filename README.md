# Personal Learning Assistant

A personal learning assistant app that converts a backlog of saved resources into structured, curriculum-aligned daily learning.

## Setup

1.  **Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    Copy `.env.example` to `.env` and fill in your keys.

3.  **Run**:
    - Backend: `uvicorn backend.main:app --reload`
    - Frontend: `streamlit run frontend/app.py`
