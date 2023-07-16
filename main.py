import argparse, time, sys
import threading
from logging import INFO, DEBUG
from random import randint
from globals import *
from payment_system.bank import Bank
from payment_system.payment_processor import PaymentProcessor
from payment_system.transaction_generator import TransactionGenerator
from utils.currency import Currency
from utils.logger import CH, LOGGER
from datetime import datetime, timedelta


if __name__ == "__main__":
    # Verificação de compatibilidade da versão do python:
    if sys.version_info < (3, 5):
        sys.stdout.write('Utilize o Python 3.5 ou mais recente para desenvolver este trabalho.\n')
        sys.exit(1)

    # Captura de argumentos da linha de comando:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_unit", "-u", help="Valor da unidade de tempo de simulação")
    parser.add_argument("--total_time", "-t", help="Tempo total de simulação")
    parser.add_argument("--debug", "-d", help="Printar logs em nível DEBUG")
    parser.add_argument("--processors", "-p", help="Numero de paymentProcessor")
    args = parser.parse_args()
    if args.time_unit:
        time_unit = float(args.time_unit)
    if args.total_time:
        total_time = int(args.total_time)
    if args.debug:
        debug = True
    if args.processors:
        n_paymentProcessor = int(args.processors)

    # Configura logger
    if debug:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(DEBUG)
    else:
        LOGGER.setLevel(INFO)
        CH.setLevel(INFO)

    # Printa argumentos capturados da simulação
    LOGGER.info(f"Iniciando simulação com os seguintes parâmetros:\n\ttotal_time = {total_time}\n\tdebug = {debug}\n")
    time.sleep(3)

    # Inicializa variável `tempo`:
    t = 0
    
    # Cria os Bancos Nacionais e popula a lista global `banks`:
    for i, currency in enumerate(Currency):
        
        # Cria Banco Nacional
        bank = Bank(_id=i, currency=currency)
        
        # Deposita valores aleatórios nas contas internas (reserves) do banco
        bank.reserves.BRL.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.CHF.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.EUR.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.GBP.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.JPY.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.USD.deposit(randint(100_000_000, 10_000_000_000))
        
        # Adiciona banco na lista global de bancos
        banks.append(bank)

    # Inicializa gerador de transações e processadores de pagamentos para os Bancos Nacionais:
    for i, bank in enumerate(banks):
        bank.operating = True
        # Inicializa um TransactionGenerator thread por banco:
        TransactionGenerator(_id=i, bank=bank).start()
        # Inicializa um PaymentProcessor thread por banco.
        # Sua solução completa deverá funcionar corretamente com múltiplos PaymentProcessor threads para cada banco.
        for i in range(n_paymentProcessor):
            PaymentProcessor(_id=i, bank=bank).start()
    
    # Enquanto o tempo total de simuação não for atingido:
    while t < total_time:
        # Aguarda um tempo aleatório antes de criar o próximo cliente:
        dt = randint(0, 3)
        time.sleep(dt * time_unit)
        bank = banks[randint(0, 5)]
        cash = randint(1_000, 10_000_000)
        bank.new_account(cash, cash*0.1)
        # Atualiza a variável tempo considerando o intervalo de criação dos clientes:
        t += dt

    # Finaliza todas as threads
    for bank in banks:
        bank.operating = False

    finished_at = datetime.now()

    for thread in threading.enumerate():
        if thread != threading.main_thread():
            thread.join()
    
    # Termina simulação. Após esse print somente dados devem ser printados no console.
    LOGGER.info(f"A simulação chegou ao fim!\n")

    # Print quantidade de transaction que não foram processada e media de tempo de espera.
    transations = 0
    total_time = finished_at - finished_at
    for bank in banks:
        transations += len(bank.transaction_queue)
        for transation in bank.transaction_queue:
            total_time += finished_at - transation.created_at 

    media_time = total_time/transations
    LOGGER.info(f"Total Transations não processadas: {transations}")
    LOGGER.info(f"Media tempo de espera: {media_time}")

    # Info Banks.
    for bank in banks:
        bank.info()