import socket
import sys
import threading
from .handlers.handle_client import handle_client
from .config import PORT, HOST

def start_server():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Portu serbest bırakmayı dene
        try:
            s.bind((HOST, PORT))
        except OSError:
            print(f"Port {PORT} kullanımda. Sunucuyu kapatıp tekrar deneyin.")
            print("Kullanımdaki portu kontrol etmek için:")
            print(f"netstat -ano | findstr :{PORT}")
            sys.exit(1)
            
        s.listen(5)
        print(f"Sunucu başlatıldı - {HOST}:{PORT}")
        
        while True:
            try:
                conn, addr = s.accept()
                print(f"Bağlantı geldi: {addr}")
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(conn, addr)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"Bağlantı hatası: {str(e)}")
                
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
    except Exception as e:
        print(f"Kritik hata: {str(e)}")
    finally:
        try:
            s.close()
        except:
            pass
        
if __name__ == "__main__":
    start_server()