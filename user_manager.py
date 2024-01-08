from UserManager import create_app

user_management = create_app() #UserManagement app


if __name__ == "__main__":
    # if FLASK_RUN_PORT is not empty, 8080 will be used
    # if FLASK_RUN_HOST is not empty, 0.0.0.0 will be used
    user_management.run(host='0.0.0.0', port=3001, debug=True)