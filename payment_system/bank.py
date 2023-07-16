from typing import Tuple
from threading import  Lock
from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER


class Bank():
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.
    transaction_lock :
        Lock para transaction_queue
    lucro : int
        Lucro total do banco
    lucro_lock : Lock
        Lock para lucro
    transactions : int
        Numero total de transactions
    transactions_lock : Lock
        Lock para transactions

    
    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.
    findAccount(id)
        Retorna conta de id
    getReserveAccount(currency)
        Retorna conta do banco para moeda currency
    customersBalance()
        Calcula saldo total dos clientes
    """

    def __init__(self, _id: int, currency: Currency):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves()
        self.operating          = False
        self.accounts           = []
        self.transaction_queue  = []
        self.transaction_lock = Lock()
        self.lucro = 0
        self.lucro_lock = Lock()
        self.transactions = 0
        self.transactions_lock = Lock()
        

    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado 
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = len(self.accounts) + 1

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)

    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco
        2. Número de transferências nacionais e internacionais realizadas
        3. Número de contas bancárias registradas no banco
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")
        LOGGER.info(f"Saldo USD:{self.reserves.USD.balance} EUR:{self.reserves.EUR.balance} GBP:{self.reserves.GBP.balance} JPY:{self.reserves.JPY.balance} CHF:{self.reserves.CHF.balance} BRL:{self.reserves.BRL.balance}")
        LOGGER.info(f"Transferências: {self.transactions}")
        LOGGER.info(f"Contas: {len(self.accounts)}")
        LOGGER.info(f"Saldo total: {self.customersBalance()}")
        LOGGER.info(f"Lucro do banco: {self.lucro}")
        
    def findAccount(self, id):
        for account in self.accounts:
            if account._id == id:
                return account
        
        return None
    
    def getReserveAccount(self,currency):
        value = currency.name
        if value == 'USD':
            return self.reserves.USD
        elif value == 'EUR':
            return self.reserves.EUR
        elif value == 'GBP':
            return self.reserves.GBP
        elif value == 'JPY':
            return self.reserves.JPY
        elif value == 'CHF':
            return self.reserves.CHF
        elif value == 'BRL':
            return self.reserves.BRL

    def customersBalance(self):
        balance = 0
        for account in self.accounts:
            balance += account.balance

        return balance