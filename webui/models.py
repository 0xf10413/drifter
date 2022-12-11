from django.db import models

class MachType(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name

class Phase(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class Server(models.Model):
    mach_type = models.ForeignKey(MachType, on_delete=models.PROTECT)
    phase = models.ForeignKey(Phase, on_delete=models.PROTECT)
    name = models.CharField(max_length=256, null=False)

    def __str__(self) -> str:
        return self.name

class NbChanges(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    nb_change = models.IntegerField()

    class Meta:
        unique_together = ("server", "datetime")
