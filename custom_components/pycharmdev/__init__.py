# noinspection DuplicatedCode
import logging
import socket
from typing import Optional

import asyncio
import voluptuous as vol

from homeassistant.components import debugpy
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType

DOMAIN = "pycharmdev"

CONFIG_SCHEMA = debugpy.CONFIG_SCHEMA

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up pycharmdev integration."""
    _LOGGER.debug("Begin setup PyCharm Remote Debugger")
    conf = config[DOMAIN]

    host = conf[debugpy.CONF_HOST]
    port = conf[debugpy.CONF_PORT]
    start = conf[debugpy.CONF_START]
    wait = conf[debugpy.CONF_WAIT]

    try:
        import pydevd_pycharm
        from pydevd import connected, stoptrace
        from _pydevd_bundle.pydevd_constants import DebugInfoHolder, get_global_debugger
    except ImportError:
        _LOGGER.exception("Unable to import necessary modules")
        return False

    # noinspection PyUnusedLocal
    async def debug_start(call: Optional[ServiceCall] = None) -> None:
        """Start the debugger."""
        _LOGGER.info(f"Activating PyCharm Remote Debugger for {host}:{port}")

        debugger = get_global_debugger()
        if debugger:
            _LOGGER.warning(f"Found running PyDB instance, stopping it now")
            _LOGGER.debug(f"connected={connected}")
            stoptrace()

            while connected:
                await asyncio.sleep(0.1)

        # DebugInfoHolder.DEBUG_RECORD_SOCKET_READS = True
        # DebugInfoHolder.DEBUG_TRACE_BREAKPOINTS = 3
        # DebugInfoHolder.DEBUG_TRACE_LEVEL = 3

        try:
            pydevd_pycharm.settrace(
                host=host,
                port=port,
                stdoutToServer=False,
                stderrToServer=False,
                suspend=wait,
                trace_only_current_thread=False,
                patch_multiprocessing=False,
            )
        except (ConnectionRefusedError, OSError, socket.gaierror) as e:
            _LOGGER.warning("Failed to connect Remote Debugger with PyCharm IDE")

    async_register_admin_service(
        hass, DOMAIN, debugpy.SERVICE_START, debug_start, schema=vol.Schema({})
    )

    # If set to start the debugger on startup, do so
    if start:
        await debug_start()

    return True
