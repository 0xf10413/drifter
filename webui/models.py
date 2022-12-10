from django.db import models

class MachType(models.Model):
    name = models.CharField(max_length=10)

class Phase(models.Model):
    name = models.CharField(max_length=100)

class Server(models.Model):
    mach_type = models.ForeignKey(MachType, on_delete=models.PROTECT)
    phase = models.ForeignKey(Phase, on_delete=models.PROTECT)
