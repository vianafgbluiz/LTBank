class User:
    __id = None
    __nmName = None
    __nmCPF = None
    __nmTelefone = None
    __nmEmail = None
    __nmPassword = None
    __flActive = None
    __dtCreated = None
    __dtUpdated = None

    def __init__(self, idCategoria, tituloCategoria, descricaoCategoria, fgAtivo):
        self.__idCategoria = idCategoria
        self.__tituloCategoria = tituloCategoria
        self.__descricaoCategoria = descricaoCategoria
        self.__fgAtivo = fgAtivo

    def getIdCategoria(self):
        return self.__idCategoria

    def getTituloCategoria(self):
        return self.__tituloCategoria

    def getDescricaoCategoria(self):
        return self.__descricaoCategoria

    def getAtivoCategoria(self):
        return self.__fgAtivo