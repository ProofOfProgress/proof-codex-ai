"""Phone hub — ADB control of bubble + affiliate Android phones via owner laptop."""

from shorts_bot.phone_hub.adb import AdbError, AdbResult, list_devices, run_adb
from shorts_bot.phone_hub.devices import PhoneSlot, load_phone_slots, slot_for_account
from shorts_bot.phone_hub.jobs import HubJob, enqueue_job, list_jobs

__all__ = [
    "AdbError",
    "AdbResult",
    "HubJob",
    "PhoneSlot",
    "enqueue_job",
    "list_devices",
    "list_jobs",
    "load_phone_slots",
    "run_adb",
    "slot_for_account",
]
