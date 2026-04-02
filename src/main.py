import uvicorn

from src.conf.app_config import get_uvicorn_config


def main() -> None:
    """
    Main entry point for the application.
    """
    cfg = get_uvicorn_config()
    uvicorn.run(
        "src.app:app",
        host=cfg.HOST,
        port=cfg.PORT,
        reload=cfg.RELOAD,
        log_level=cfg.LOG_LEVEL,
    )


if __name__ == "__main__":
    main()
