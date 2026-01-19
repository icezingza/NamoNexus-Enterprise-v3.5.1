# -----------------------------------------------------------------------------
# 🐳 Dockerfile for NamoNexus Enterprise v3.5.1 (Sovereign Edition)
# -----------------------------------------------------------------------------

# 1. Base Image: ใช้ Python 3.11 แบบ Slim (เบาแต่ครบเครื่อง)
FROM python:3.11-slim

# 2. Metadata
LABEL maintainer="Ice & Namo <namo-nexus-team>"
LABEL version="3.5.1"
LABEL description="Sovereign AI Infrastructure with Multimodal Capabilities"

# 3. System Dependencies (ติดตั้ง FFmpeg และ SQLCipher ที่นี่ทีเดียวจบ!)
# - ffmpeg: สำหรับหูทิพย์ (Mission 2)
# - libsqlcipher-dev: สำหรับฐานข้อมูลเข้ารหัส
# - build-essential: สำหรับ compile library บางตัว
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsqlcipher-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Setup Workspace
WORKDIR /app

# 5. Install Python Dependencies
# Copy แค่ requirements ก่อน เพื่อใช้ Docker Cache (ถ้าแก้ Code แต่ไม่แก้ Lib จะได้ไม่ต้องโหลดใหม่)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Code
COPY . .

# 7. Security: สร้าง User ธรรมดา (ไม่ใช้ Root) เพื่อความปลอดภัยสูงสุด
RUN useradd -m namo_user
USER namo_user

# 8. Expose Port
EXPOSE 8000

# 9. Ignition Command (เดินเครื่อง!)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
