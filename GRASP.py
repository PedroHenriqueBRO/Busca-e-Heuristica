import random
import math

import time

# Parâmetros do problema
num_tuplas = 180
num_classes = 6
num_professores = 6
num_salas = 6
num_periodos = 30 # Exemplo de período representando todos os dias de uma semana

start_time=time.time()
def Calcular_Custo(solucao):
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
            if abs(dia - media_aulas) > 1:  # penalizar se a distribuição for desigual além de 1 aula
                saving += 1
                conflitos.add((classe, dias.index(dia)))  # adiciona o conflito para o dia específico

    return saving, conflitos

def AlterarPeriodo_PrimeiraMelhora(solucao, saving):
    melhor_solucao = solucao.copy() # copiar a solução atual
    melhor_custo = saving # custo da solução atual

    for idx, (classe, professor, sala, periodo) in enumerate(solucao): # para cada tupla na solução atual
        for novo_periodo in range(num_periodos): # para cada período
            if novo_periodo != periodo:  # evitar ser igual
                nova_solucao = solucao.copy() # copiar a solução atual
                nova_solucao[idx] = (classe, professor, sala, novo_periodo) # alterar o período da tupla atual
                saving_novo, _ = Calcular_Custo(nova_solucao) # calcular o custo da nova solução

                if saving_novo < melhor_custo:  # se a nova solução for melhor que a solução atual, atualizamos a solução e o custo
                    print("Primeira melhora encontrada") # imprimir mensagem de melhora
                    return nova_solucao, saving_novo
    
    return melhor_solucao, melhor_custo


def AlterarPeriodo_MelhorMelhora(solucao, saving):
    melhor_solucao = solucao.copy()
    melhor_custo = saving

    for idx, (classe, professor, sala, periodo) in enumerate(solucao):
        for novo_periodo in range(num_periodos):
            if novo_periodo != periodo:  # evitar ser igual
                nova_solucao = solucao.copy()
                nova_solucao[idx] = (classe, professor, sala, novo_periodo)
                saving_novo, _ = Calcular_Custo(nova_solucao)

                if saving_novo < melhor_custo:
                    melhor_custo = saving_novo
                    melhor_solucao = nova_solucao.copy()
    
    print("Melhor melhora encontrada")
    return melhor_solucao, melhor_custo


def AlterarSala_PrimeiraMelhora(solucao, saving):
    melhor_solucao = solucao.copy()
    melhor_custo = saving

    for idx, (classe, professor, sala, periodo) in enumerate(solucao): # para cada tupla na solução atual
        for nova_sala in range(num_salas): # para cada sala
            if nova_sala != sala:  # evitar ser igual
                nova_solucao = solucao.copy() # copiar a solução atual
                nova_solucao[idx] = (classe, professor, nova_sala, periodo) # alterar a sala da tupla atual
                saving_novo, _ = Calcular_Custo(nova_solucao) # calcular o custo da nova solução

                if saving_novo < melhor_custo: # se a nova solução for melhor que a solução atual, atualizamos a solução e o custo
                    print("Primeira melhora encontrada") # imprimir mensagem de melhora
                    return nova_solucao, saving_novo # retornar a nova solução e o custo da nova solução

    return melhor_solucao, melhor_custo

# funcão alterar sala melhor melhora
def AlterarSala_MelhorMelhora(solucao, saving):
    melhor_solucao = solucao.copy()
    melhor_custo = saving

    # aqui verificamos se a mudança de sala melhora o custo da solução, se sim, atualizamos a solução e o custo da solução
    for idx, (classe, professor, sala, periodo) in enumerate(solucao): # para cada tupla na solução atual
        for nova_sala in range(num_salas):
            if nova_sala != sala:  # Evitar manter a mesma sala
                nova_solucao = solucao.copy()
                nova_solucao[idx] = (classe, professor, nova_sala, periodo)
                saving_novo, _ = Calcular_Custo(nova_solucao)

                if saving_novo < melhor_custo: # se a nova solução for melhor que a solução atual, atualizamos a solução e o custo
                    melhor_custo = saving_novo
                    melhor_solucao = nova_solucao.copy()
    
    print("Melhor melhora encontrada")
    return melhor_solucao, melhor_custo

