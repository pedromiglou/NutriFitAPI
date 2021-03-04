from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Macronutrientes(models.Model):
    hidratos_carbono = models.DecimalField(max_digits=4,decimal_places=1,default="")
    proteina = models.DecimalField(max_digits=4,decimal_places=1,default="")
    gordura = models.DecimalField(max_digits=4,decimal_places=1,default="")


class Categoria(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return self.nome


class Alimento(models.Model):
    nome = models.CharField(max_length=30)
    calorias = models.IntegerField()
    categoria = models.OneToOneField(Categoria, on_delete=models.CASCADE)
    macro_nutrientes = models.OneToOneField(Macronutrientes, on_delete=models.CASCADE)
    verificado = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
    altura = models.IntegerField(blank=True, null=True)
    idade = models.IntegerField(blank=True, null=True)
    sexo = models.CharField(max_length=20,blank=True, null=True)
    objetivo = models.CharField(max_length=20,blank=True, null=True)
    imc = models.DecimalField(max_digits=4, decimal_places=2,blank=True, null=True)
    ci = models.IntegerField(blank=True, null=True)
    atividade = models.CharField(max_length=40,blank=True, null=True)

    def __str__(self):
          return self.user.username

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()


class Refeicao(models.Model):
    nome = models.CharField(max_length=30)
    data = models.DateField()
    alimentos = models.ManyToManyField(Alimento, through="Composta")
    utilizador = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

#ligacao entre Refeicao e Alimento
class Composta(models.Model):
    quantidade = models.IntegerField()
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    refeicao = models.ForeignKey(Refeicao, on_delete=models.CASCADE)