import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import permutations
import time
import os

PLACA_LARGURA = 300
PLACA_ALTURA = 250

class Peca:
    def __init__(self, largura, altura, id):
        self.largura = largura
        self.altura = altura
        self.id = id
        self.x = 0
        self.y = 0
        self.rotacionada = False
    
    def __repr__(self):
        return f"Peça {self.id}: {self.largura}x{self.altura}"

class Placa:
    def __init__(self):
        self.largura = PLACA_LARGURA
        self.altura = PLACA_ALTURA
        # ATENÇÃO: Usar uma matriz de ocupação píxel a píxel é EXTREMAMENTE LENTO
        # para este tipo de problema. A abordagem correta seria gerir uma lista
        # de retângulos livres, mas mantivemos a sua lógica original.
        self.ocupacao = [[False for _ in range(self.largura)] for _ in range(self.altura)]
        self.pecas = []
    
    def limpar(self):
        self.ocupacao = [[False for _ in range(self.largura)] for _ in range(self.altura)]
        self.pecas = []
    
    def area_livre(self):
        return sum(row.count(False) for row in self.ocupacao)
    
    def verificar_espaco(self, x, y, largura, altura):
        """Verifica se há espaço disponível para colocar a peça"""
        if x + largura > self.largura or y + altura > self.altura:
            return False
        
        # A verificação píxel a píxel é o principal gargalo de performance
        for i in range(y, min(y + altura, self.altura)):
            for j in range(x, min(x + largura, self.largura)):
                if self.ocupacao[i][j]:
                    return False
        return True
    
    def ocupar_espaco(self, x, y, largura, altura):
        """Marca o espaço como ocupado"""
        for i in range(y, y + altura):
            for j in range(x, x + largura):
                self.ocupacao[i][j] = True
    
    def calcular_custo_posicao(self, x, y, largura, altura):
        """Calcula o custo de cortar a peça nessa posição"""
        # Custo baseado em:
        # 1. Distância do canto (0,0) - penaliza posições centrais
        # 2. Perda de material nas bordas
        distancia_origem = (x**2 + y**2)**0.5
        custo_posicao = distancia_origem * 0.01
        
        # Penalidade por espaço desperdiçado ao redor
        espaco_desperdicado = 0
        if x + largura < self.largura:
            espaco_desperdicado += (self.largura - (x + largura))
        if y + altura < self.altura:
            espaco_desperdicado += (self.altura - (y + altura))
        
        custo_total = custo_posicao + (espaco_desperdicado * 0.1)
        return custo_total
    
    def encontrar_melhor_posicao(self, peca):
        """
        Encontra a melhor posição (x, y, rotação) para uma peça NESTA placa.
        Retorna (custo, x, y, rotacionada)
        """
        melhor_custo = float('inf')
        melhor_x, melhor_y = -1, -1
        melhor_rotacao = False
        
        # Tenta posições sem rotação
        # ATENÇÃO: Iterar píxel a píxel é muito lento.
        for y in range(self.altura - peca.altura + 1):
            for x in range(self.largura - peca.largura + 1):
                if self.verificar_espaco(x, y, peca.largura, peca.altura):
                    custo = self.calcular_custo_posicao(x, y, peca.largura, peca.altura)
                    if custo < melhor_custo:
                        melhor_custo = custo
                        melhor_x, melhor_y = x, y
                        melhor_rotacao = False
        
        # Tenta posições com rotação (se a peça não for quadrada)
        if peca.largura != peca.altura:
            for y in range(self.altura - peca.largura + 1):
                for x in range(self.largura - peca.altura + 1):
                    if self.verificar_espaco(x, y, peca.altura, peca.largura):
                        custo = self.calcular_custo_posicao(x, y, peca.altura, peca.largura)
                        if custo < melhor_custo:
                            melhor_custo = custo
                            melhor_x, melhor_y = x, y
                            melhor_rotacao = True
        
        if melhor_x == -1:
            return float('inf'), -1, -1, False # Não coube
        
        return melhor_custo, melhor_x, melhor_y, melhor_rotacao

    def colocar_peca(self, peca, x, y, rotacionada):
        """Coloca a peça fisicamente na placa"""
        peca.x = x
        peca.y = y
        peca.rotacionada = rotacionada
        
        if rotacionada:
            self.ocupar_espaco(x, y, peca.altura, peca.largura)
        else:
            self.ocupar_espaco(x, y, peca.largura, peca.altura)
            
        self.pecas.append(peca)

