import base64
import os, sys
from os import listdir
from os.path import isfile, join, isdir, exists
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from Dev.SaltHandling import checkIfSaltExists
import getpass
import atexit
import queue
import threading


class CryptoHandler:
    #Create Fernet Key For Encryption and Decryption
    def createFernet(self):
        salt = checkIfSaltExists()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000,)
        self.fernet = Fernet(base64.urlsafe_b64encode(kdf.derive(getpass.getpass(prompt="Enter Password: ").encode("utf-8"))))
    
    #Create A Second Fernet Key For Re-Encryption and Decryption
    def createFerentLocal(self):
        salt = checkIfSaltExists()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000,)
        return Fernet(base64.urlsafe_b64encode(kdf.derive(getpass.getpass(prompt="Enter New Password: ").encode("utf-8"))))
    
    def __init__(self, max_threads = 8):
        self.max_threads = max_threads
        self.queue = queue.Queue()
        self.folder_path = input("Path To Folder: ")
    
    def getTaskIfQueue(self):
        if self.queue.empty() == False:
            return self.queue.get()
        else:
            return None
    
    def markTaskDone(self):
        self.queue.task_done()
    
    class CryptoThread:
        def __init__(self, thread_number, handler, encrypt=True):
            self.done = False
            self.encrypt = encrypt
            self.handler = handler
            self.thread_number = thread_number
        
        def encryptFile(self, path):
            #Open Orginial File
            with open(path, 'rb') as file:
                original = file.read()
            #Encrypted Version Of The File
            encrypted = self.handler.fernet.encrypt(original)
            #Save Encrypted Version In Place of Original
            with open(path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted)
        
        def decryptFile(self, path):
            # opening the encrypted file
            with open(path, 'rb') as enc_file:
                encrypted = enc_file.read()
            # decrypting the file
            decrypted = self.handler.fernet.decrypt(encrypted)
            with open(path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted)
        
        def run(self):
            while self.done == False:
                next_task = self.handler.getTaskIfQueue()
                if next_task != None:
                    #Next_task = Amazon Item
                    if self.encrypt == True:
                        self.encryptFile(next_task)
                    else:
                        self.decryptFile(next_task)
                    self.handler.markTaskDone()
                else:
                    return
    
    #Encrypts Files Using Current Ferent
    def encryptFile(self, path):
        #Open Orginial File
        with open(path, 'rb') as file:
            original = file.read()
        #Encrypted Version Of The File
        encrypted = self.fernet.encrypt(original)
        #Save Encrypted Version In Place of Original
        with open(path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
    
    def decryptFile(self, path):
        # opening the encrypted file
        with open(path, 'rb') as enc_file:
            encrypted = enc_file.read()
        # decrypting the file
        decrypted = self.fernet.decrypt(encrypted)
        with open(path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted)
    
    def secureEreaseFernet(self, overwrites: int = 1000):
        del self.fernet
        for _ in range(0, overwrites):
            self.fernet = os.urandom(256)
            del self.fernet

    def getAllPaths(self, current_path):
        onlyfiles = [f for f in listdir(current_path) if isfile(join(current_path, f))]
        subfolders = [ f for f in os.scandir(current_path) if f.is_dir()]
        new_paths = []
        delete_paths = []
        for file in onlyfiles:
            if file.endswith(".DS_Store"):
                delete_paths.append(join(current_path, file))
            else:
                new_paths.append(join(current_path, file))
        directories = []
        for dir in subfolders:
            directories.append(join(current_path, dir.name))
        for dir in directories:
            new_paths = new_paths + self.getAllPaths(dir)
        for delete_path in delete_paths:
            os.remove(delete_path)
        return new_paths

    def encryptFolderInternal(self):
        paths = self.getAllPaths(self.folder_path)
        self.crypto_threads = []
        for i in range(self.max_threads):
            self.crypto_threads.append(CryptoHandler.CryptoThread(i, self, True))
        for path in paths:
            self.queue.put(path)
        for i in range(self.max_threads):
            worker = threading.Thread(target=self.crypto_threads[i].run, args=(), daemon=True)
            worker.start()
        self.queue.join()
    
    def encryptFolderInternalFinal(self):
        self.encryptFolderInternal()
        self.secureEreaseFernet()
    
    def encryptFolder(self):
        self.createFernet()
        self.encryptFolderInternal()
        self.secureEreaseFernet()
    
    def decryptFolderInternal(self):
        paths = self.getAllPaths(self.folder_path)
        self.crypto_threads = []
        for i in range(self.max_threads):
            self.crypto_threads.append(CryptoHandler.CryptoThread(i, self, False))
        for path in paths:
            self.queue.put(path)
        for i in range(self.max_threads):
            worker = threading.Thread(target=self.crypto_threads[i].run, args=(), daemon=True)
            worker.start()
        self.queue.join()
    
    def decryptFolder(self):
        self.createFernet()
        self.decryptFolderInternal()
        self.secureEreaseFernet()
    
    def workingDecrypt(self):
        self.createFernet()
        atexit.register(self.encryptFolderInternalFinal)
        self.decryptFolderInternal()
        while True:
            pass
        
