import uvicorn

#if __name__ == '__main__':
 #   uvicorn.run('app:app', host="127.0.0.1", port=8000, reload=True)
uvicorn.run(
        app= "app:app",
        reload = False,
        workers=1,
        port=8000,
        host="0.0.0.0",
        log_config=None,
        ws_max_size=167772160,
        h11_max_incomplete_event_size=167772160,
)

   