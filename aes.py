import base64
import bcrypt
import argparse
import getpass
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key): 
        self.bs = 32
        salt = 'zkj$!@,ap!c$ywEEz(^~!$QeZ*dD-$_p'
        self.key = bcrypt.kdf(key, salt, 16, 100)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


parser = argparse.ArgumentParser(description='Mihai`s tool for encrypting with AES')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-e', action='store_true', help='encrypting mode')
group.add_argument('-d', action='store_true', help='decrypting mode')
parser.add_argument('input', metavar='infile', type=str, help='filename to encrypt/decrypt')
parser.add_argument('-o', metavar='outfile', type=str, help='custom output filename')
args = parser.parse_args()

password = getpass.getpass('Enter password :')
cipher = AESCipher(password)

with open(args.input,'r') as f:
    if args.e:
        # Encryption mode
        plain = f.read()
        cipherdata = cipher.encrypt(plain)
        if args.o is None:
            out = args.input+'.enc'
        else:
            out = args.o
        with open(out,'w') as g:
            g.write(cipherdata)
    else:
        # Decryption mode
        cipherdata = f.read()
        plain = cipher.decrypt(cipherdata)
        if args.o is None:
            out = args.input+'.dec'
        else:
            out = args.o
        with open(out,'w') as g:
            g.write(plain)
