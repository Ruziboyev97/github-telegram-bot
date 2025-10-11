from cryptography.fernet import Fernet
from config import config

class EncryotionService:
    """shifrofka va deshifrofka"""

    def __init__(self) -> None:
        if config.ENCRYPRION_KEY != None:
            self.cipher = Fernet(config.ENCRYPRION_KEY.encode())
        else:
            print("shirflash kodi bo'sh")
    def encrypt(self, data: str) -> str:
        """ma'lumotlarni shifrlash"""
        enrypted = self.cipher.encrypt(data.encode())
        return enrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """shifrni yechish"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()