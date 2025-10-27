class ArvDriver:
    def __init__(self, id: int, driver=None, user_data_dir=None):
        self.esquerda: ArvDriver = None
        self.direita: ArvDriver = None
        self.id: int = id
        self.user_data_dir = user_data_dir
        self.driver = driver

    def defineDriver(self, driver):
        self.driver = driver
    
    def obtemDriver(self):
        return self.driver
    
    def obtemId(self):
        return self.id

    def insere(self, id, driver=None, user_data_dir=None):
        if id < self.id:
            if not self.esquerda:
                self.esquerda = ArvDriver(id, driver, user_data_dir)
            else:
                self.esquerda.insere(id, driver, user_data_dir)
        else:
            if not self.direita:
                self.direita = ArvDriver(id, driver, user_data_dir)
            else:
                self.direita.insere(id, driver, user_data_dir)

    def mostra_EmOrdem(self):
        if self.esquerda:
            self.esquerda.mostra_EmOrdem()
        print(f'ID: {self.id}, Driver: {self.driver}')
        if self.direita:
            self.direita.mostra_EmOrdem()

    def encontra(self, id):
        if id < self.id:
            if not self.esquerda:
                return None
            else:
                return self.esquerda.encontra(id)
        elif id > self.id:
            if not self.direita:
                return None
            else:
                return self.direita.encontra(id)
        elif id == self.id:
            return self