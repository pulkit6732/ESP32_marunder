# ESP32 Marauder Console - Usage Guide

## 🚀 Quick Start

### Installation
```bash
pip install pyserial websockets
```

### Running the Application
```bash
python serial_server.py
```

The application will automatically:
- Start WebSocket server on port 8765
- Start HTTP server on port 80 (or next available port)
- Show access URL in console

### Access
Open your browser to the URL shown in the console output (typically `http://localhost:80`)

## ✅ Fixed Issues

### Cross-Platform Serial Detection
- **Windows**: Detects COM3-COM10 ports automatically
- **macOS**: Detects /dev/cu.usbserial-* and /dev/cu.SLAB_USBtoUART*
- **Linux/WSL**: Detects /dev/ttyUSB* and /dev/ttyACM* ports
- ESP32 devices are marked with ⭐ for easy identification

### WebSocket Fixes
- Fixed connection errors with proper error handling
- Auto-reconnection with exponential backoff
- Clean error messages displayed in terminal instead of crashes

### HTTP Server Fixes
- Fixed 403 Forbidden errors with proper MIME types
- Fixed 304 Not Modified issues with cache headers
- Automatic port fallback if default ports are in use

### Modern Professional UI
- Replaced neon green with modern blue/teal theme
- Inter and JetBrains Mono fonts for professional look
- Responsive design for desktop and mobile
- Subtle animations and hover effects

## 🎯 ESP32 Marauder Features

### Quick Commands
- `help` - Show available commands
- `scan` - Basic WiFi scan
- `scan -a` - Advanced scan with details
- `reboot` - Restart the device
- `version` - Show firmware version
- `list` - List captured data
- `settings` - Show current settings
- `update` - Check for updates

### Terminal Features
- Auto-scroll with toggle
- Copy all content to clipboard
- Download logs as text file
- Line count display
- Color-coded message types

### Connection Management
- Real-time connection status
- Automatic ESP32 port detection
- Manual port selection fallback
- Configurable baud rates (9600-921600)

## 📁 Project Files

- `serial_server.py` - Main application server
- `index.html` - Web interface
- `style.css` - Modern professional styling

## 🔧 Troubleshooting

### Port Access Issues
- **Linux/WSL**: Add user to dialout group: `sudo usermod -a -G dialout $USER`
- **Windows**: Close other serial applications (Arduino IDE, PuTTY, etc.)

### WebSocket Connection Issues
- Ensure both HTTP server and WebSocket server are running
- Check firewall settings
- Verify the application shows "✅ Servers started successfully!"

### Serial Port Not Found
- Connect ESP32 via USB
- Install CP210x or CH340 drivers if needed
- Use "Refresh Ports" button to rescan
- Try manual port selection if auto-detect fails

## 🌐 Supported Systems

✅ Windows 10/11 (Pro, Home, any edition)
✅ macOS (Intel/Apple Silicon)  
✅ Debian Linux (including Kali, Ubuntu)
✅ WSL2 on Windows

All issues from the original broken project have been resolved.