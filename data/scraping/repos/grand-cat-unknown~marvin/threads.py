import asyncio
from typing import TYPE_CHECKING, Callable, Optional

from openai.types.beta.threads import ThreadMessage
from pydantic import BaseModel, Field

from marvin.beta.assistants.formatting import pprint_message
from marvin.utilities.asyncio import (
    ExposeSyncMethodsMixin,
    expose_sync_method,
)
from marvin.utilities.logging import get_logger
from marvin.utilities.openai import get_client
from marvin.utilities.pydantic import parse_as

logger = get_logger("Threads")

if TYPE_CHECKING:
    from .assistants import Assistant
    from .runs import Run


class Thread(BaseModel, ExposeSyncMethodsMixin):
    id: Optional[str] = None
    metadata: dict = {}
    messages: list[ThreadMessage] = Field([], repr=False)

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()
        # If an exception has occurred, you might want to handle it or pass it through
        # Returning False here will re-raise any exception that occurred in the context
        return False

    @expose_sync_method("create")
    async def create_async(self, messages: list[str] = None):
        """
        Creates a thread.
        """
        if self.id is not None:
            raise ValueError("Thread has already been created.")
        if messages is not None:
            messages = [{"role": "user", "content": message} for message in messages]
        client = get_client()
        response = await client.beta.threads.create(messages=messages)
        self.id = response.id
        return self

    @expose_sync_method("add")
    async def add_async(
        self, message: str, file_paths: Optional[list[str]] = None
    ) -> ThreadMessage:
        """
        Add a user message to the thread.
        """
        client = get_client()

        if self.id is None:
            await self.create_async()

        # Upload files and collect their IDs
        file_ids = []
        for file_path in file_paths or []:
            with open(file_path, mode="rb") as file:
                response = await client.files.create(file=file, purpose="assistants")
                file_ids.append(response.id)

        # Create the message with the attached files
        response = await client.beta.threads.messages.create(
            thread_id=self.id, role="user", content=message, file_ids=file_ids
        )
        return ThreadMessage.model_validate(response.model_dump())

    @expose_sync_method("get_messages")
    async def get_messages_async(
        self,
        limit: int = None,
        before_message: Optional[str] = None,
        after_message: Optional[str] = None,
    ):
        if self.id is None:
            await self.create_async()
        client = get_client()

        response = await client.beta.threads.messages.list(
            thread_id=self.id,
            # note that because messages are returned in descending order,
            # we reverse "before" and "after" to the API
            before=after_message,
            after=before_message,
            limit=limit,
            order="desc",
        )

        return parse_as(list[ThreadMessage], reversed(response.model_dump()["data"]))

    @expose_sync_method("delete")
    async def delete_async(self):
        client = get_client()
        await client.beta.threads.delete(thread_id=self.id)
        self.id = None

    @expose_sync_method("run")
    async def run_async(
        self,
        assistant: "Assistant",
        **run_kwargs,
    ) -> "Run":
        """
        Creates and returns a `Run` of this thread with the provided assistant.
        """
        if self.id is None:
            await self.create_async()

        from marvin.beta.assistants.runs import Run

        run = Run(assistant=assistant, thread=self, **run_kwargs)
        return await run.run_async()


class ThreadMonitor(BaseModel, ExposeSyncMethodsMixin):
    thread_id: str
    _thread: Thread
    last_message_id: Optional[str] = None
    on_new_message: Callable = Field(default=pprint_message)

    @property
    def thread(self):
        return self._thread

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._thread = Thread(id=kwargs["thread_id"])

    @expose_sync_method("run_once")
    async def run_once_async(self):
        messages = await self.get_latest_messages()
        for msg in messages:
            if self.on_new_message:
                self.on_new_message(msg)

    @expose_sync_method("run")
    async def run_async(self, interval_seconds: int = None):
        if interval_seconds is None:
            interval_seconds = 1
        if interval_seconds < 1:
            raise ValueError("Interval must be at least 1 second.")

        while True:
            try:
                await self.run_once_async()
            except KeyboardInterrupt:
                logger.debug("Keyboard interrupt received; exiting thread monitor.")
                break
            except Exception as exc:
                logger.error(f"Error refreshing thread: {exc}")
            await asyncio.sleep(interval_seconds)

    async def get_latest_messages(self) -> list[ThreadMessage]:
        limit = 20

        # Loop to get all new messages in batches of 20
        while True:
            messages = await self.thread.get_messages_async(
                after_message=self.last_message_id, limit=limit
            )

            # often the API will retrieve messages that have been created but
            # not populated with text. We filter out these empty messages.
            filtered_messages = []
            for i, msg in enumerate(messages):
                skip_message = False
                for c in msg.content:
                    if getattr(getattr(c, "text", None), "value", None) == "":
                        skip_message = True
                if not skip_message:
                    filtered_messages.append(msg)

            if filtered_messages:
                self.last_message_id = filtered_messages[-1].id

            if len(messages) < limit:
                break

        return filtered_messages

    # async def refresh_messages_async(self) -> list[ThreadMessage]:
    #     """
    #     Asynchronously refreshes and updates the message list.

    #     This function fetches the latest messages up to a specified limit and
    #     checks if the latest message in the current message list
    #     (`self.messages`) is included in the new batch. If the latest message is
    #     missing, it continues to fetch additional messages in batches, up to a
    #     maximum count, using pagination. The function then updates
    #     `self.messages` with these new messages, ensuring any existing messages
    #     are updated with their latest versions and new messages are appended in
    #     their original order.
    #     """

    #     new_messages = []

    #     # fetch up to 100 messages
    #     max_fetched = 100
    #     limit = 50
    #     max_attempts = max_fetched / limit + 2

    #     # Fetch the latest messages
    #     messages = await self.get_messages_async(limit=limit)

    #     if not messages:
    #         return

    #     # Check if the latest message in self.messages is in the new messages
    #     latest_message_id = self.messages[-1].id if self.messages else None
    #     missing_latest = (
    #         latest_message_id not in {m.id for m in messages}
    #         if latest_message_id
    #         else True
    #     )

    #     # If the latest message is missing, fetch additional messages
    #     total_fetched = len(messages)
    #     attempts = 0
    #     while (
    #         messages
    #         and missing_latest
    #         and total_fetched < max_fetched
    #         and attempts < max_attempts
    #     ):
    #         attempts += 1
    #         paginated_messages = await self.get_messages_async(
    #             limit=limit, before_message=messages[0].id
    #         )
    #         total_fetched += len(paginated_messages)
    #         # prepend messages
    #         messages = paginated_messages + messages
    #         if any(m.id == latest_message_id for m in paginated_messages):
    #             missing_latest = False

    #     # Update self.messages with the latest data
    #     new_messages_dict = {m.id: m for m in messages}
    #     for i in range(len(self.messages) - 1, -1, -1):
    #         if self.messages[i].id in new_messages_dict:
    #             self.messages[i] = new_messages_dict.pop(self.messages[i].id)
    #         else:
    #             break
    #     # Append remaining new messages at the end in their original order
    #     self.messages.extend(new_messages_dict.values())

    #     return messages
