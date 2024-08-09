# main.py
import app


if __name__ == '__main__':
    # Configuração do logging
    # logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    # try:
    # Inicialização do aplicativo Flask

    app.flask_app.run(host='0.0.0.0', debug=True)
# except Exception as e:
# Em caso de exceção, registre a mensagem de erro no log
# logging.exception('Error occurred: %s', str(e))
