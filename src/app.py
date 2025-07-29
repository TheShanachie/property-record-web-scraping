import server, os
if __name__ == '__main__':
    server.app.run(
        debug=False,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        threaded=True
    )