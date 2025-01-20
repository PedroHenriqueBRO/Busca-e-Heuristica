import random
import math

import time

# Parâmetros do problema
num_tuplas = 210
num_classes = 7
num_professores = 7
num_salas = 7
num_periodos = 30 # Exemplo de período representando todos os dias de uma semana

start_time=time.time()
def calcular_custo(solucao):
    saving = 0
    conflitos = set()
    count_class_period = {}
    count_teacher_period = {}
    count_room_period = {}
    
    # essas variáveis são usadas para verificar se a distribuição de aulas é equitativa ao longo da semana para cada classe
    aulas_por_classe = {classe: [0] * 5 for classe in range(num_classes)}  # distribuição semanal de aulas para cada classe
    count_room_adjacent = {sala: [] for sala in range(num_salas)}  # aqui armazenamos os períodos consecutivos de cada sala para verificar conflitos consecutivos

    for (classe, professor, sala, periodo) in solucao:
        # contagem de aulas por classe, professor e sala
        count_class_period[(classe, periodo)] = count_class_period.get((classe, periodo), 0) + 1
        count_teacher_period[(professor, periodo)] = count_teacher_period.get((professor, periodo), 0) + 1
        count_room_period[(sala, periodo)] = count_room_period.get((sala, periodo), 0) + 1

        # verificar se há conflitos consecutivos na sala
        dia_semana = periodo // (num_periodos // 5)  # assumindo 5 dias de semana
        aulas_por_classe[classe][dia_semana] += 1

        # verificar se há aulas consecutivas na mesma sala, a adjacência é baseada no período de aulas consecutivas na mesma sala
        count_room_adjacent[sala].append(periodo)

    # penalizar aulas consecutivas na mesma sala (adjacência)
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

    # essa função penaliza a distribuição desigual de aulas ao longo da semana para cada classe (média de aulas por dia)
    for classe, dias in aulas_por_classe.items():
        media_aulas = sum(dias) / 5
        for dia in dias:
            if abs(dia - media_aulas) > 1:  # Penalizar se a distribuição for desigual além de 1 aula
                saving += 1
                conflitos.add((classe, dias.index(dia)))  # Adiciona o conflito para o dia específico

    return saving, conflitos

# Heurística Construtiva Gulosa para a solução inicial
def heuristica_construtiva():
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

                        # Adicionar opção de tupla com penalidades computadas
                        opcoes.append((tupla, saving_temp))

         # Ordena as opções de tuplas pelo custo "saving_temp" e escolhe a melhor
        opcoes.sort(key=lambda x: x[1])
        melhor_opcao = random.choice(opcoes[:5])  # Escolhe entre as 5 melhores opções

        solucao.append(melhor_opcao[0])

    # Salva a solução em um arquivo de texto
    with open("solucao.txt", "w") as file:
        for tupla in solucao:
            file.write(f"{tupla[0] + 1} {tupla[1] + 1} {tupla[2] + 1} {tupla[3] + 1}\n")
    
    return solucao

# Função para perturbar a solução atual e resolver conflitos, perturbar significa alterar aleatoriamente um período, sala ou professor
def perturbar_solucao(solucao, conflitos):
    nova_solucao = solucao.copy()
    
    conflito = random.choice(list(conflitos)) # escolhe um conflito aleatório, porque a heurística é gulosa e pode não resolver todos os conflitos de uma vez 
    elemento, periodo = conflito
    
    # encontra o índice da tupla que contém o elemento em conflito, para poder alterar aleatoriamente o período, sala ou professor
    indices = [i for i, (classe, professor, sala, p) in enumerate(solucao) if (classe == elemento or professor == elemento or sala == elemento) and p == periodo]
    if indices:
        idx = random.choice(indices)
        classe, professor, sala, periodo = nova_solucao[idx]

        # escolhe aleatoriamente um novo período, sala ou professor que não seja o atual para resolver o conflito 
        novo_periodo = random.choice([p for p in range(num_periodos) if p != periodo])
        nova_sala = random.choice([s for s in range(num_salas) if s != sala])
        novo_professor = random.choice([t for t in range(num_professores) if t != professor])

        # escolhe aleatoriamente o que alterar para resolver o conflito
        alteracao = random.choice(["periodo", "sala", "professor"])
        if alteracao == "periodo":
            nova_solucao[idx] = (classe, professor, sala, novo_periodo)
        elif alteracao == "sala":
            nova_solucao[idx] = (classe, professor, nova_sala, periodo)
        else:
            nova_solucao[idx] = (classe, novo_professor, sala, periodo)
    
    return nova_solucao

#função de recozimento simulado para otimização 
def simulated_annealing(temperatura_inicial, taxa_resfriamento, iteracoes_constantes):
    solucao_atual = heuristica_construtiva()
    custo_atual, conflitos = calcular_custo(solucao_atual)
    temperatura = temperatura_inicial

    while custo_atual != 0 and temperatura > 0.001: # condição de parada, devido a complexidade do problema e a heurística gulosa que pode não resolver todos os conflitos
        for _ in range(iteracoes_constantes):
            nova_solucao = perturbar_solucao(solucao_atual, conflitos) # perturba a solução atual para resolver conflitos
            custo_remocao, _ = calcular_custo(solucao_atual) # custo da solução atual
            custo_insercao, novos_conflitos = calcular_custo(nova_solucao) # custo da nova solução
            delta_custo = custo_insercao - custo_remocao # diferença de custo entre a solução atual e a nova solução

            if delta_custo <= 0 or math.exp(-delta_custo / temperatura) > random.random(): # aceita a nova solução se o custo for menor ou com probabilidade baseada na temperatura
                solucao_atual = nova_solucao
                custo_atual = custo_insercao
                conflitos = novos_conflitos

        temperatura *= taxa_resfriamento

    custo_final, conflitos = calcular_custo(solucao_atual)
    return solucao_atual, custo_final, conflitos


temperatura_inicial = 1000
taxa_resfriamento = 0.99
iteracoes_constantes = 100

# Executar o algoritmo de recozimento simulado
melhor_solucao, melhor_custo, conflitos = simulated_annealing(temperatura_inicial, taxa_resfriamento, iteracoes_constantes)

# Imprimir a melhor solução encontrada
print("Melhor solução (Classe, Professor, Sala, Período):")
for i, (classe, professor, sala, periodo) in enumerate(melhor_solucao):
    print(f"Tupla {i+1}: Classe {classe + 1}, Professor {professor + 1}, Sala {sala + 1}, Período {periodo + 1}")

print("\nCusto da melhor solução:", melhor_custo)

if conflitos:
    print("\nConflitos restantes (Elemento, Período):")
    for conflito in conflitos:
        elemento, periodo = conflito
        print(f"Elemento {elemento} em Período {periodo + 1} tem conflito!")
else:
    print("\nNenhum conflito encontrado!")
end_time=time.time()-start_time
print(end_time)
