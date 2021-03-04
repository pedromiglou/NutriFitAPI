from datetime import date
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from NutriFit.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# funcoes auxiliares
def calculateBMI(weight, height):
    weight = float(weight)
    height = float(height)
    height = height / 100
    bmi = weight / (height * height)
    bmi = round(bmi, 2)
    return bmi


def calculateCI(sex, weight, height, age, activity, objective):
    weight = float(weight)
    height = float(height)
    age = float(age)
    bmr = 0
    if sex == 'male':
        bmr = 66.4730 + (13.7516 * weight) + (5.0033 * height) - (6.7550 * age)
    elif sex == 'female':
        bmr = 655.0955 + (9.5634 * weight) + (1.8496 * height) - (4.6756 * age)

    caloric_intake = 0
    if activity == 'none':
        caloric_intake = bmr * 1.2
    elif activity == 'light':
        caloric_intake = bmr * 1.375
    elif activity == 'moderate':
        caloric_intake = bmr * 1.55
    elif activity == 'heavy':
        caloric_intake = bmr * 1.725
    elif activity == 'very_heavy':
        caloric_intake = bmr * 1.9

    caloric_intake = round(caloric_intake)

    if objective == 'gain':
        return caloric_intake + 500
    elif objective == 'maintain':
        return caloric_intake
    elif objective == 'lose':
        return caloric_intake - 500


# Create your views here.

# post to create account
@api_view(['POST'])
def register_user(request):
    serializer = newUserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(serializer.data['username'], serializer.data['email'],
                                        serializer.data['password'])
        user.first_name = serializer.data['first_name']
        user.last_name = serializer.data['last_name']

        user.profile.altura = serializer.data['altura']
        user.profile.peso = float(serializer.data['peso'])
        user.profile.idade = serializer.data['idade']
        user.profile.sexo = serializer.data['sexo']
        user.profile.objetivo = serializer.data['objetivo']
        user.profile.atividade = serializer.data['atividade']

        # get imc
        user.profile.imc = calculateBMI(user.profile.peso, user.profile.altura)

        # get caloric intake
        user.profile.ci = calculateCI(user.profile.sexo, user.profile.peso, user.profile.altura, user.profile.idade,
                                      user.profile.atividade, user.profile.objetivo)

        # save user
        user.save()
        return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_400_BAD_REQUEST)


# put data from bmi calculator if the user wants to save it
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def update_bmi(request):
    serializer = imcSerializer(data=request.data)
    if serializer.is_valid():
        profile = request.user.profile

        profile.peso = float(serializer.data['peso'])
        profile.altura = serializer.data['altura']
        profile.idade = serializer.data['idade']
        profile.imc = calculateBMI(profile.peso, profile.altura)
        profile.ci = calculateCI(profile.sexo, profile.peso, profile.altura, profile.altura, profile.atividade,
                                 profile.objetivo)

        profile.save()
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


# put data from ci calculator if the user wants to save it
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def update_ci(request):
    serializer = ciSerializer(data=request.data)
    if serializer.is_valid():
        profile = request.user.profile

        profile.peso = float(serializer.data['peso'])
        profile.altura = serializer.data['altura']
        profile.idade = serializer.data['idade']
        profile.atividade = serializer.data['atividade']
        profile.imc = calculateBMI(profile.peso, profile.altura)
        profile.ci = calculateCI(profile.sexo, profile.peso, profile.altura, profile.altura, profile.atividade,
                                 profile.objetivo)

        profile.save()
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


# get calories, carbon-hydrates, protein and fat of a given day
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def daily_statistics(request):
    user = request.user

    # date must be like 01-01-2000
    try:
        data = request.GET['date'].split("-")
        data = date(int(data[0]), int(data[1]), int(data[2]))
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # various intakes
    ci = user.profile.ci
    hi = 0.125 * ci
    pi = 0.075 * ci
    gi = 0.022 * ci

    # various counters
    cc = 0.0
    hc = 0.0
    pc = 0.0
    gc = 0.0

    meals = []
    if Refeicao.objects.filter(nome='breakfast', data=data, utilizador=user):
        meals.append(Refeicao.objects.get(nome='breakfast', data=data, utilizador=user))

    if Refeicao.objects.filter(nome='lunch', data=data, utilizador=user):
        meals.append(Refeicao.objects.get(nome='lunch', data=data, utilizador=user))

    if Refeicao.objects.filter(nome='snack', data=data, utilizador=user):
        meals.append(Refeicao.objects.get(nome='snack', data=data, utilizador=user))

    if Refeicao.objects.filter(nome='dinner', data=data, utilizador=user):
        meals.append(Refeicao.objects.get(nome='dinner', data=data, utilizador=user))

    for meal in meals:
        compostas = Composta.objects.filter(refeicao=meal)
        for composta in compostas:
            cc += composta.alimento.calorias * composta.quantidade / 100
            hc += float(composta.alimento.macro_nutrientes.hidratos_carbono) * composta.quantidade / 100
            pc += float(composta.alimento.macro_nutrientes.proteina) * composta.quantidade / 100
            gc += float(composta.alimento.macro_nutrientes.gordura) * composta.quantidade / 100

    return Response({'cc': round(cc, 1), 'ci': round(ci, 1), 'hc': round(hc, 1), 'hi': round(hi, 1), 'pc': round(pc, 1),
                     'pi': round(pi, 1), 'gc': round(gc, 1), 'gi': round(gi, 1)}, status=status.HTTP_200_OK)


