from __init__ import create_app

sla_manager = create_app() 


if __name__ == "__main__":
    # if FLASK_RUN_PORT is not empty, 8080 will be used
    # if FLASK_RUN_HOST is not empty, 0.0.0.0 will be used
    sla_manager.run(host='0.0.0.0', port=5000)