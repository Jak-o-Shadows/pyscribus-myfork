Draw a wireframe of a file
--------------------------

  ::

   import pyscribus.sla as sla
   import pyscribus.extra.wireframe as wire

   slafile = sla.SLA("wireframe_example.sla", "1.5.5")

   wireframe = wire.Wireframe()
   wireframe.from_sla(slafile)

   wireframe.draw(
       output="wireframe_example.png",
       stylesheet=True,
       margins=[10, 10]
   )

.. figure:: ../_static/logo.png
   :align: center
   :scale: 15%

   Original SLA file

.. figure:: ../_static/logo.png
   :align: center
   :scale: 15%

   Wireframe
