from RouteHandler import create_app

route_handler = create_app() #RouteHandler app


if __name__ == "__main__":
    # if FLASK_RUN_PORT is not empty, 8080 will be used
    # if FLASK_RUN_HOST is not empty, 0.0.0.0 will be used
    route_handler.run(host='0.0.0.0', port=3002, debug=True)