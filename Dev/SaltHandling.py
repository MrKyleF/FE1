from os.path import exists
import os
from cryptography.hazmat.primitives import hashes
import getpass

def createSaltPath(salt_number: str):
    front_len = 4 - len(salt_number)
    front_addition = ""
    for i in range(0, front_len):
        front_addition += '0'
    final_salt = front_addition + salt_number
    origin_path = '/Users/kylefogerty/Project Fluorine/Encrypt/FE1/Salts/' # **************** UPDATE IF CLONING REPO TO LOCAL FULL PATH ****************
    salt_path = origin_path + str(final_salt) + '.key'
    return salt_path

def checkIfSaltExists(pin: int = None):
    if pin == None:
        salt_path = createSaltPath(getpass.getpass(prompt="Enter Pin (1-4 Digits): "))
    else:
        salt_path = createSaltPath(str(pin))
    if exists(path=salt_path) == True:
        with open(salt_path, 'rb') as filekey:
            key = filekey.read()
        return key
    else:
        print("Error In Entry: Please Try Again")
        checkIfSaltExists()

def createSingleSalt(pin: int = None):
    if pin == None:
        salt_path = createSaltPath(getpass.getpass(prompt="Enter Pin (1-4 Digits): "))
    else:
        salt_path = createSaltPath(str(pin))
    if exists(path=salt_path) == True:
        with open(salt_path, 'rb') as filekey:
            key = filekey.read()
        return key
    else:
        key = os.urandom(16)
        with open(salt_path, 'wb') as filekey:
            filekey.write(key)

def createSaltBatch(number_of_salts: int = 10000): #Post 10,000 becomes difficult to work with
    for i in range(0, number_of_salts):
        createSingleSalt(pin=i)