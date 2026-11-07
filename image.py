import socket

def start_browser_image_server(image_path, host='', port=6789):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow restarting the server immediately without "Address already in use" errors
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on http://localhost:{port}")
    
    while True:
        conn, addr = server_socket.accept()
        
        try:
            # 1. Read the browser's incoming HTTP request text (up to 1024 bytes)
            # We must read this, or the browser may fail to receive our response
            request = conn.recv(1024)
            if not request:
                continue
            
            # 2. Open the image file in Read-Binary ('rb') mode
            with open(image_path, 'rb') as file:
                image_data = file.read()
            
            # 3. Construct proper HTTP headers for the browser
            # We use .encode('utf-8') here because HTTP headers are text strings
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: image/jpeg\r\n"  # Change to image/png if using a PNG
                f"Content-Length: {len(image_data)}\r\n"
                "Connection: close\r\n"
                "\r\n"  # This blank line is crucial; it separates headers from the body
            ).encode('utf-8')
            
            # 4. Send the text headers first, then the raw binary image data
            conn.sendall(http_response)
            conn.sendall(image_data)
            
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            conn.close()

# Run the server (Make sure this file exists in your directory)
start_browser_image_server('anger.png')
