from typing import Dict, Optional
import logging
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class DataSourceConfig:
    api_key: str
    endpoint: str
    max_retries: int = 3
    retry_delay: float = 1.0  # in seconds

class DataCollectionError(Exception):
    pass

class SARGEDataCollector:
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def fetch_data(self) -> Dict:
        """Fetches real-time data from the configured API endpoint."""
        try:
            for _ in range(self.config.max_retries):
                response = requests.get(
                    self.config.endpoint,
                    headers={'Authorization': f'Bearer {self.config.api_key}'}
                )
                if response.status_code == 200:
                    return response.json()
                self.logger.warning(f"Retrieved status code: {response.status_code}")
                delay = min(2**_, self.config.retry_delay)
                await self._delay(delay)
            raise DataCollectionError("Max retries exceeded")
        except Exception as e:
            self.logger.error(f"Data collection failed: {str(e)}")
            raise

    async def _delay(self, seconds: float) -> None:
        """Introduces a delay with logging."""
        self.logger.debug(f"Delaying for {seconds} seconds...")
        await asyncio.sleep(seconds)

    async def process_data(self, data: Dict) -> Dict:
        """Processes and enriches the collected data."""
        processed = {
            'timestamp': datetime.now().isoformat(),
            'raw_data': data
        }
        return processed

    async def collect_and_process(self) -> Dict:
        """Main method to collect and process data."""
        raw_data = await self.fetch_data()
        processed_data = await self.process_data(raw_data)
        return processed_data

# Example usage:
if __name__ == "__main__":
    config = DataSourceConfig(
        api_key="your_api_key_here",
        endpoint="https://api.example.com/data"
    )
    collector = SARGEDataCollector(config)
    try:
        data = collector.collect_and_process()
        print("Collected Data:", data)
    except Exception as e:
        print(f"Error occurred: {str(e)}")