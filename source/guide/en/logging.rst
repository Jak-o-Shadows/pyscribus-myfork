PyScribus logging
=================

Activation
----------

  ::

   import pyscribus.logs as logs

   # Initialize the logs
   logs.init_logging("mylog.log", "%(asctime)s:%(message)s")

   # From now, if PyScribus want to log something, it will log
   # to mylog.log instead of printing on STDOUT

   # Changing the level of the logger used by PyScribus
   logger = logs.getLogger()

Configuration
----------

The logger used by PyScribus is a standard library logger (from ``logging`` 
module). By default, this logger is verbose, as its logs every level of 
messages (starting from ``logging.DEBUG``).

  ::

   import logging
   import pyscribus.logs as logs

   # Initialize the logs
   logs.init_logging("mylog.log", "%(asctime)s:%(levelname)s:%(message)s")

   # Get the logger used by PyScribus
   logger = logs.getLogger()

   # Changing the level of the logger
   logger.setLevel(logging.WARNING)