# get all food and quantities for a specific meal
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getMeal(request):
    user = request.user

    try:
        type = request.GET['type']
        if type == '' or type not in ['breakfast', 'lunch', 'snack', 'dinner']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = request.GET['data']
        if data == "":
            data = date.today()
        else:
            data = data.split("-")
            data = date(int(data[0]), int(data[1]), int(data[2]))
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if Refeicao.objects.filter(nome=type, data=data, utilizador=user):
        meal = Refeicao.objects.get(nome=type, data=data, utilizador=user)
    else:
        meal = Refeicao(nome=type, data=data, utilizador=user)
        meal.save()
        return Response({"meal": [], "meal_id": meal.id}, status=status.HTTP_200_OK)

    compostas = Composta.objects.filter(refeicao=meal)

    data = []
    for composta in compostas:
        food = Alimento.objects.get(id=composta.alimento_id)
        data.append({'food_id': food.id, 'composed_id': composta.id, 'name': food.nome, 'calories': food.calorias,
                     'protein': food.macro_nutrientes.proteina, 'carbohydrates': food.macro_nutrientes.hidratos_carbono,
                     'fat': food.macro_nutrientes.gordura, 'quantity': composta.quantidade})

    return Response({"meal": data, "meal_id": meal.id}, status=status.HTTP_200_OK)


# get list of food with some filters
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getFoodList(request):
    user = request.user

    filter_List = {'name': "", 'category': "", 'protein_lower': 1000, 'protein_higher': 0,
                   'hc_lower': 1000, 'hc_higher': 0, 'fat_lower': 1000, 'fat_higher': 0}

    for key in request.GET.keys():
        filter_List[key] = request.GET[key]

    alimentos = Alimento.objects.all()

    if filter_List.get('name') != "":
        alimentos = alimentos.filter(nome__icontains=filter_List.get('name'))
    if filter_List.get('category') != "":
        alimentos = alimentos.filter(categoria__nome=filter_List.get('category'))
    alimentos = alimentos.filter(macro_nutrientes__proteina__gte=filter_List.get('protein_higher')).filter(
        macro_nutrientes__proteina__lte=filter_List.get('protein_lower')).filter(
        macro_nutrientes__hidratos_carbono__gte=filter_List.get('hc_higher')).filter(
        macro_nutrientes__hidratos_carbono__lte=filter_List.get('hc_lower')).filter(
        macro_nutrientes__gordura__gte=filter_List.get('fat_higher')).filter(
        macro_nutrientes__gordura__lte=filter_List.get('fat_lower')).order_by('nome')

    if 'size' in request.GET.keys():
        size = request.GET.get('size')
    else:
        size = 5

    if 'page' in request.GET.keys():
        page = request.GET.get('page')
    else:
        page = 1

    paginator = Paginator(alimentos, size)
    try:
        alimentos = paginator.page(page)
    except PageNotAnInteger:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = []
    for food in alimentos:
        data.append({'nome': food.nome, 'calorias': food.calorias, 'proteina': food.macro_nutrientes.proteina,
                     'hidratos_carbono': food.macro_nutrientes.hidratos_carbono,
                     'gordura': food.macro_nutrientes.gordura,
                     'id_alimento': food.id})
    return Response({'pages': paginator.num_pages, 'food': data}, status=status.HTTP_200_OK)


# post a food to a specific meal
@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def insertComposta(request):
    composta = ComposedSerializer(data=request.data)
    if composta.is_valid():
        composta.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


