import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente(ABC):
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.tipo = "PF"


class PessoaJuridica(Cliente):
    def __init__(self, razao_social, fundacao, cnpj, endereco):
        super().__init__(endereco)
        self.razao_social = razao_social
        self.fundacao = fundacao
        self.cnpj = cnpj
        self.tipo = "PJ"


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True
    
    def adicionar_transacao(self, transacao):
        transacao.registrar(self)

    def exibir_extrato(self):
        print("\n=============== EXTRATO ===============")
        if not self.historico.transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for transacao in self.historico.transacoes:
                print(f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
        print(f"\nSaldo atual: R$ {self.saldo:.2f}")
        print("=======================================")


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [t for t in self.historico.transacoes if t["tipo"] == Saque.__name__]
        )

        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        elif numero_saques >= self._limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        titular = getattr(self.cliente, 'nome', getattr(self.cliente, 'razao_social', ''))
        return f"""
        Agência:\t{self.agencia}
        C/C:\t\t{self.numero}
        Titular:\t{titular}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):  # Executa o depósito e retorna True/False
            conta.historico.adicionar_transacao(self)
            
def menu():
    return input(textwrap.dedent("""\
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """))


def filtrar_cliente(cpf=None, cnpj=None, clientes=[]):
    for cliente in clientes:
        if cpf and getattr(cliente, 'tipo', None) == "PF" and cliente.cpf == cpf:
            return cliente
        elif cnpj and getattr(cliente, 'tipo', None) == "PJ" and cliente.cnpj == cnpj:
            return cliente
    return None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None
    return cliente.contas[0]


def depositar(clientes):
    tipo = input("Informe se a conta é CPF ou CNPJ. 1 para CPF // 2 para CNPJ: ")

    cpf = cnpj = None
    if tipo == "1":
        cpf = input("Informe o CPF do cliente: ")
    elif tipo == "2":
        cnpj = input("Informe o CNPJ do cliente: ")
    else:
        print("Tipo inválido.")
        return

    cliente = filtrar_cliente(cpf=cpf, cnpj=cnpj, clientes=clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return

    # Verifica se o cliente possui contas
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))

    transacao = Deposito(valor)
    cliente.contas[0].adicionar_transacao(transacao)

def sacar(clientes):
    tipo = input("Informe se a conta é CPF ou CNPJ. 1 para CPF // 2 para CNPJ: ")

    cpf = cnpj = None
    if tipo == "1":
        cpf = input("Informe o CPF do cliente: ")
    elif tipo == "2":
        cnpj = input("Informe o CNPJ do cliente: ")
    else:
        print("Tipo inválido.")
        return

    cliente = filtrar_cliente(cpf=cpf, cnpj=cnpj, clientes=clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return

    # Verifica se o cliente possui contas
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    valor = float(input("Informe o valor do saque: "))

    transacao = Saque(valor)
    cliente.contas[0].adicionar_transacao(transacao)

def exibir_extrato(clientes):
    tipo = input("Informe se a conta é CPF ou CNPJ. 1 para CPF // 2 para CNPJ: ")

    cpf = cnpj = None
    if tipo == "1":
        cpf = input("Informe o CPF do cliente: ")
    elif tipo == "2":
        cnpj = input("Informe o CNPJ do cliente: ")
    else:
        print("Tipo inválido.")
        return

    cliente = filtrar_cliente(cpf=cpf, cnpj=cnpj, clientes=clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return

    # Verifica se o cliente possui contas
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    print("Extrato:")
    cliente.contas[0].exibir_extrato()

def criar_cliente(clientes):
    tipo = input("Informe se a conta é CPF ou CNPJ. 1 para CPF // 2 para CNPJ: ")

    if tipo == "1":
        cpf = input("Informe o CPF (somente números): ")
        if filtrar_cliente(cpf=cpf, clientes=clientes):
            print("\n@@@ Já existe cliente com esse CPF! @@@")
            return
        nome = input("Nome completo: ")
        nascimento = input("Data de nascimento (dd-mm-aaaa): ")
        endereco = input("Endereço: ")
        cliente = PessoaFisica(nome, nascimento, cpf, endereco)

    elif tipo == "2":
        cnpj = input("Informe o CNPJ (somente números): ")
        if filtrar_cliente(cnpj=cnpj, clientes=clientes):
            print("\n@@@ Já existe cliente com esse CNPJ! @@@")
            return
        razao_social = input("Razão social: ")
        fundacao = input("Data de fundação (dd-mm-aaaa): ")
        endereco = input("Endereço: ")
        cliente = PessoaJuridica(razao_social, fundacao, cnpj, endereco)

    else:
        print("\n@@@ Opção inválida! @@@")
        return

    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    tipo = input("Informe se a conta é CPF ou CNPJ. 1 para CPF // 2 para CNPJ: ")

    cpf = cnpj = None
    if tipo == "1":
        cpf = input("Informe o CPF do cliente: ")
    elif tipo == "2":
        cnpj = input("Informe o CNPJ do cliente: ")
    else:
        print("Tipo inválido. Conta não criada.")
        return

    cliente = filtrar_cliente(cpf=cpf, cnpj=cnpj, clientes=clientes)
    if cliente:
        conta = ContaCorrente.nova_conta(cliente, numero_conta)
        cliente.adicionar_conta(conta)
        contas.append(conta)
        print("=== Conta criada com sucesso! ===")
    else:
        print("Cliente não encontrado. Conta não criada.")


def listar_contas(contas):
    for conta in contas:
        print("=" * 50)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []
    numero_conta = 1

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            criar_conta(numero_conta, clientes, contas)
            numero_conta += 1
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
