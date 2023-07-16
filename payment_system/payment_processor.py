import time
from threading import Thread

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
from utils.currency import get_exchange_rate
from utils.logger import LOGGER


class PaymentProcessor(Thread):
    """
    Uma classe para representar um processador de pagamentos de um banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do processador de pagamentos.
    bank: Bank
        Banco sob o qual o processador de pagamentos operará.

    Métodos
    -------
    run():
        Inicia thread to PaymentProcessor
    process_transaction(transaction: Transaction) -> TransactionStatus:
        Processa uma transação bancária.
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank


    def run(self):
        """
        Esse método deve buscar Transactions na fila de transações do banco e processá-las 
        utilizando o método self.process_transaction(self, transaction: Transaction).
        Ele não deve ser finalizado prematuramente (antes do banco realmente fechar).
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"Inicializado o PaymentProcessor {self._id} do Banco {self.bank._id}!")
        queue = banks[self.bank._id].transaction_queue

        while self.bank.operating:
            if len(queue) > 0:
                try:
                    self.bank.transaction_lock.acquire()
                    transaction = queue.pop(0)
                    self.bank.transaction_lock.release()
                    LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: id:{transaction._id} origim:{transaction.origin} destino:{transaction.destination} valor: {transaction.amount}" )
                except Exception as err:
                    LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
                else:
                    self.process_transaction(transaction)


        LOGGER.info(f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado.")


    def process_transaction(self, transaction: Transaction) -> TransactionStatus:
        """
        Esse método deverá processar as transações bancárias do banco ao qual foi designado.
        Caso a transferência seja realizada para um banco diferente (em moeda diferente), a 
        lógica para transações internacionais detalhada no enunciado (README.md) deverá ser
        aplicada.
        Ela deve retornar o status da transacão processada.
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !


        LOGGER.info(f"PaymentProcessor {self._id} do Banco {self.bank._id} iniciando processamento da Transaction {transaction._id}!")
        
        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)
        
        origin_count = self.bank.findAccount(transaction.origin[1])
        if transaction.destination[0] == self.bank._id:
            destination_account = self.bank.findAccount(transaction.destination[1])

            if origin_count.withdraw(transaction.amount):
                destination_account.deposit(transaction.amount)
                self.bank.transactions_lock.acquire()
                self.bank.transactions += 1
                self.bank.transactions_lock.release()
                transaction.set_status(TransactionStatus.SUCCESSFUL)

            else:
                transaction.set_status(TransactionStatus.FAILED)
        else:
            amount = transaction.amount*get_exchange_rate(self.bank.currency,transaction.currency)
            taxa = amount*0.1
            amount += taxa

            if origin_count.withdraw(amount):
                account_bank_national = self.bank.getReserveAccount(self.bank.currency)
                account_bank_interneicional = self.bank.getReserveAccount(transaction.currency)
                destination_bank = banks[transaction.destination[0]]
                destination_account = destination_bank.findAccount(transaction.destination[1])

                if account_bank_interneicional.withdraw(transaction.amount):
                    account_bank_national.deposit(amount)
                    destination_account.deposit(transaction.amount)

                    self.bank.lucro_lock.acquire()
                    self.bank.lucro += taxa
                    self.bank.lucro_lock.release()

                    self.bank.transactions_lock.acquire()
                    self.bank.transactions += 1
                    self.bank.transactions_lock.release()
                    
                    transaction.set_status(TransactionStatus.SUCCESSFUL)
                else:
                    origin_count.deposit(amount)
                    transaction.set_status(TransactionStatus.FAILED)
            else:
                transaction.set_status(TransactionStatus.FAILED)

        return transaction.status
