import random
import time


num_tuplas = 180
num_classes = 6
num_professores = 6
num_salas = 6
num_periodos = 30


def calcular_custo(solucao):
    saving = 0
    conflitos = set()
    count_class_period = {}
    count_teacher_period = {}
    count_room_period = {}
    aulas_por_classe = {classe: [0] * 5 for classe in range(num_classes)}
    count_room_adjacent = {sala: [] for sala in range(num_salas)}

    for (classe, professor, sala, periodo) in solucao:
        count_class_period[(classe, periodo)] = count_class_period.get((classe, periodo), 0) + 1
        count_teacher_period[(professor, periodo)] = count_teacher_period.get((professor, periodo), 0) + 1
        count_room_period[(sala, periodo)] = count_room_period.get((sala, periodo), 0) + 1
        dia_semana = periodo // (num_periodos // 5)
        aulas_por_classe[classe][dia_semana] += 1
        count_room_adjacent[sala].append(periodo)
    
    for (classe, periodo), count in count_class_period.items():
        if count > 1:
            saving += (count - 1)
            conflitos.add((classe, periodo))

    for (professor, periodo), count in count_teacher_period.items():
        if count > 1:
            saving += (count - 1)
            conflitos.add((professor, periodo))

    for (sala, periodo), count in count_room_period.items():
        if count > 1:
            saving += (count - 1)
            conflitos.add((sala, periodo))

    for classe, dias in aulas_por_classe.items():
        media_aulas = sum(dias) / 5
        for dia in dias:
            if abs(dia - media_aulas) > 1:
                saving += 1
                conflitos.add((classe, dias.index(dia)))

    return saving, conflitos


def fitness(solucao):
    saving, _ = calcular_custo(solucao)
    return 1 / (1 + saving)

def gerar_solucao_inicial():
    solucao = []
    for _ in range(num_tuplas):
        opcoes = []
        for classe in range(num_classes):
            for professor in range(num_professores):
                for sala in range(num_salas):
                    for periodo in range(num_periodos):
                        tupla = (classe, professor, sala, periodo)
                        solucao_temp = solucao + [tupla]
                        saving_temp, _ = calcular_custo(solucao_temp)

                        opcoes.append((tupla, saving_temp))

        opcoes.sort(key=lambda x: x[1])
        melhor_opcao = random.choice(opcoes[:5])

        solucao.append(melhor_opcao[0])

    return solucao


def selecionar_pais(populacao):
    melhores = sorted(populacao, key=lambda x: fitness(x), reverse=True)[:2]
    return random.choice(melhores), random.choice(melhores)


def cruzamento(pai1, pai2):
    ponto = random.randint(1, len(pai1) - 2)
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2


def mutacao(solucao):
    if random.random() < 0.2:
        idx = random.randint(0, len(solucao) - 1)
        melhor_solucao = solucao[:]
        melhor_fitness = fitness(solucao)
        
        for _ in range(400):
            nova_solucao = solucao[:]
            nova_solucao[idx] = (
                random.randint(0, num_classes - 1),
                random.randint(0, num_professores - 1),
                random.randint(0, num_salas - 1),
                random.randint(0, num_periodos - 1),
            )
            if fitness(nova_solucao) > melhor_fitness:
                melhor_solucao = nova_solucao
                melhor_fitness = fitness(nova_solucao)
        
        return melhor_solucao
    return solucao


def algoritmo_genetico(geracoes=1200, tamanho_pop=1):
    populacao = [gerar_solucao_inicial() for _ in range(tamanho_pop)]
    for _ in range(geracoes):
        nova_populacao = []
        while len(nova_populacao) < tamanho_pop:
            pai1, pai2 = selecionar_pais(populacao)
            filho1, filho2 = cruzamento(pai1, pai2)
            filho1, filho2 = mutacao(filho1), mutacao(filho2)
            nova_populacao.extend([filho1,filho2])
        populacao = sorted(nova_populacao + populacao, key=lambda x: fitness(x), reverse=True)[:tamanho_pop]
    return populacao[0]


solucao_otima = algoritmo_genetico()

custo,_=calcular_custo(solucao_otima)
print("Fitness da melhor solução:", custo)
