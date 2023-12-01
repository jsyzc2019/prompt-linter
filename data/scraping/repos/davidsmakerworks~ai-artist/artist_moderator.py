# MIT License

# Copyright (c) 2023 David Rice

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging

import openai

from log_config import get_logger_name

logger = logging.getLogger(get_logger_name())


class ArtistModerator:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def check_msg(self, msg: str) -> bool:
        """
        Check if a message complies with content policy.

        Returns True if message is safe, False if it is not.
        """
        try:
            response = openai.Moderation.create(api_key=self.api_key, input=msg)
        except Exception as e:
            logger.error(f"Moderation response: {response}")
            logger.exception(e)
            raise

        flagged = response["results"][0]["flagged"]

        if flagged:
            logger.info(f"Message flagged by moderation: {msg}")
            logger.info(f"Moderation response: {response}")
        else:
            logger.info(f"Moderation check passed")

        return not flagged