# Função que implementa a heurística construtiva do GRASP (original)
def Heuristica_Construtiva(alpha):
    solucao = []

    for _ in range(num_tuplas):
        opcoes = []
        for classe in range(num_classes):
            for professor in range(num_professores):
                for sala in range(num_salas):
                    for periodo in range(num_periodos):
                        tupla = (classe, professor, sala, periodo)
                        solucao_temp = solucao + [tupla]
                        saving_temp, _ = Calcular_Custo(solucao_temp)

                        # Adicionar opção de tupla com penalidades computadas
                        opcoes.append((tupla, saving_temp))

        # ordena as opções de tuplas pelo custo "saving_temp" e escolhe a melhor
        numb=random.randint(0,len(opcoes)-1)
        limite_superior=opcoes[numb][1]/alpha
        lrc=[]
        for i in opcoes:
            if(i[1]<=limite_superior):
                lrc.append(i)    
        lrc.sort(key=lambda x:x[1])
        opcao_encontrada=random.choice(lrc[:5])
        solucao.append(opcao_encontrada[0])
        customelhor=opcao_encontrada[1]
    # salva a solução em um arquivo de texto
    with open("solucao.txt", "w") as file:
        for tupla in solucao:
            file.write(f"{tupla[0] + 1} {tupla[1] + 1} {tupla[2] + 1} {tupla[3] + 1}\n")
    print(f"Custo Inicial Da Solução : {customelhor}")
    return solucao,customelhor

# fução recebe como parâmetros o número máximo de iterações, a vizinhança e a estratégia de busca. a vizinhança pode ser "periodo" ou "sala" e a estratégia pode ser "primeira" ou "melhor"
def GRASP(max_iteracoes, vizinhanca, estrategia):
    alpha = 0.9
    melhor_solucao = []
    melhor_custo = math.inf

    for i in range(max_iteracoes):
        print(f"\niteração {i + 1}")
        solucao, _ = Heuristica_Construtiva(alpha)
        saving, _ = Calcular_Custo(solucao)

        if saving == 0:  # Solução ótima encontrada
            melhor_solucao = solucao.copy()
            melhor_custo = saving
            break

        # Escolher a vizinhança e estratégia de busca
        if vizinhanca == "periodo":
            if estrategia == "primeira":
                solucao, saving = AlterarPeriodo_PrimeiraMelhora(solucao, saving)
            elif estrategia == "melhor":
                solucao, saving = AlterarPeriodo_MelhorMelhora(solucao, saving)
        elif vizinhanca == "sala":
            if estrategia == "primeira":
                solucao, saving = AlterarSala_PrimeiraMelhora(solucao, saving)
            elif estrategia == "melhor":
                solucao, saving = AlterarSala_MelhorMelhora(solucao, saving)

        print(f"Custo da solução após busca local ({estrategia} melhora): {saving}")

        if saving < melhor_custo:
            melhor_custo = saving
            melhor_solucao = solucao.copy()

    return melhor_solucao, melhor_custo



print("\nPARAMETRO PERIODO - PRIMEIRA MELHORA")
solucao_periodo_primeira, custo_periodo_primeira = GRASP(10, "periodo", "primeira")
print(f"Melhor custo: {custo_periodo_primeira}")

print("\nPARAMETRO PERIODO - MELHOR MELHORA")
solucao_periodo_melhor, custo_periodo_melhor = GRASP(10, "periodo", "melhor")
print(f"Melhor custo: {custo_periodo_melhor}")

print("\nPARAMETRO SALA - PRIMEIRA MELHORA")
solucao_sala_primeira, custo_sala_primeira = GRASP(10, "sala", "primeira")
print(f"Melhor custo: {custo_sala_primeira}")

print("\nPARAMETRO SALA - MELHOR MELHORA")
solucao_sala_melhor, custo_sala_melhor = GRASP(10, "sala", "melhor")
print(f"Melhor custo: {custo_sala_melhor}")