def ler_arquivo_pecas(caminho_arquivo):
    """Lê o arquivo com as especificações das peças"""
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    
    num_pecas = int(linhas[0].strip())
    pecas = []
    
    # CORREÇÃO: Limita a leitura ao número de peças ou ao fim do arquivo
    for i in range(1, min(num_pecas + 1, len(linhas))):
        largura, altura = map(int, linhas[i].strip().split())
        pecas.append(Peca(largura, altura, i))
    
    # CORREÇÃO: Garante que o número de peças lido é o esperado
    if len(pecas) != num_pecas:
        print(f"AVISO: O arquivo dizia {num_pecas} peças, mas {len(pecas)} foram lidas.")
        
    return pecas

def desenhar_solucao(placas, arquivo_saida, titulo="Solução", custo_total=0, tempo=0):
    """Gera uma imagem PNG com a disposição das peças nas placas"""
    num_placas = len(placas)
    if num_placas == 0:
        print("Nenhuma placa para desenhar.")
        return
        
    fig, axes = plt.subplots(1, num_placas, figsize=(8*num_placas, 6))
    
    if num_placas == 1:
        axes = [axes]
    
    cores = plt.cm.get_cmap('Set3').colors
    
    for idx, placa in enumerate(placas):
        ax = axes[idx]
        ax.set_xlim(0, PLACA_LARGURA)
        ax.set_ylim(0, PLACA_ALTURA)
        ax.set_aspect('equal')
        ax.set_title(f'Placa {idx + 1}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Largura (cm)')
        ax.set_ylabel('Altura (cm)')
        ax.grid(True, alpha=0.3)
        
        placa_rect = patches.Rectangle((0, 0), PLACA_LARGURA, PLACA_ALTURA,
                                         linewidth=3, edgecolor='black', 
                                         facecolor='lightgray', alpha=0.3)
        ax.add_patch(placa_rect)
        
        for peca in placa.pecas:
            cor = cores[peca.id % len(cores)]
            
            largura_desenho = peca.largura
            altura_desenho = peca.altura
            if peca.rotacionada:
                largura_desenho = peca.altura
                altura_desenho = peca.largura
            
            rect = patches.Rectangle((peca.x, peca.y), largura_desenho, altura_desenho,
                                       linewidth=2, edgecolor='black', 
                                       facecolor=cor, alpha=0.7)
            ax.add_patch(rect)
            
            texto = f"P{peca.id}\n{peca.largura}x{peca.altura}"
            if peca.rotacionada:
                texto += "\n(ROT)"
            
            ax.text(peca.x + largura_desenho/2, peca.y + altura_desenho/2, 
                   texto, ha='center', va='center', fontsize=9, 
                   fontweight='bold', color='black')
    
    fig.suptitle(f'{titulo}\nCusto Total: {custo_total:.2f} | Tempo: {tempo:.3f}s | Placas: {num_placas}', 
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(arquivo_saida, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Imagem salva: {arquivo_saida}")

def calcular_solucao(pecas_ordenadas):
    """
    Calcula o custo e a disposição para uma ordem específica de peças.
    LÓGICA CORRIGIDA: Agora implementa "Best Fit".
    Testa todas as placas existentes E uma nova placa, e escolhe a
    opção de menor custo total.
    """
    placas = [Placa()]
    custo_total_solucao = 0
    
    for peca in pecas_ordenadas:
        melhor_custo_global = float('inf')
        melhor_acao = None # (tipo, indice_placa, custo, x, y, rot)
        
        # 1. Tenta colocar em todas as placas existentes
        for idx, placa in enumerate(placas):
            custo_pos, x, y, rot = placa.encontrar_melhor_posicao(peca)
            if custo_pos < melhor_custo_global:
                melhor_custo_global = custo_pos
                melhor_acao = ('existente', idx, custo_pos, x, y, rot)
        
        # 2. Tenta colocar em uma placa nova
        placa_teste = Placa()
        custo_nova, x_nova, y_nova, rot_nova = placa_teste.encontrar_melhor_posicao(peca)
        
        # 3. Verifica se a peça é grande demais
        if custo_nova == float('inf') and melhor_custo_global == float('inf'):
            # Peça não cabe nem sozinha em uma placa
            return [], float('inf') # Solução inválida
            
        # 4. Compara o custo de usar uma placa existente vs. uma nova
        # A penalidade de 1000 é pelo uso da placa, não pela posição
        custo_com_nova_placa = custo_nova + 1000 # Penalidade por placa nova
        
        if custo_com_nova_placa < melhor_custo_global:
            # Ação: Criar nova placa
            nova_placa = Placa()
            nova_placa.colocar_peca(peca, x_nova, y_nova, rot_nova)
            placas.append(nova_placa)
            custo_total_solucao += custo_nova # Custo da posição
        else:
            # Ação: Usar placa existente
            tipo, idx, custo, x, y, rot = melhor_acao
            placas[idx].colocar_peca(peca, x, y, rot)
            custo_total_solucao += custo # Custo da posição
            
    # Adiciona a penalidade por placa APENAS no custo total final
    # A lógica de decisão já usou 1000, mas o custo total é a soma
    # dos custos de posição + (N-1)*1000
    custo_total_solucao += (len(placas) - 1) * 1000
    
    return placas, custo_total_solucao

def forca_bruta(arquivo_entrada):
    """Algoritmo de força bruta que testa todas as permutações"""
    print("\n" + "="*60)
    print("🔧 ALGORITMO DE FORÇA BRUTA - CORTE DE PLACAS")
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
        
        # Cria cópias das peças na ordem da permutação
        # É crucial criar novas instâncias para limpar x, y, rotacionada
        pecas_ordenadas = [Peca(pecas_originais[i].largura, 
                                pecas_originais[i].altura, 
                                pecas_originais[i].id) 
                           for i in ordem]
        
        placas, custo = calcular_solucao(pecas_ordenadas)
        
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = placas
            melhor_ordem = ordem
            tempo_decorrido = time.time() - tempo_inicio
            
            print(f"\n✨ NOVA MELHOR SOLUÇÃO ENCONTRADA!")
            print(f"   • Permutação #{contador}")
            print(f"   • Ordem ID: {[pecas_originais[i].id for i in ordem]}")
            print(f"   • Custo: {custo:.2f}")
            print(f"   • Placas usadas: {len(placas)}")
            print(f"   • Tempo: {tempo_decorrido:.3f}s")
            
            arquivo_saida = f'output/solucao_permutacao_{contador}.png'
            desenhar_solucao(placas, arquivo_saida, 
                           f"Melhor Solução (Permutação #{contador})",
                           custo, tempo_decorrido)
        
        # CORREÇÃO: Impressão de progresso movida para cá
        if contador % 100 == 0 or contador == total_permutacoes:
            tempo_decorrido = time.time() - tempo_inicio
            print(f"   Testadas: {contador}/{total_permutacoes} | Tempo: {tempo_decorrido:.2f}s | Melhor Custo: {melhor_custo:.2f}")
    
    tempo_total = time.time() - tempo_inicio
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO CONCLUÍDO")
    print("="*60)
    
    if melhor_solucao:
        print(f"🏆 MELHOR SOLUÇÃO:")
        print(f"   • Custo final: {melhor_custo:.2f}")
        print(f"   • Ordem das peças (por ID): {[pecas_originais[i].id for i in melhor_ordem]}")
        print(f"   • Placas utilizadas: {len(melhor_solucao)}")
        print(f"   • Permutações testadas: {contador}")
        print(f"   • Tempo total: {tempo_total:.3f}s")
        
        desenhar_solucao(melhor_solucao, 'output/solucao_final.png',
                       "🏆 SOLUÇÃO ÓTIMA FINAL", melhor_custo, tempo_total)
    else:
        print("❌ Nenhuma solução viável foi encontrada.")

if __name__ == "__main__":
    arquivo_entrada = "pecas.txt"
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo '{arquivo_entrada}' não encontrado!")
        print("\n📝 Criando arquivo de exemplo...")
        
        # CORREÇÃO: O número de peças agora é 7
        with open(arquivo_entrada, 'w') as f:
            f.write("7\n") # CORRIGIDO DE 5 PARA 7
            f.write("250 200\n") # Peça 1
            f.write("50 50\n")   # Peça 2
            f.write("200 200\n") # Peça 3
            f.write("250 70\n")  # Peça 4
            f.write("50 250\n")  # Peça 5
            f.write("100 150\n") # Peça 6
            f.write("180 90\n")  # Peça 7
        
        print(f"✓ Arquivo '{arquivo_entrada}' criado com 7 peças de exemplo")
    
    forca_bruta(arquivo_entrada)
