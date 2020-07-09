import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "debug_host"
CONF_PORT = "debug_port"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 15678
DOMAIN = "pycharmdev"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST, default=DEFAULT_HOST): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SCHEMA = vol.Schema({})


async def async_setup(hass, config):
    """Set up pycharmdev integration."""
    _LOGGER.debug("Begin setup PyCharm Remote Debugger")
    conf = config.get(DOMAIN)
    if conf is None:
        conf = CONFIG_SCHEMA({DOMAIN: {}})[DOMAIN]

    host = conf[CONF_HOST]
    port = conf[CONF_PORT]

    async def async_start_debugger(service):
        try:
            import pydevd_pycharm

            _LOGGER.info(f"Activating PyCharm Remote Debugger for {host}:{port}")
            pydevd_pycharm.settrace(
                host=host,
                port=port,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
                patch_multiprocessing=False,
            )
        except Exception as e:
            _LOGGER.error("Failed to setup PyCharm Remote Debugger:\n%s", e)

    hass.services.async_register(
        DOMAIN, "start", async_start_debugger, schema=SERVICE_SCHEMA
    )

    return True
