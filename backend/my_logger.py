import logging

logger_name = __file__.split("\\")[-1].split(".")[0]


# Configure custom logger
def config_logger(name=logger_name, level=logging.DEBUG, fname="my_app.log"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    file_handler = logging.FileHandler(fname)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger