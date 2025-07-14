from dotenv import load_dotenv

from utils.logging import get_logger

logger = get_logger(__name__)


class Config:
    def __init__(self) -> None:
        load_dotenv()
        """ Define yours environment variables here. 
            E.g.:
            self.NUMBER_OF_WORKER_PER_GPU = int(os.getenv('NUMBER_OF_WORKER_PER_GPU'))
        """
