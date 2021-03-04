from NutriFit.models import *
from rest_framework import serializers


class MacronutrientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Macronutrientes
        fields = ('id', 'hidratos_carbono', 'proteina', 'gordura')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'nome')


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        fields = ('id', 'nome', 'calorias', 'categoria', 'macro_nutrientes')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'peso', 'altura', 'idade', 'sexo', 'objetivo', 'imc', 'ci', 'atividade')


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refeicao
        fields = ('id', 'nome', 'data', 'alimentos', 'utilizador')


class ComposedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composta
        fields = ('id', 'quantidade', 'alimento', 'refeicao')


######custom serializers#########
class newUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150)
    peso = serializers.DecimalField(max_digits=5, decimal_places=2)
    altura = serializers.IntegerField()
    idade = serializers.IntegerField()
    sexo = serializers.CharField(max_length=20)
    objetivo = serializers.CharField(max_length=20)
    atividade = serializers.CharField(max_length=40)


class imcSerializer(serializers.Serializer):
    peso = serializers.DecimalField(max_digits=5, decimal_places=2)
    altura = serializers.IntegerField()
    idade = serializers.IntegerField()


class ciSerializer(serializers.Serializer):
    peso = serializers.DecimalField(max_digits=5, decimal_places=2)
    altura = serializers.IntegerField()
    idade = serializers.IntegerField()
    atividade = serializers.CharField(max_length=40)


class foodWithMacroSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=30)
    calorias = serializers.IntegerField()
    categoria = serializers.CharField(max_length=30)
    hidratos_carbono = serializers.DecimalField(max_digits=4, decimal_places=1)
    proteina = serializers.DecimalField(max_digits=4, decimal_places=1)
    gordura = serializers.DecimalField(max_digits=4, decimal_places=1)
