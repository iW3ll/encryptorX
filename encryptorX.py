import os
import os.path
import sys
import getpass
import time
from Crypto import Random
from Crypto.Cipher import AES

class Encryptor:
    def __init__(self, key):
        self.key = key
    
    def generate_new_key(self):
      new_key = os.urandom(256)[:32]  
      key_hex = new_key.hex()  
      with open("encryption_key.txt", "w") as key_file:
        key_file.write(key_hex)
        print(f"\n{key_hex}")
      return new_key

    def load_key_from_file(self, file_name):
        with open(file_name, "r") as key_file:
            key = key_file.read()
        return key

    def save_key_to_file(self, file_name, key):
        with open(file_name, "wb") as key_file:
            key_file.write(key)

    def pad(self, s):
        pad_len = AES.block_size - len(s) % AES.block_size
        padding = bytes([pad_len] * pad_len)
        return s + padding

    def encrypt(self, message, key):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)
        os.remove(file_name)

    def decrypt(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        pad_len = plaintext[-1]
        return plaintext[:-pad_len]

    def decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, self.key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)
        os.remove(file_name)

    def getAllFiles(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dirs = []
        for dirName, subdirList, fileList in os.walk(dir_path):
            for fname in fileList:
                if (fname != 'encriptorX.py' and fname != 'data.txt.enc'):
                    dirs.append(dirName + "\\" + fname)
        return dirs

    def encrypt_all_files(self):
        dirs = self.getAllFiles()
        for file_name in dirs:
            self.encrypt_file(file_name)

    def decrypt_all_files(self):
        dirs = self.getAllFiles()
        for file_name in dirs:
            self.decrypt_file(file_name)
    
def parse_args():
    args = sys.argv[1:]
    key = None
    if '--key' in args:
        key_index = args.index('--key') + 1
        if key_index < len(args):
            key_hex = args[key_index]
            key = bytes.fromhex(key_hex)
    return key

key_from_args = parse_args()              
key = key_from_args if key_from_args else b'\xf9\x89TB\xc7\x02\xd9\xdeE\xc7\xa1\x19\xb1\xc6\xcb\x83\x8e\xf7l-\x04\t\x8azc8\xdb\xf7\x8a\x9e,\x8c'
enc = Encryptor(key)
clear = lambda: os.system('clear')
print(key)

if os.path.isfile('data.txt.enc'):
    while True:
        password = getpass.getpass("[!] Enter your password: ")
        enc.decrypt_file("data.txt.enc")
        p = ''
        with open("data.txt", "r") as f:
            p = f.readlines()
        if p[0] == password:
            enc.encrypt_file("data.txt")
            break

    while True:
        clear()
        choice = int(input(
            "1. Press '1' to encrypt file.\n2. Press '2' to decrypt file.\n3. Press '3' to Encrypt all files in the "
            "directory.\n4. Press '4' to decrypt all files in the directory.\n5. Press '5' to generate a new key.\n6. Press '6' to exit.\n"))
        clear()
        if choice == 1:
            enc.encrypt_file(str(input("Enter name of file to encrypt: ")))
        elif choice == 2:
            enc.decrypt_file(str(input("Enter name of file to decrypt: ")))
        elif choice == 3:
            enc.encrypt_all_files()
        elif choice == 4:
            enc.decrypt_all_files()
        elif choice == 5:
            enc.key = enc.generate_new_key()
            print("\nNew key generated and saved in encryption_key.txt\nWARN: Keep this key safe it is used to decrypted your files!\n")
          
        elif choice == 6:
            exit()
        else:
            print("Please select a valid option!")

else:
    while True:
        clear()
        password = getpass.getpass("Setting up stuff. Enter a password that will be used for decryption: ")
        repassword = getpass.getpass("Confirm password: ")
        if password == repassword:
            break
        else:
            print("Passwords Mismatched!")
    f = open("data.txt", "w+")
    f.write(password)
    f.close()
    enc.encrypt_file("data.txt")
    print("The program will restart shortly. Please re-run.")
time.sleep(5)

