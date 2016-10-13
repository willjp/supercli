#!/usr/bin/env python
import supercli.logging
import logging

logger = logging.getLogger(__name__)

supercli.logging.SetLog('v')
logger.info('test info')
logger.warning('test warning')
logger.error('test error')

