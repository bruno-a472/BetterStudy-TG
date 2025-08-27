from random import randint


class GeraId():
    def __init__(self):
        self.id_lista = []
    
    def geraId(self):
        while True:
            num = randint(1, 20)
            if num not in self.id_lista :
                self.id_lista.append(num)
                return num

    def obtemId_Lista(self):
        return self.id_lista