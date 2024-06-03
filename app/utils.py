import logging

import streamlit as st
from cachetools import cached

logger = logging.getLogger(__name__)


@cached(cache={})
def get_app_custom_config(arg):
    default_values = {
        "debug": False,
        "count": 10,
        "sleep_time": 55 * 60,  # update cache 5 minutes before cache's TTL
        "thread_details": False,
        "cache_updater_details": False,
    }
    if arg in default_values:
        value = (
            st.secrets.config.get(arg)
            if (st.secrets.has_key("config") and st.secrets.config.get(arg))
            else default_values[arg]
        )
        return value
    else:
        raise KeyError(f"Invalid config parameter {arg}")
