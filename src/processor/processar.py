import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import permutations
import time
import os

# Constantes conforme enunciado
PLACA_LARGURA = 300
PLACA_ALTURA = 300
MARGEM = 10  # cm - margem mínima obrigatória
LASER_CUSTO_POR_CM = 0.01  # R$ por cm de corte
PLACA_CUSTO = 1000.0  # R$ por placa

class Peca:
    def __init__(self, largura, altura, id):
        self.largura = largura
        self.altura = altura
        self.id = id
        self.x = 0
        self.y = 0
    
    def __repr__(self):
        return f"Peça {self.id}: {self.largura}x{self.altura}"

class Placa:
    def __init__(self):
        self.largura = PLACA_LARGURA
        self.altura = PLACA_ALTURA
        self.ocupacao = [[False for _ in range(self.largura)] for _ in range(self.altura)]
        self.pecas = []
    
    def limpar(self):
        self.ocupacao = [[False for _ in range(self.largura)] for _ in range(self.altura)]
        self.pecas = []
    
    def area_livre(self):
        return sum(row.count(False) for row in self.ocupacao)
    
    def verificar_espaco(self, x, y, largura, altura):
        """
        Verifica se há espaço disponível respeitando a margem de 10cm.
        """
        # Limites da área útil (descontando margem de 10cm em cada borda)
        x_min = MARGEM
        y_min = MARGEM
        x_max = self.largura - MARGEM
        y_max = self.altura - MARGEM
        
        # A peça deve estar completamente dentro da área útil
        if x < x_min or y < y_min:
            return False
        if x + largura > x_max or y + altura > y_max:
            return False
        
        # Verificar colisão com peças já colocadas
        for i in range(y, y + altura):
            for j in range(x, x + largura):
                if self.ocupacao[i][j]:
                    return False
        return True
    
    def ocupar_espaco(self, x, y, largura, altura):
        """Marca o espaço como ocupado."""
        for i in range(y, y + altura):
            for j in range(x, x + largura):
                self.ocupacao[i][j] = True
    
    def calcular_custo_posicao(self, x, y, largura, altura):
        """
        Calcula o CUSTO REAL de corte a laser para colocar a peça nesta posição.
        
        Custo = (perímetro da peça - bordas compartilhadas) × R$0,01/cm
        
        Bordas compartilhadas: quando a peça encosta em outra peça já colocada,
        não precisamos cortar aquele trecho novamente.
        """
        # Perímetro total da peça (em cm)
        perimetro = 2 * (largura + altura)
        
        # Calcular bordas compartilhadas com peças adjacentes
        compartilhado = 0
        
        # Borda superior (y-1)
        if y > 0:
            for j in range(x, x + largura):
                if self.ocupacao[y - 1][j]:
                    compartilhado += 1
        
        # Borda inferior (y + altura)
        if y + altura < self.altura:
            for j in range(x, x + largura):
                if self.ocupacao[y + altura][j]:
                    compartilhado += 1
        
        # Borda esquerda (x-1)
        if x > 0:
            for i in range(y, y + altura):
                if self.ocupacao[i][x - 1]:
                    compartilhado += 1
        
        # Borda direita (x + largura)
        if x + largura < self.largura:
            for i in range(y, y + altura):
                if self.ocupacao[i][x + largura]:
                    compartilhado += 1
        
        # Comprimento real de corte = perímetro - bordas compartilhadas
        comprimento_corte = perimetro - compartilhado
        
        # Custo em R$
        return comprimento_corte * LASER_CUSTO_POR_CM
    
    def encontrar_melhor_posicao(self, peca):
        """
        Encontra a melhor posição (x, y) para uma peça nesta placa.
        Retorna (custo_em_reais, x, y)
        """
        melhor_custo = float('inf')
        melhor_x, melhor_y = -1, -1
        
        # Iterar dentro da área útil (respeitando margem)
        for y in range(MARGEM, self.altura - MARGEM - peca.altura + 1):
            for x in range(MARGEM, self.largura - MARGEM - peca.largura + 1):
                if self.verificar_espaco(x, y, peca.largura, peca.altura):
                    custo = self.calcular_custo_posicao(x, y, peca.largura, peca.altura)
                    if custo < melhor_custo:
                        melhor_custo = custo
                        melhor_x, melhor_y = x, y

        if melhor_x == -1:
            return float('inf'), -1, -1
        
        return melhor_custo, melhor_x, melhor_y

    def colocar_peca(self, peca, x, y):
        """Coloca a peça fisicamente na placa."""
        peca.x = x
        peca.y = y
        self.ocupar_espaco(x, y, peca.largura, peca.altura)
        self.pecas.append(peca)

