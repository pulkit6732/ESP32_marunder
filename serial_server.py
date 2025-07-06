#!/usr/bin/env python3
"""
ESP32 Marauder Serial Console Server
Cross-platform WebSocket server for ESP32 serial communication
Supports Windows, MacOS, Linux, WSL2
"""

import asyncio
import websockets
import json
import threading
import time
import os
import sys
import http.server
import socketserver
from pathlib import Path

# Try to import serial, handle gracefully if not available
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Error: pyserial is required. Install with: pip install pyserial")

class SerialManager:
    """Manages cross-platform serial communication with ESP32 Marauder"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.read_thread = None
        self.should_stop = False
        self.clients = set()
        self.current_port = None
        self.current_baudrate = None
        
    async def add_client(self, websocket):
        """Add WebSocket client"""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
    async def remove_client(self, websocket):
        """Remove WebSocket client"""
        self.clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def broadcast_message(self, message):
        """Send message to all connected clients"""
        if self.clients:
            clients_copy = self.clients.copy()
            for client in clients_copy:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    self.clients.discard(client)
                except Exception as e:
                    print(f"Error sending to client: {e}")
                    self.clients.discard(client)
                    
    def get_available_ports(self):
        """Get list of available serial ports with ESP32 detection"""
        if not SERIAL_AVAILABLE:
            return []
        
        ports = []
        esp32_keywords = [
            'esp32', 'esp', 'silicon labs', 'cp210x', 'ch340', 'ch341', 
            'ftdi', 'prolific', 'arduino', 'usb-serial', 'uart', 'marauder'
        ]
        
        try:
            for port in serial.tools.list_ports.comports():
                port_info = {
                    'device': port.device,
                    'description': port.description or 'Unknown Device',
                    'hwid': port.hwid or '',
                    'manufacturer': getattr(port, 'manufacturer', '') or '',
                    'is_esp32': False
                }
                
                # Check if this looks like an ESP32 device
                check_text = f"{port_info['description']} {port_info['hwid']} {port_info['manufacturer']}".lower()
                if any(keyword in check_text for keyword in esp32_keywords):
                    port_info['is_esp32'] = True
                
                ports.append(port_info)
                
        except Exception as e:
            print(f"Error listing ports: {e}")
        
        # Sort ESP32 devices first
        ports.sort(key=lambda x: (not x['is_esp32'], x['device']))
        return ports
        
    def auto_detect_esp32_port(self):
        """Auto-detect the first ESP32-like device"""
        ports = self.get_available_ports()
        
        # First try ESP32-identified devices
        for port in ports:
            if port['is_esp32']:
                return port['device']
        
        # Fallback to common ESP32 port names
        common_ports = []
        if os.name == 'nt':  # Windows
            common_ports = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10']
        else:  # Linux/Mac/WSL
            common_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1', 
                           '/dev/cu.usbserial-*', '/dev/cu.SLAB_USBtoUART*']
        
        # Test common ports
        for test_port in common_ports:
            if '*' in test_port:  # Handle wildcards for macOS
                continue
            try:
                test_conn = serial.Serial(port=test_port, baudrate=115200, timeout=0.1)
                test_conn.close()
                return test_port
            except:
                continue
                
        # Return first available port if nothing else works
        if ports:
            return ports[0]['device']
            
        return None
        
    def connect(self, port=None, baudrate=115200):
        """Connect to serial port with proper error handling"""
        if not SERIAL_AVAILABLE:
            return False, "pyserial library not available. Install with: pip install pyserial"
            
        if self.is_connected:
            self.disconnect()
            
        # Auto-detect port if not specified
        if not port or port == "auto":
            port = self.auto_detect_esp32_port()
            if not port:
                return False, "No ESP32 devices detected. Please select a port manually."
                
        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1,
                write_timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            self.is_connected = True
            self.should_stop = False
            self.current_port = port
            self.current_baudrate = baudrate
            
            # Start reading thread
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            return True, f"Connected to {port} at {baudrate} baud"
            
        except serial.SerialException as e:
            error_msg = f"Failed to connect to {port}: {str(e)}"
            if "Access is denied" in str(e) or "Permission denied" in str(e):
                error_msg += "\nPort may be in use by another application. Close other serial programs and try again."
            elif "does not exist" in str(e) or "No such file" in str(e):
                error_msg += "\nPort not found. Please refresh and select the correct port."
            return False, error_msg
            
        except Exception as e:
            return False, f"Unexpected error connecting to {port}: {str(e)}"
            
    def disconnect(self):
        """Disconnect from serial port"""
        self.should_stop = True
        self.is_connected = False
        
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
            
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=3)
            
        self.current_port = None
        self.current_baudrate = None
            
    def send_data(self, data):
        """Send data to serial port with proper encoding"""
        if not self.is_connected or not self.connection:
            return False, "Not connected to serial port"
            
        try:
            # Ensure data ends with newline for ESP32 commands
            if not data.endswith('\n'):
                data += '\n'
                
            # Send as UTF-8 bytes
            self.connection.write(data.encode('utf-8', errors='replace'))
            self.connection.flush()
            return True, "Command sent"
            
        except serial.SerialException as e:
            self.is_connected = False
            return False, f"Serial error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send command: {str(e)}"
            
    def _read_loop(self):
        """Background thread to read serial data line by line"""
        buffer = ""
        
        while not self.should_stop and self.is_connected and self.connection:
            try:
                if self.connection.in_waiting > 0:
                    # Read available bytes
                    try:
                        chunk = self.connection.read(self.connection.in_waiting)
                        text = chunk.decode('utf-8', errors='replace')
                        buffer += text
                        
                        # Process complete lines
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.rstrip('\r')  # Remove carriage return
                            
                            if line.strip():  # Only send non-empty lines
                                asyncio.run_coroutine_threadsafe(
                                    self.broadcast_message(line),
                                    asyncio.get_event_loop()
                                )
                                
                    except UnicodeDecodeError as e:
                        # Handle invalid UTF-8 gracefully
                        error_msg = f"Encoding error: {str(e)}"
                        asyncio.run_coroutine_threadsafe(
                            self.broadcast_message(f"⚠️ {error_msg}"),
                            asyncio.get_event_loop()
                        )
                        
                else:
                    time.sleep(0.01)  # Small delay to prevent CPU spinning
                    
            except serial.SerialException as e:
                self.is_connected = False
                error_msg = f"Serial connection lost: {str(e)}"
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_message(f"❌ {error_msg}"),
                    asyncio.get_event_loop()
                )
                break
            except Exception as e:
                print(f"Unexpected read error: {e}")
                break

# Global serial manager instance
serial_manager = SerialManager()

async def handle_websocket_client(websocket, path):
    """Handle WebSocket client connections"""
    await serial_manager.add_client(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action')
                
                if action == 'get_ports':
                    ports = serial_manager.get_available_ports()
                    response = {
                        'type': 'ports',
                        'data': ports
                    }
                    await websocket.send(json.dumps(response))
                    
                elif action == 'connect':
                    port = data.get('port')
                    if port == '':  # Auto-detect
                        port = None
                    baudrate = int(data.get('baudrate', 115200))
                    success, msg = serial_manager.connect(port, baudrate)
                    
                    response_type = 'SUCCESS' if success else 'ERROR'
                    await websocket.send(f"{response_type}: {msg}")
                    
                elif action == 'disconnect':
                    serial_manager.disconnect()
                    await websocket.send("✅ Disconnected")
                    
                elif action == 'send':
                    command = data.get('data', '').strip()
                    if command:
                        success, msg = serial_manager.send_data(command)
                        if not success:
                            await websocket.send(f"❌ {msg}")
                        else:
                            # Echo the command to show it was sent
                            await websocket.send(f"➤ {command}")
                            
                elif action == 'status':
                    if serial_manager.is_connected:
                        status = f"Connected to {serial_manager.current_port} at {serial_manager.current_baudrate} baud"
                    else:
                        status = "Disconnected"
                    await websocket.send(f"📊 Status: {status}")
                    
            except json.JSONDecodeError:
                await websocket.send("❌ Invalid message format")
            except ValueError as e:
                await websocket.send(f"❌ Invalid parameter: {str(e)}")
            except Exception as e:
                print(f"Message handling error: {e}")
                await websocket.send(f"❌ Error: {str(e)}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await serial_manager.remove_client(websocket)

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with proper MIME types"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=Path(__file__).parent, **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def guess_type(self, path):
        """Fix MIME type detection"""
        if path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.html'):
            return 'text/html'
        else:
            return super().guess_type(path)
    
    def log_message(self, format, *args):
        # Reduce HTTP log noise
        pass

def start_http_server(port=8080):
    """Start HTTP server for static files"""
    max_retries = 10
    current_port = port
    
    for attempt in range(max_retries):
        try:
            httpd = socketserver.TCPServer(("0.0.0.0", current_port), HTTPRequestHandler)
            httpd.allow_reuse_address = True
            print(f"HTTP server running on http://0.0.0.0:{current_port}")
            print(f"Access at: http://localhost:{current_port}")
            httpd.serve_forever()
            break
        except OSError as e:
            if e.errno == 98 or "Address already in use" in str(e):
                print(f"Port {current_port} is in use. Trying port {current_port + 1}")
                current_port += 1
                if attempt == max_retries - 1:
                    print(f"Failed to find available port after {max_retries} attempts")
                    return
            else:
                print(f"Failed to start HTTP server: {e}")
                return
        except Exception as e:
            print(f"HTTP server error: {e}")
            return

async def main():
    """Main server function"""
    if not SERIAL_AVAILABLE:
        print("❌ Error: pyserial is required")
        print("Install with: pip install pyserial websockets")
        sys.exit(1)
        
    print("🚀 ESP32 Marauder Serial Console Server")
    print("="*50)
    
    # Find available ports
    websocket_port = 8765
    http_port = 8080
    
    # Check if HTTP port 80 is available (requires admin on Windows/Linux)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 80))
        sock.close()
        http_port = 80
    except:
        pass  # Use 8080 instead
    
    print(f"📡 WebSocket server: ws://0.0.0.0:{websocket_port}")
    print(f"🌐 HTTP server: Starting on port {http_port} (will auto-adjust if needed)")
    print(f"🔗 Access web interface at the port shown above")
    print("📋 Supported systems: Windows, MacOS, Linux, WSL2")
    print("\n⚡ Starting servers...")
    
    # Start HTTP server in background thread
    http_thread = threading.Thread(
        target=start_http_server, 
        args=(http_port,), 
        daemon=True
    )
    http_thread.start()
    
    # Start WebSocket server
    try:
        start_server = websockets.serve(handle_websocket_client, "0.0.0.0", websocket_port)
        print("✅ Servers started successfully!")
        print("Press Ctrl+C to stop")
        
        await start_server
        await asyncio.Future()  # Run forever
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        serial_manager.disconnect()
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")