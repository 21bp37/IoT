from pisklak import create_app, app_socketio
if __name__ == '__main__':
    app = create_app()
    app_socketio.run(app)