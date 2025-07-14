import multiprocessing
import sys
import threading
import traceback

from utils.logging import get_logger


def join_thread_with_timeout(
    thread_or_process: threading.Thread | multiprocessing.Process,
    timeout: float = 5.0,
) -> bool:
    """
    Join a thread or process with timeout, deadlock detection, and retry logic.
    If the thread/process cannot be joined after all retries, the entire process will be
    terminated as this indicates a serious issue that requires immediate attention.

    Args:
        thread_or_process: The thread or process to join
        timeout: Initial timeout in seconds for each join attempt
    Returns:
        bool: True if thread/process was successfully joined, False if process was terminated
    """
    if not thread_or_process or not thread_or_process.is_alive():
        return True

    is_process = isinstance(thread_or_process, multiprocessing.Process)
    target_type = "Process" if is_process else "Thread"
    target_id = thread_or_process.name or str(thread_or_process.ident)
    logger = get_logger(__name__, {"job": target_id})

    attempt = 0
    while True:
        try:
            logger.info(f"Attempting to join {target_type} {target_id} (attempt {attempt + 1})")
            thread_or_process.join(timeout=timeout)

            if not thread_or_process.is_alive():
                logger.info(f"Successfully joined {target_type} {target_id}")
                return True

            logger.warning(f"{target_type} {target_id} did not join within {timeout}s timeout. ")
            current_frames = sys._current_frames()
            if thread_or_process.ident in current_frames:
                current_frame = current_frames[thread_or_process.ident]
                logger.warning(
                    f"{target_type=} {target_id=} stack trace:\n{''.join(traceback.format_stack(current_frame))}"
                )
            else:
                logger.warning(f"{target_type=} {target_id=} is not in current frames")

        except Exception as e:
            logger.error(f"Error joining {target_type} {target_id}: {str(e)}", exc_info=True)
        finally:
            attempt += 1


def join_thread_with_timeout_async(
    thread_or_process: threading.Thread | multiprocessing.Process,
    timeout: float = 5.0,
) -> threading.Thread:
    """
    Asynchronously join a thread or process with timeout, deadlock detection, and retry logic.
    The join operation runs in a daemon thread to avoid blocking the main thread.

    Args:
        thread_or_process: The thread or process to join
        timeout: Initial timeout in seconds for each join attempt
    Returns:
        threading.Thread: The daemon thread that is performing the join operation
    """
    join_thread = threading.Thread(
        target=join_thread_with_timeout,
        args=(thread_or_process, timeout),
        name=f"join_thread_{thread_or_process.name or thread_or_process.ident}",
        daemon=True,
    )
    join_thread.start()
    return join_thread
