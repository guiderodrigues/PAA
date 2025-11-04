import webview

pagina_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analisador de Rotas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding-top: 70px;
        }

        /* Navbar */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            padding: 0 2rem;
        }

        .nav-btn {
            background: white;
            border: 2px solid #3b82f6;
            color: #3b82f6;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .nav-btn:hover {
            background: #eff6ff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .nav-btn-active {
            background: #3b82f6;
            color: white;
        }

        /* Container Principal */
        .screen {
            display: none;
            max-width: 1800px;
            margin: 2rem auto;
            padding: 2rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .screen-active {
            display: block;
            animation: fadeIn 0.3s ease forwards;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Container de Seções Horizontal */
        .sections-container {
            display: flex;
            gap: 1.5rem;
            align-items: stretch;
             height: calc(100vh - 160px);
        }

        /* Seções */
        .section {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #3b82f6;
            flex-shrink: 0;
        }

        /* Botões de Ação */
        .action-buttons {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            white-space: nowrap;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
        }

        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .btn-secondary {
            background: #10b981;
            color: white;
        }

        .btn-secondary:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        /* Container de Entrada (com status + imagem) */
        .input-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            flex-grow: 1;
        }

        /* Status */
        .status-box {
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Container de Preview da Imagem */
        .image-preview {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
            flex-grow: 1;
        }

        .image-preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }

        .image-preview-empty {
            color: #94a3b8;
            font-style: italic;
            text-align: center;
        }

        /* Container de Solução */
        .solution-container {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #64748b;
            font-style: italic;
            flex-grow: 1;
            overflow: auto;
        }

        /* Container de Poda */
        .poda-container {
            background: #fef3c7;
            border: 2px solid #fbbf24;
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 400px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .poda-letter {
            font-size: 3rem;
            font-weight: 900;
            color: #dc2626;
            text-align: center;
            margin-bottom: 1rem;
            flex-shrink: 0;
        }

        .poda-placeholder {
            background: white;
            border: 2px dashed #fbbf24;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            color: #92400e;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-grow: 1;
        }

        /* Árvore */
        .tree-container {
            background: #f0fdf4;
            border: 2px solid #86efac;
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #166534;
            font-style: italic;
            flex-grow: 1;
        }

        /* Resultados */
        .results-container {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 400px;
            flex-grow: 1;
        }

        .results-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 1rem;
        }

        /* Input File Oculto */
        input[type="file"] {
            display: none;
        }

        /* Responsive */
        @media (max-width: 1200px) {
            .sections-container {
                flex-direction: column;
            }

            .section {
                min-height: auto;
            }
        }

        @media (max-width: 768px) {
            .navbar {
                flex-wrap: wrap;
                height: auto;
                padding: 1rem;
            }

            .nav-btn {
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
            }

            .screen {
                padding: 1rem;
            }

            body {
                padding-top: 120px;
            }
        }
    </style>
</head>
<body>
    <!-- Navbar Fixa -->
    <nav class="navbar">
        <button class="nav-btn nav-btn-active" onclick="switchScreen('bruto')">Bruto</button>
        <button class="nav-btn" onclick="switchScreen('bnb')">Branch and Bound</button>
        <button class="nav-btn" onclick="switchScreen('heuristica')">Heurística</button>
    </nav>

    <!-- Tela Bruto -->
    <div id="screen-bruto" class="screen screen-active">
        <div class="sections-container">
            <!-- Seção 1: Entrada e Processamento -->
            <div class="section">
                <h2 class="section-title">Entrada e Processamento</h2>
                <div class="action-buttons">
                    <input type="file" id="fileBruto" accept=".png,.jpg,.jpeg">
                    <button class="btn btn-primary" onclick="document.getElementById('fileBruto').click()">
                        📁 Carregar Placas
                    </button>
                    <button class="btn btn-secondary" onclick="processarBruto()">
                        ▶️ Processar
                    </button>
                </div>
                <div class="input-container">
                    <div id="statusBruto" class="status-box">
                        Aguardando arquivo...
                    </div>
                    <div id="previewBruto" class="image-preview">
                        <span class="image-preview-empty">Nenhuma imagem carregada</span>
                    </div>
                </div>
            </div>

            <!-- Seção 2: Solução Atual -->
            <div class="section">
                <h2 class="section-title">Solução Atual</h2>
                <div id="solucaoAtualBruto" class="solution-container">
                    Solução ótima atual (INSERIR JS AQUI para desenhar)
                </div>
            </div>

            <!-- Seção 3: Solução Antiga -->
            <div class="section">
                <h2 class="section-title">Solução Antiga</h2>
                <div id="solucaoAntigaBruto" class="solution-container">
                    Solução antiga (INSERIR JS AQUI para desenhar)
                </div>
            </div>
        </div>
    </div>

    <!-- Tela Branch and Bound -->
    <div id="screen-bnb" class="screen">
        <div class="sections-container">
            <!-- Seção 1: Entrada e Processamento -->
            <div class="section">
                <h2 class="section-title">Entrada e Processamento</h2>
                <div class="action-buttons">
                    <input type="file" id="fileBnB" accept=".png,.jpg,.jpeg">
                    <button class="btn btn-primary" onclick="document.getElementById('fileBnB').click()">
                        📁 Carregar Placas
                    </button>
                    <button class="btn btn-secondary" onclick="processarBnB()">
                        ▶️ Processar
                    </button>
                </div>
                <div class="input-container">
                    <div id="statusBnB" class="status-box">
                        Aguardando arquivo...
                    </div>
                    <div id="previewBnB" class="image-preview">
                        <span class="image-preview-empty">Nenhuma imagem carregada</span>
                    </div>
                </div>
            </div>

            <!-- Seção 2: Solução Atual -->
            <div class="section">
                <h2 class="section-title">Solução Atual</h2>
                <div id="solucaoAtualBnB" class="solution-container">
                    Solução ótima atual (INSERIR JS AQUI)
                </div>
            </div>

            <!-- Seção 3: Podas -->
            <div class="section">
                <h2 class="section-title">Podas</h2>
                <div id="podaBnB" class="poda-container">
                    <div class="poda-letter">P</div>
                    <div class="poda-placeholder">
                        Configuração podada (INSERIR JS AQUI)
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Tela Heurística -->
    <div id="screen-heuristica" class="screen">
        <div class="sections-container">
            <!-- Seção 1: Entrada e Processamento -->
            <div class="section">
                <h2 class="section-title">Entrada e Processamento</h2>
                <div class="action-buttons">
                    <input type="file" id="fileHeuristica" accept=".png,.jpg,.jpeg">
                    <button class="btn btn-primary" onclick="document.getElementById('fileHeuristica').click()">
                        📁 Carregar Placas
                    </button>
                    <button class="btn btn-secondary" onclick="processarHeuristica()">
                        ▶️ Processar
                    </button>
                </div>
                <div class="input-container">
                    <div id="statusHeuristica" class="status-box">
                        Aguardando arquivo...
                    </div>
                    <div id="previewHeuristica" class="image-preview">
                        <span class="image-preview-empty">Nenhuma imagem carregada</span>
                    </div>
                </div>
            </div>

            <!-- Seção 2: Árvore de Decisão -->
            <div class="section">
                <h2 class="section-title">Árvore de Decisão</h2>
                <div id="arvoreHeuristica" class="tree-container">
                    Arvore da heurística (INSERIR JS AQUI para desenhar árvore de decisões)
                </div>
            </div>

            <!-- Seção 3: Resultados -->
            <div class="section">
                <h2 class="section-title">Resultados da Heurística</h2>
                <div id="resultadosHeuristica" class="results-container">
                    <p style="color: #64748b; font-style: italic;">Métricas serão exibidas aqui após processamento</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Navegação entre telas
        function switchScreen(screenName) {
            document.querySelectorAll('.screen').forEach(s => {
                s.classList.remove('screen-active');
            });
            document.querySelectorAll('.nav-btn').forEach(b => {
                b.classList.remove('nav-btn-active');
            });

            document.getElementById('screen-' + screenName).classList.add('screen-active');
            event.target.classList.add('nav-btn-active');
        }

        // Função para mostrar imagem no preview
        function mostrarImagem(event, previewId, statusId) {
            const file = event.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById(previewId);
                    preview.innerHTML = `<img src="${e.target.result}" alt="Placas carregadas">`;
                    document.getElementById(statusId).textContent = 'Imagem carregada: ' + file.name;
                };
                reader.readAsDataURL(file);
            }
        }

        // Handlers de arquivo com preview
        document.getElementById('fileBruto').addEventListener('change', function(e) {
            mostrarImagem(e, 'previewBruto', 'statusBruto');
        });

        document.getElementById('fileBnB').addEventListener('change', function(e) {
            mostrarImagem(e, 'previewBnB', 'statusBnB');
        });

        document.getElementById('fileHeuristica').addEventListener('change', function(e) {
            mostrarImagem(e, 'previewHeuristica', 'statusHeuristica');
        });

        // Funções de processamento
        async function processarBruto() {
            document.getElementById('statusBruto').textContent = 'Processando...';
            try {
                const result = await window.pywebview.api.on_process_bruto();
                document.getElementById('statusBruto').textContent = 'Processamento concluído: ' + result;
            } catch (error) {
                document.getElementById('statusBruto').textContent = 'Erro ao processar: ' + error;
            }
        }

        async function processarBnB() {
            document.getElementById('statusBnB').textContent = 'Processando...';
            try {
                const result = await window.pywebview.api.on_process_bnb();
                document.getElementById('statusBnB').textContent = 'Processamento concluído: ' + result;
            } catch (error) {
                document.getElementById('statusBnB').textContent = 'Erro ao processar: ' + error;
            }
        }

        async function processarHeuristica() {
            document.getElementById('statusHeuristica').textContent = 'Processando...';
            try {
                const result = await window.pywebview.api.on_process_heuristica();
                document.getElementById('statusHeuristica').textContent = 'Processamento concluído: ' + result;
            } catch (error) {
                document.getElementById('statusHeuristica').textContent = 'Erro ao processar: ' + error;
            }
        }

        // Funções stub para atualização de visualizações
        function updateBrutoSolucaoAtual(data) {
            console.log('Atualizando solução atual bruto:', data);
        }

        function updateBrutoSolucaoAntiga(data) {
            console.log('Atualizando solução antiga bruto:', data);
        }

        function updateBnBSolucaoAtual(data) {
            console.log('Atualizando solução atual BnB:', data);
        }

        function updateBnBPodas(data) {
            console.log('Atualizando podas:', data);
        }

        function updateArvoreHeuristica(data) {
            console.log('Atualizando árvore heurística:', data);
        }

        function updateResultadosHeuristica(data) {
            console.log('Atualizando resultados heurística:', data);
        }
    </script>
</body>
</html>
"""

class Api:
    def on_process_bruto(self):
        print("Processamento bruto iniciado")
        return "OK"
    
    def on_process_bnb(self):
        print("Processamento Branch and Bound iniciado")
        return "OK"
    
    def on_process_heuristica(self):
        print("Processamento heurística iniciado")
        return "OK"

api = Api()

if __name__ == "__main__":
    webview.create_window(
        "Analisador de Rotas",
        html=pagina_html,
        width=1920,
        height=1080,
        js_api=api
    )
    webview.start()