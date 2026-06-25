#Criado por Ísis Barbiere e Projeto PhysCore

import math
import numpy as np
from dataclasses import dataclass
from typing import List
import json
from datetime import datetime
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image

@dataclass
class Corpo:
    nome: str
    massa: float
    cor: tuple
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float


class SimuladorGravitacional:

    # Ajuste conforme a escala da sua simulação (default: 1 metro).
    SOFTENING = 1.0  # metros

    def __init__(self):
        self.G = 6.67430e-11  # Constante gravitacional (m³/kg/s²)
        self.corpos: List[Corpo] = []
        self.historico = []

    def adicionar_corpo(self, corpo: Corpo):
        self.corpos.append(corpo)

    def calcular_forca_entre_corpos(self, corpo1: Corpo, corpo2: Corpo):
        """Calcula a força gravitacional entre dois corpos com softening."""
        dx = corpo2.x - corpo1.x
        dy = corpo2.y - corpo1.y
        dz = corpo2.z - corpo1.z

        # [CORREÇÃO 3] Usa softening para evitar singularidade quando distância → 0
        distancia_sq = dx**2 + dy**2 + dz**2 + self.SOFTENING**2
        distancia = math.sqrt(distancia_sq)

        forca_magnitude = (self.G * corpo1.massa * corpo2.massa) / distancia_sq

        fx = forca_magnitude * (dx / distancia)
        fy = forca_magnitude * (dy / distancia)
        fz = forca_magnitude * (dz / distancia)

        return fx, fy, fz

    def calcular_aceleracao(self, corpo: Corpo, forcas: List[tuple]):
        """Calcula a aceleração resultante em um corpo."""
        fx_total = sum(f[0] for f in forcas)
        fy_total = sum(f[1] for f in forcas)
        fz_total = sum(f[2] for f in forcas)

        ax = fx_total / corpo.massa
        ay = fy_total / corpo.massa
        az = fz_total / corpo.massa

        return ax, ay, az

    def executar_simulacao(self, tempo_total: float, instante: float):
        """Executa a simulação completa usando integrador Euler-Cromer."""
        tempo_atual = 0.0
        num_instantes = int(tempo_total / instante)

        print(f"Iniciando simulação: {num_instantes} instantes a calcular...")

        for passo in range(num_instantes + 1):
            # Salvar estado atual
            estado_atual = {
                'tempo': tempo_atual,
                'corpos': []
            }

            for corpo in self.corpos:
                estado_atual['corpos'].append({
                    'nome': corpo.nome,
                    'x': corpo.x,
                    'y': corpo.y,
                    'z': corpo.z,
                    'vx': corpo.vx,
                    'vy': corpo.vy,
                    'vz': corpo.vz
                })

            self.historico.append(estado_atual)

            if passo == num_instantes:
                break

            # Calcular forças entre todos os pares de corpos
            forcas_por_corpo = [[] for _ in self.corpos]

            for i, corpo1 in enumerate(self.corpos):
                for j, corpo2 in enumerate(self.corpos):
                    if i != j:
                        fx, fy, fz = self.calcular_forca_entre_corpos(corpo1, corpo2)
                        forcas_por_corpo[i].append((fx, fy, fz))

        
            # velocidade atualizada primeiro, depois posição usa a velocidade nova.
            # Isso conserva energia melhor que o Euler simples em órbitas.
            for i, corpo in enumerate(self.corpos):
                ax, ay, az = self.calcular_aceleracao(corpo, forcas_por_corpo[i])

                # 1) Atualizar velocidades
                corpo.vx += ax * instante
                corpo.vy += ay * instante
                corpo.vz += az * instante

                # 2) Atualizar posições com a velocidade NOVA (Euler-Cromer)
                corpo.x += corpo.vx * instante
                corpo.y += corpo.vy * instante
                corpo.z += corpo.vz * instante

            tempo_atual += instante

            # Progresso a cada 1%
            if num_instantes > 100 and passo % (num_instantes // 100) == 0 and passo > 0:
                progresso = (passo / num_instantes) * 100
                print(f"Progresso dos cálculos: {progresso:.1f}%")

        print("Simulação concluída!")

    def exportar_dados(self, nome_arquivo: str):
        """Exporta os dados da simulação para um arquivo txt."""
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(f"# Simulação Gravitacional - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            arquivo.write(f"# Número de corpos: {len(self.corpos)}\n")
            arquivo.write(f"# Número de instantes: {len(self.historico)}\n\n")

            arquivo.write("# Informações dos Corpos:\n")
            for corpo in self.corpos:
                arquivo.write(f"# {corpo.nome}: massa={corpo.massa:.2e} kg, cor={corpo.cor}\n")
            arquivo.write("\n")

            arquivo.write("Tempo(s) | ")
            for corpo in self.corpos:
                arquivo.write(
                    f"{corpo.nome}_X(m) {corpo.nome}_Y(m) {corpo.nome}_Z(m) "
                    f"{corpo.nome}_VX(m/s) {corpo.nome}_VY(m/s) {corpo.nome}_VZ(m/s) | "
                )
            arquivo.write("\n")

            for estado in self.historico:
                arquivo.write(f"{estado['tempo']:.6f} | ")
                for corpo_estado in estado['corpos']:
                    arquivo.write(
                        f"{corpo_estado['x']:.6e} {corpo_estado['y']:.6e} {corpo_estado['z']:.6e} "
                        f"{corpo_estado['vx']:.6e} {corpo_estado['vy']:.6e} {corpo_estado['vz']:.6e} | "
                    )
                arquivo.write("\n")

        print(f"Dados exportados para {nome_arquivo}")

    def gerar_visualizacao_3d(self, nome_pasta: str, amostragem: int = 1):
        """Gera gráficos 3D para cada instante e cria um GIF animado."""

        if not os.path.exists(nome_pasta):
            os.makedirs(nome_pasta)

        print(f"Gerando visualizações 3D na pasta '{nome_pasta}'...")

        # Encontrar limites dos eixos para escala consistente
        todos_x, todos_y, todos_z = [], [], []
        for estado in self.historico:
            for corpo in estado['corpos']:
                todos_x.append(corpo['x'])
                todos_y.append(corpo['y'])
                todos_z.append(corpo['z'])

        max_range = max(
            max(todos_x) - min(todos_x),
            max(todos_y) - min(todos_y),
            max(todos_z) - min(todos_z)
        ) * 0.6

        centro_x = (max(todos_x) + min(todos_x)) / 2
        centro_y = (max(todos_y) + min(todos_y)) / 2
        centro_z = (max(todos_z) + min(todos_z)) / 2

     
        # eliminando o desalinhamento entre j e o filtro por nome.
        indice_por_nome = {corpo.nome: idx for idx, corpo in enumerate(self.corpos)}

        massa_minima = min(c.massa for c in self.corpos)

        imagens = []
        total_instantes = len(self.historico)

        for i, estado in enumerate(self.historico):
            if i % amostragem != 0 and i != total_instantes - 1:
                continue

            fig = plt.figure(figsize=(12, 9))
            ax = fig.add_subplot(111, projection='3d')

            for corpo_info in estado['corpos']:
                corpo_original = next(c for c in self.corpos if c.nome == corpo_info['nome'])

                cor_normalizada = (
                    corpo_original.cor[0] / 255,
                    corpo_original.cor[1] / 255,
                    corpo_original.cor[2] / 255
                )

                tamanho = 50 + 100 * math.log10(corpo_original.massa / massa_minima + 1)

                ax.scatter(
                    corpo_info['x'], corpo_info['y'], corpo_info['z'],
                    c=[cor_normalizada], s=tamanho,
                    label=corpo_info['nome'], marker='o', alpha=0.8
                )

                # [CORREÇÃO 1] Busca a trajetória usando o índice fixo do corpo,
                # sem risco de desalinhamento entre j e a condição if.
                idx_corpo = indice_por_nome[corpo_info['nome']]

                x_traj = [e['corpos'][idx_corpo]['x'] for e in self.historico[:i + 1]]
                y_traj = [e['corpos'][idx_corpo]['y'] for e in self.historico[:i + 1]]
                z_traj = [e['corpos'][idx_corpo]['z'] for e in self.historico[:i + 1]]

                ax.plot(x_traj, y_traj, z_traj, color=cor_normalizada, alpha=0.3, linewidth=1)

            ax.set_xlim([centro_x - max_range, centro_x + max_range])
            ax.set_ylim([centro_y - max_range, centro_y + max_range])
            ax.set_zlim([centro_z - max_range, centro_z + max_range])

            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')
            ax.set_title(f'Simulação Gravitacional\nTempo: {estado["tempo"]:.2f} segundos')
            ax.legend(loc='upper left', bbox_to_anchor=(0, 1))
            ax.grid(True, alpha=0.3)

            nome_imagem = f"{nome_pasta}/frame_{i:06d}.png"
            plt.savefig(nome_imagem, dpi=100, bbox_inches='tight')
            imagens.append(nome_imagem)
            plt.close()

            if i % max(1, total_instantes // 10) == 0:
                progresso = (i / total_instantes) * 100
                print(f"Progresso das visualizações: {progresso:.1f}%")

        print("Criando GIF animado...")
        frames = [Image.open(img) for img in imagens]

        gif_path = f"{nome_pasta}/animacao_gravitacional.gif"
        frames[0].save(
            gif_path, format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=100,
            loop=0
        )

        print(f"GIF animado salvo como: {gif_path}")
        print(f"Total de frames gerados: {len(imagens)}")

        return gif_path


def main():
    simulador = SimuladorGravitacional()

    print("=== Simulador Gravitacional de N-Corpos ===\n")

    while True:
        try:
            num_corpos = int(input("Quantidade de corpos na simulação: "))
            if num_corpos > 0:
                break
            print("Digite um número maior que 0.")
        except ValueError:
            print("Digite um número válido.")

    for i in range(num_corpos):
        print(f"\n--- Corpo {i+1} ---")
        nome = input("Nome do corpo: ")

        while True:
            try:
                massa = float(input("Massa (kg): "))
                if massa > 0:
                    break
                print("A massa deve ser maior que 0.")
            except ValueError:
                print("Digite um número válido.")

        print("Posição inicial:")
        x = float(input("  X (m): "))
        y = float(input("  Y (m): "))
        z = float(input("  Z (m): "))

        print("Velocidade inicial:")
        vx = float(input("  VX (m/s): "))
        vy = float(input("  VY (m/s): "))
        vz = float(input("  VZ (m/s): "))

        print("Cor (valores RGB de 0 a 255):")
        r = int(input("  R: "))
        g = int(input("  G: "))
        b = int(input("  B: "))

        corpo = Corpo(nome, massa, (r, g, b), x, y, z, vx, vy, vz)
        simulador.adicionar_corpo(corpo)

    while True:
        try:
            tempo_total = float(input("\nTempo total da simulação (segundos): "))
            if tempo_total > 0:
                break
            print("O tempo deve ser maior que 0.")
        except ValueError:
            print("Digite um número válido.")

    while True:
        try:
            instante = float(input("Intervalo de tempo para cálculos (instante em segundos): "))
            if 0 < instante <= tempo_total:
                break
            print(f"O instante deve ser maior que 0 e menor ou igual ao tempo total ({tempo_total}s).")
        except ValueError:
            print("Digite um número válido.")

    print("\nIniciando cálculos...")
    simulador.executar_simulacao(tempo_total, instante)

    nome_arquivo = input("\nNome do arquivo para exportação (sem extensão): ") + ".txt"
    simulador.exportar_dados(nome_arquivo)

    print("\nDeseja gerar visualização 3D animada?")
    print("Isso pode demorar para simulações longas.")
    gerar_visualizacao = input("Gerar animação? (s/n): ").lower().strip()

    if gerar_visualizacao == 's':
        nome_pasta = "simulacao_3d"
        total_instantes = len(simulador.historico)

        if total_instantes > 1000:
            amostragem = max(1, total_instantes // 500)
            print(f"Muitos instantes ({total_instantes}). Usando amostragem de 1 em {amostragem}.")
        else:
            amostragem = 1

        gif_path = simulador.gerar_visualizacao_3d(nome_pasta, amostragem)
        print(f"\n✨ Animação concluída! Verifique o arquivo: {gif_path}")

    print(f"\nSimulação finalizada!")


if __name__ == "__main__":
    main()