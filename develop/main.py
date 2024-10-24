from telegram.ext import Application
from controller import Controller

def read_token_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def main():
    token = read_token_from_file('../config.txt')
    application = Application.builder().token(token).build()

    Controller(application)

    application.run_polling()

if __name__ == '__main__':
    main()
