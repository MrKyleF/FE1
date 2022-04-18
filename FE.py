#Kyle R Fogerty
from Dev.Cryptography import CryptoHandler

def selectAction():
    input_string = '\n' + "Action Selection:" + '\n'\
        + "0 - Decrypt For Use (Default)" + '\n'\
        + "1 - Encrypt Files" + '\n'\
        + "2 - Decrypt Files" + '\n'\
        + "3 - Settings" + '\n'\
        + "Enter Selection: "
    selection = input(input_string)
    if selection == "0" or len(selection) == 0:
        #Set to Re-Encrypt On Exit
        #Decrypt
        crypto = CryptoHandler()
        crypto.workingDecrypt()
    elif selection == "1":
        #Encrypt Folder
        crypto = CryptoHandler()
        crypto.encryptFolder()
    elif selection == "2":
        crypto = CryptoHandler()
        crypto.decryptFolder()
        #Decrypt Folder
    elif selection == "3":
        print('')
       #Open Settings
    else:
        print('\n' + "Incorrect Selection: Please Try Again")
        return selectAction()

if __name__ == "__main__":
    selectAction()