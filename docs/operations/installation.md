# Operations: Installation & Setup Guide

## 1. System Requirements

### Minimum Configuration
- **Operating System**: Windows 10/11 64-bit (macOS 13+ / Linux Ubuntu 22.04+ compatible)
- **CPU**: 4 Cores / 8 Threads (Intel Core i5 10th Gen or AMD Ryzen 5 3600)
- **RAM**: 16 GB System Memory
- **GPU**: NVIDIA GPU with 4 GB VRAM (CUDA 11.8+) or CPU fallback
- **Disk**: 20 GB free NVMe SSD space
- **External Binaries**: FFmpeg 5.0+ / FFprobe 5.0+

### Recommended Production Configuration (Target Machine)
- **Operating System**: Windows 11 64-bit
- **CPU**: AMD Ryzen 7 7435HS (8 Cores, 16 Threads)
- **RAM**: 24 GB DDR5 System Memory
- **GPU**: NVIDIA GeForce RTX 4050 Laptop GPU (6 GB GDDR6 VRAM, CUDA 12.x / 13.x, Driver 550+)
- **Storage**: NVMe PCIe Gen4 SSD
- **External Binaries**: FFmpeg 8.0+ full build, Kdenlive 23.08+ / MLT `melt`

---

## 2. Step-by-Step Environment Setup

### Step 1: Verify Core Prerequisites
Open Windows PowerShell:
```powershell
python --version   # Must be 3.10+ (tested on 3.13)
node --version     # Must be v20+ (tested on v22)
ffmpeg -version    # Must be 5.0+ (tested on 8.0)
nvidia-smi         # Verify GPU and CUDA Driver
```

### Step 2: Install Python Backend Dependencies
Navigate to the AgentCut project root:
```powershell
# Create a dedicated virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install core framework dependencies
pip install fastapi uvicorn pydantic mcp rapidocr-onnxruntime opencv-python scenedetect faster-whisper torch torchvision
```

### Step 3: Install Frontend Dependencies
```powershell
npm install
```

### Step 4: Configure Environment & Hardware Settings
Create an `.env` file in the project root:
```ini
AGENTCUT_HOST=127.0.0.1
AGENTCUT_PORT=8000
AGENTCUT_PROJECTS_DIR=./projects
AGENTCUT_CACHE_DIR=./cache
AGENTCUT_DEVICE=cuda
AGENTCUT_VRAM_LIMIT_MB=4200
AGENTCUT_MELT_PATH=melt
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe
```

---

## 3. Running AgentCut in Development Mode

### Terminal 1: Launch Backend & MCP Server
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn agentcut.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Launch Electron Desktop Application
```powershell
npm run electron:dev
```

### Verifying MCP Server Stdio for Claude Desktop / External Agents
To connect Claude Desktop to AgentCut:
Add to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "agentcut": {
      "command": "C:\\path\\to\\AgentCut\\.venv\\Scripts\\python.exe",
      "args": ["-m", "agentcut.mcp.server", "--transport", "stdio"]
    }
  }
}
```

