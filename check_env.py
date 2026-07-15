data = open('.env', 'rb').read()
print('Byte 85:', hex(data[85]))
print('Contexto:', data[80:90])