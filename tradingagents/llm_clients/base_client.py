from abc import ABC, abstractmethod
from typing import Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        self.model = model
        self.base_url = base_url
        self.kwargs = kwargs
        # 默认超时120秒，可配置
        self.invoke_timeout = kwargs.get("invoke_timeout", 120)

    @abstractmethod
    def get_llm(self) -> Any:
        """Return the configured LLM instance."""
        pass

    @abstractmethod
    def validate_model(self) -> bool:
        """Validate that the model is supported by this client."""
        pass

    def invoke_with_timeout(self, messages: Any, max_retries: int = 2) -> Any:
        """
        调用LLM并设置超时保护
        """
        llm = self.get_llm()
        last_exception: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(llm.invoke, messages)
                    result = future.result(timeout=self.invoke_timeout)
                    if attempt > 0:
                        logger.info(f"[LLM_RETRY_SUCCESS] 第{attempt + 1}次尝试成功")
                    return result
            except FutureTimeoutError:
                logger.warning(f"[LLM_TIMEOUT] 第{attempt + 1}次尝试超时({self.invoke_timeout}s)")
                last_exception = TimeoutError(f"LLM调用超时({self.invoke_timeout}s)")
            except Exception as e:
                logger.error(f"[LLM_ERROR] 第{attempt + 1}次尝试失败: {e}")
                last_exception = e

        if last_exception is not None:
            raise last_exception
        raise TimeoutError(f"LLM调用失败，已重试{max_retries}次")