def ler_arquivo_pecas(caminho_arquivo):
    """Lê o arquivo com as especificações das peças."""
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    
    num_pecas = int(linhas[0].strip())
    pecas = []
    
    for i in range(1, min(num_pecas + 1, len(linhas))):
        largura, altura = map(int, linhas[i].strip().split())
        pecas.append(Peca(largura, altura, i))
    
    if len(pecas) != num_pecas:
        print(f"AVISO: O arquivo dizia {num_pecas} peças, mas {len(pecas)} foram lidas.")
        
    return pecas

def desenhar_placa(placa, idx, arquivo_saida):
    """Desenha uma única placa em um PNG."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    ax.set_xlim(0, PLACA_LARGURA)
    ax.set_ylim(0, PLACA_ALTURA)
    ax.set_aspect('equal')
    ax.set_title(f'Placa {idx + 1}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Largura (cm)')
    ax.set_ylabel('Altura (cm)')
    ax.grid(True, alpha=0.3)

    placa_rect = patches.Rectangle(
        (0, 0), PLACA_LARGURA, PLACA_ALTURA,
        linewidth=3, edgecolor='black', facecolor='lightgray', alpha=0.3
    )
    ax.add_patch(placa_rect)

    cores = plt.cm.get_cmap('Set3').colors
    for peca in placa.pecas:
        cor = cores[peca.id % len(cores)]
        rect = patches.Rectangle(
            (peca.x, peca.y), peca.largura, peca.altura,
            linewidth=2, edgecolor='black', facecolor=cor, alpha=0.7
        )
        ax.add_patch(rect)

        texto = f"P{peca.id}\n{peca.largura}x{peca.altura}"
        ax.text(
            peca.x + peca.largura/2, peca.y + peca.altura/2,
            texto, ha='center', va='center', fontsize=9,
            fontweight='bold', color='black'
        )

    plt.tight_layout()
    plt.savefig(arquivo_saida, dpi=150, bbox_inches='tight')
    plt.close()

def salvar_solucao_em_pasta(placas, pasta, custo_total, tempo_segundos):
    os.makedirs(pasta, exist_ok=True)

    # Salvar cada placa separadamente
    for idx, placa in enumerate(placas, start=1):
        caminho_png = os.path.join(pasta, f"placa_{idx}.png")
        desenhar_placa(placa, idx-1, caminho_png)

    # Salvar info da solução
    info_txt = os.path.join(pasta, "info.txt")
    with open(info_txt, "w", encoding="utf-8") as f:
        f.write(f"Placas: {len(placas)}\n")
        f.write(f"Custo: R${custo_total:.2f}\n")
        f.write(f"Tempo: {tempo_segundos:.3f}s\n")

    print(f"✓ Solução salva em: {pasta}")

def calcular_solucao(pecas_ordenadas):
    """
    Calcula o custo REAL para uma ordem específica de peças.
    
    Custo Total = (número de placas × R$1000) + (comprimento total de corte × R$0,01/cm)
    """
    placas = [Placa()]
    custo_total = PLACA_CUSTO  # Primeira placa já custa R$1000
    
    for peca in pecas_ordenadas:
        melhor_custo_global = float('inf')
        melhor_acao = None
        
        # 1. Tentar colocar em placas existentes
        for idx, placa in enumerate(placas):
            custo_pos, x, y = placa.encontrar_melhor_posicao(peca)
            if custo_pos < melhor_custo_global:
                melhor_custo_global = custo_pos
                melhor_acao = ('existente', idx, custo_pos, x, y)
        
        # 2. Tentar colocar em uma nova placa
        placa_teste = Placa()
        custo_nova_pos, x_nova, y_nova = placa_teste.encontrar_melhor_posicao(peca)
        
        # 3. Verificar se a peça cabe em algum lugar
        if custo_nova_pos == float('inf') and melhor_custo_global == float('inf'):
            return [], float('inf')  # Peça não cabe nem sozinha
        
        # 4. Comparar: usar placa existente vs. criar nova placa
        # Custo de criar nova placa = R$1000 (placa) + custo de corte
        custo_opcao_nova = PLACA_CUSTO + custo_nova_pos if custo_nova_pos != float('inf') else float('inf')
        
        if custo_opcao_nova < melhor_custo_global:
            # Criar nova placa
            nova_placa = Placa()
            nova_placa.colocar_peca(peca, x_nova, y_nova)
            placas.append(nova_placa)
            custo_total += PLACA_CUSTO + custo_nova_pos
        else:
            # Usar placa existente
            _, idx, custo_pos, x, y = melhor_acao
            placas[idx].colocar_peca(peca, x, y)
            custo_total += custo_pos
    
    return placas, custo_total

def forca_bruta(arquivo_entrada):
    """Algoritmo de força bruta que testa todas as permutações."""
    print("\n" + "="*60)
    print("🔧 ALGORITMO DE FORÇA BRUTA - CORTE DE PLACAS")
    print("   (Sem rotação, com margem de 10cm, custo real)")
    print("="*60)
    
    os.makedirs('output', exist_ok=True)
    
    pecas_originais = ler_arquivo_pecas(arquivo_entrada)
    num_pecas = len(pecas_originais)
    if num_pecas == 0:
        print("❌ Nenhuma peça válida lida do arquivo.")
        return

    print(f"\n📦 Peças carregadas: {num_pecas}")
    for peca in pecas_originais:
        print(f"   • {peca}")
    
    print(f"\n📐 Dimensões da placa: {PLACA_LARGURA}x{PLACA_ALTURA} cm")
    print(f"   Área útil: {PLACA_LARGURA-2*MARGEM}x{PLACA_ALTURA-2*MARGEM} cm (margem de {MARGEM}cm)")
    print(f"💰 Custos:")
    print(f"   • Placa: R$ {PLACA_CUSTO:.2f}")
    print(f"   • Laser: R$ {LASER_CUSTO_POR_CM:.2f} por cm")
    
    total_permutacoes = math.factorial(num_pecas)
    print(f"\n📊 Total de permutações a testar: {total_permutacoes}")
    
    melhor_custo = float('inf')
    melhor_solucao = None
    melhor_ordem = None
    contador = 0
    tempo_inicio = time.time()
    
    print("\n🔄 Processando permutações...")
    
    for ordem in permutations(range(num_pecas)):
        contador += 1
        print(f"\n🔄 permutação #{contador}: {[pecas_originais[i].id for i in ordem]}")

        pecas_ordenadas = [
            Peca(pecas_originais[i].largura, 
                 pecas_originais[i].altura, 
                 pecas_originais[i].id)
            for i in ordem
        ]
        placas, custo = calcular_solucao(pecas_ordenadas)
        
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = placas
            melhor_ordem = ordem
            tempo_decorrido = time.time() - tempo_inicio
            
            print(f"\n✨ NOVA MELHOR SOLUÇÃO!")
            print(f"   • Permutação #{contador}")
            print(f"   • Ordem ID: {[pecas_originais[i].id for i in ordem]}")
            print(f"   • Custo: R$ {custo:.2f}")
            print(f"   • Placas: {len(placas)}")
            print(f"   • Tempo: {tempo_decorrido:.3f}s")
            
            pasta = os.path.join('output', f'solucao # {contador}')
            salvar_solucao_em_pasta(placas, pasta, custo, tempo_decorrido)
        
        if contador % 100 == 0 or contador == total_permutacoes:
            tempo_decorrido = time.time() - tempo_inicio
            print(f"   [{contador}/{total_permutacoes}] Tempo: {tempo_decorrido:.2f}s | Melhor: R$ {melhor_custo:.2f}")
    
    tempo_total = time.time() - tempo_inicio
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO CONCLUÍDO")
    print("="*60)
    
    if melhor_solucao:
        print(f"🏆 MELHOR SOLUÇÃO:")
        print(f"   • Custo total: R$ {melhor_custo:.2f}")
        print(f"   • Ordem: {[pecas_originais[i].id for i in melhor_ordem]}")
        print(f"   • Placas: {len(melhor_solucao)}")
        print(f"   • Permutações testadas: {contador}")
        print(f"   • Tempo: {tempo_total:.3f}s")
        
        pasta_final = os.path.join('output', 'solucao final')
        salvar_solucao_em_pasta(melhor_solucao, pasta_final, melhor_custo, tempo_total)
    else:
        print("❌ Nenhuma solução viável encontrada.")

if __name__ == "__main__":
    arquivo_entrada = "pecas.txt"
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo '{arquivo_entrada}' não encontrado!")
        print("\n📝 Criando arquivo de exemplo...")
        
        with open(arquivo_entrada, 'w') as f:
            f.write("5\n")
            f.write("200 250\n")  # Peça 1
            f.write("50 50\n")    # Peça 2
            f.write("200 200\n")  # Peça 3
            f.write("70 250\n")   # Peça 4
            f.write("50 250\n")   # Peça 5
        
        print(f"✓ Arquivo '{arquivo_entrada}' criado com 5 peças de exemplo")
    
    forca_bruta(arquivo_entrada)