# put a quantity for a specific food and meal
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def updateComposta(request):
    try:
        composta = Composta.objects.get(id=request.data['id'])
    except Composta.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ComposedSerializer(composta, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


# delete a food from a meal
@permission_classes((IsAuthenticated,))
@api_view(['DELETE'])
def deleteComposta(request, id):
    try:
        composta = Composta.objects.get(id=id)
    except Composta.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    composta.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# get food details by id
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getFood(request):
    try:
        food = Alimento.objects.get(id=request.GET['id'])
    except Alimento.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {'nome': food.nome, 'calorias': food.calorias, 'categoria': food.categoria.nome,
            'hidratos_carbono': food.macro_nutrientes.hidratos_carbono,
            'proteina': food.macro_nutrientes.proteina, 'gordura': food.macro_nutrientes.gordura}

    return Response(data, status=status.HTTP_200_OK)


# get user first name, last name, username and email
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getUser(request):
    user = request.user
    data = {'firstName': user.first_name, 'lastName': user.last_name,
            'username': user.username, 'email': user.email, 'id': user.id, 'gender': user.profile.sexo}
    return Response(data, status=status.HTTP_200_OK)


# put to update the previous fields
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def setUser(request):
    user = request.user

    sexo = request.data['gender']
    del request.data['gender']

    serializer = UserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        user.profile.sexo = sexo
        user.profile.ci = calculateCI(sexo, user.profile.peso, user.profile.altura, user.profile.idade,
                                      user.profile.atividade, user.profile.objetivo)

        user.profile.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# put to update password
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def setPassword(request):
    user = request.user
    try:
        oldpassword = request.data['old_pwd']
        newpassword = request.data['new_pwd']
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if user.check_password(oldpassword):
        user.set_password(newpassword)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


# get objective, weight, height, age, bmi, caloric intake of a user
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getProfile(request):
    profile = request.user.profile

    data = {'id': profile.id, 'objetivo': profile.objetivo, 'peso': profile.peso, 'altura': profile.altura,
            'idade': profile.idade, 'imc': profile.imc, 'ci': profile.ci, 'atividade': profile.atividade,
            'sexo': profile.sexo}
    return Response(data, status=status.HTTP_200_OK)


# put to update the previous fields
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def updateProfile(request):
    profile = request.user.profile

    serializer = ProfileSerializer(profile, data=request.data)

    if serializer.is_valid():
        serializer.save()

        profile.imc = calculateBMI(profile.peso, profile.altura)
        profile.ci = calculateCI(profile.sexo, profile.peso, profile.altura, profile.idade,
                                 profile.atividade, profile.objetivo)

        profile.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# post a new food
@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def addFood(request):
    if not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = foodWithMacroSerializer(data=request.data)

    if serializer.is_valid():
        try:
            category = Categoria.objects.get(nome=serializer.data['categoria'])
        except Categoria.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        macros = Macronutrientes.objects.create(hidratos_carbono=serializer.data['hidratos_carbono'],
                                                gordura=serializer.data['gordura'],
                                                proteina=serializer.data['proteina'])
        macros.save()
        food = Alimento.objects.create(nome=serializer.data['nome'], calorias=serializer.data['calorias'],
                                       categoria=category, macro_nutrientes=macros)
        food.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# put to update food attributes
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def updateFood(request):
    if not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        food = Alimento.objects.get(id=request.data['id'])
    except Alimento.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = foodWithMacroSerializer(data=request.data)

    if serializer.is_valid():
        try:
            category = Categoria.objects.get(nome=serializer.data['categoria'])
        except Categoria.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        food.macro_nutrientes.hidratos_carbono = serializer.data['hidratos_carbono']
        food.macro_nutrientes.gordura = serializer.data['gordura']
        food.macro_nutrientes.proteina = serializer.data['proteina']
        food.macro_nutrientes.save()
        food.nome = serializer.data['nome']
        food.calorias = serializer.data['calorias']
        food.categoria = category
        food.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# delete a food
@permission_classes((IsAuthenticated,))
@api_view(['DELETE'])
def deleteFood(request, id):
    if not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        food = Alimento.objects.get(id=id)
    except Alimento.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    food.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# get user list, allow filter by name
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getUsers(request):
    if not request.user.is_superuser:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if 'name' in request.GET.keys():
        users = User.objects.filter(username__icontains=request.GET['name'])
    else:
        users = User.objects.all()

    if 'staff' in request.GET.keys():
        if request.GET['staff'] == 'True':
            users = users.filter(is_staff=True)
        else:
            users = users.filter(is_staff=False)

    if 'superUser' in request.GET.keys():
        if request.GET['superUser'] == 'True':
            users = users.filter(is_superuser=True)
        else:
            users = users.filter(is_superuser=False)

    if 'size' in request.GET.keys():
        size = request.GET.get('size')
    else:
        size = 5

    if 'page' in request.GET.keys():
        page = request.GET.get('page')
    else:
        page = 1

    paginator = Paginator(users, size)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = []
    for user in users:
        data.append({'id': user.id, 'name': user.username, 'staff': user.is_staff, 'superuser': user.is_superuser})

    return Response({'users': data, 'pages': paginator.num_pages}, status=status.HTTP_200_OK)


# put user new status
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def updateUserUp(request):
    if not request.user.is_superuser:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.data['id']:
        id = request.data['id']
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if user.is_staff:
        user.is_superuser = True
    else:
        user.is_staff = True
    user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


# put user new status
@permission_classes((IsAuthenticated,))
@api_view(['PUT'])
def updateUserDown(request):
    if not request.user.is_superuser:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.data['id']:
        id = request.data['id']
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if user.is_superuser:
        user.is_superuser = False
    else:
        user.is_staff = False
    user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getCategories(request):
    categories = Categoria.objects.all()

    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def postCategory(request):
    if not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = CategorySerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes((IsAuthenticated,))
@api_view(['DELETE'])
def deleteCategory(request, id):
    if not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        c = Categoria.objects.get(id=id)
    except Categoria.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    c.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def getPermissions(request):
    user = request.user

    return Response(data={'food': user.is_staff, 'user': user.is_superuser})
