from datetime import datetime
import time
import configparser
import os.path
import subprocess

# Autor této funkce: Pavel Dušek
def _read_sectionless_ini(filepath) -> dict:
    config = configparser.ConfigParser()
    config.optionxform=str
    with open(filepath) as file:
        conf = file.read()
    config.read_string(f"[DEFAULT]\n{conf}")
    return dict(config['DEFAULT'])

def get_task_list():
    # Přečti ../../BotConfig/Tasks.ini, získej seznam URL úkonů
    return list(_read_sectionless_ini('../../BotConfig/Tasks.ini').keys())

def get_task_config(task_id):
    # Přečti hodnoty nastavení v ../../BotConfig/Tasks/{TASK_ID}/TaskConfig.ini
    return _read_sectionless_ini('../../BotConfig/Tasks/' + task_id + '/TaskConfig.ini')

def is_task_running(task_id):
    # Zkontroluj, zda existuje soubor {TASK_ID}/!running
    return os.path.isfile(task_id + '/!running')

def set_task_as_running(task_id):
    # Vytvoř soubor {TASK_ID}/!running
    with open(task_id + '/!running', 'w') as fp:
        pass

def set_task_as_finished(task_id):
    # Odstraň soubor {TASK_ID}/!running
    os.remove(task_id + '/!running')

def is_task_queued(task_id):
    # Zkontroluj zda soubor taskqueue obsahuje řádek s hodnotou {TASK_ID}
    with open("taskqueue", "r") as file:
        for line in file.readlines():
            if line.strip() == task_id:
                return True

def enqueue_task(task_id):
    # Přidej na konec souboru taskqueue řádek s hodnotou {TASK_ID}
    with open('taskqueue', 'a') as file:
        file.write(task_id + "\n")

def dequeue_task(task_id):
    # Odstraň ze souboru taskqueue první řádek obsahující hodnotu {TASK_ID}
    with open('taskqueue', 'r') as fin:
        data = fin.read().splitlines(True)
    with open('taskqueue', 'w') as fout:
        fout.writelines(data[1:])

def get_task_last_run_timestamp(task_id):
    # Přečti hodnotou v {TASK_URL}/lastrun
    with open(task_id + '/lastrun', "r") as time_file:
        return int(time_file.read().strip())

def update_task_last_run_timestamp(task_id):
    # Přepiš hodnotou v {TASK_URL}/lastrun
    with open(task_id + '/lastrun', "w") as time_file:
        time_file.write(str(int(time.time())))

def get_next_nonrunning_task_from_queue():
    # Načti první řádek ze souboru taskqueue ({TASK_ID}) a zkontroluj, zda již běží. Pokud ano, pokračuj na další řádek souboru taskqueue
    with open("taskqueue", "r") as file:
        for line in file.readlines():
            if not is_task_running(line):
                return line.strip()
    return None;

def run_task_queue_filling(task_id):
    # Spusť {TASK_ID}/fill_queue.py, výstup ulož do logovacích souborů
    log_file_path = os.path.join("../../BotLog/Tasks/" + task_id, datetime.now().strftime("%Y-%m-%d_%H-%M-%S_queuefilling.log"))
    err_log_file_path = os.path.join("../../BotLog/Tasks/" + task_id, "Errors.tsv")
    with open(log_file_path, 'a') as run_log, open(err_log_file_path, 'a') as error_log:
        process = subprocess.Popen(
            ['python3', task_id + '/fill_queue.py', '-dir:/var/www/html/WikiBots/Bot'],
            stdout=run_log,
            stderr=error_log
        )
    process.wait()

def run_task_queue_processing(task_id):
    # Spusť {TASK_ID}/process_queue.py, výstup ulož do logovacích souborů
    log_file_path = os.path.join("../../BotLog/Tasks/" + task_id, datetime.now().strftime("%Y-%m-%d_%H-%M-%S_processing.log"))
    err_log_file_path = os.path.join("../../BotLog/Tasks/" + task_id, "Errors.tsv")
    with open(log_file_path, 'a') as run_log, open(err_log_file_path, 'a') as error_log:
        process = subprocess.Popen(
            ['python3', task_id + '/process_queue.py', '-dir:/var/www/html/WikiBots/Bot'],
            stdout=run_log,
            stderr=error_log
        )
    process.wait()

