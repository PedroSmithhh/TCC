<template>
  <div class="graficos-container">
    <h2>Gráficos de Acidentes</h2>
    <p>Análise exploratória dos dados de acidentes em Bauru (2022-2025).</p>
    
    <hr>

    <div class="filtros-container">
      <div class="filtro">
        <label for="filtro-chuva">Condição Climática:</label>
        <select id="filtro-chuva" v-model="filtroChuva">
          <option value="Todos">Todos</option>
          <option value="Sem chuva">Sem Chuva</option>
          <option value="Chuva fraca">Chuva Fraca</option>
          <option value="Chuva moderada">Chuva Moderada</option>
          <option value="Chuva forte">Chuva Forte</option>
          <option value="Chuva violenta">Chuva Violenta</option>
        </select>
      </div>

      <div class="filtro">
        <label for="data-inicio">Data Início:</label>
        <input type="date" id="data-inicio" v-model="filtroDataInicio" :min="minData" :max="maxData">
      </div>

      <div class="filtro">
        <label for="data-fim">Data Fim:</label>
        <input type="date" id="data-fim" v-model="filtroDataFim" :min="minData" :max="maxData">
      </div>
    </div>
    <hr>

    <div class="grafico-secao">
      <h3>Distribuição de Acidentes por Hora do Dia</h3>
      
      <div class="chart-wrapper">
        <BarChart
          v-if="timeChartDataComputado"
          :chartData="timeChartDataComputado"
          :chartOptions="timeChartOptions"
        />
      </div>
      
      <div class="analise">
        <h4>Análise:</h4>
        <p>Contagem do número de <strong>acidentes</strong> ocorridos em cada hora do dia, com base nos filtros selecionados.</p>
      </div>
    </div>

    <hr> 

    <div class="grafico-secao">
      <h3>Distribuição de Gravidade por Tipo de Veículo (em Nº de Acidentes)</h3>
      
      <div class="chart-wrapper">
        <BarChart
          v-if="vehicleDataComputado"
          :chartData="vehicleDataComputado"
          :chartOptions="vehicleChartOptions" 
        />
      </div>
      
      <div class="analise">
        <h4>Análise:</h4>
        <p>Contagem do número de <strong>acidentes únicos</strong>. A gravidade do acidente é definida pela vítima mais grave envolvida (Fatal > Grave > Leve > Ileso).</p>
      </div>
    </div>

  </div>
</template>

<script>
// Importa o "molde" do gráfico
import BarChart from './BarChart.vue'

export default {
  name: 'GraficoAcidentes',
  components: {
    BarChart
  },
  data() {
    return {
      listaAcidentes: [], // Guarda o JSON
      filtroChuva: 'Todos',
      filtroDataInicio: '',
      filtroDataFim: '',
      minData: '',
      maxData: '',
      timeChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Nº de Acidentes' } },
          x: { title: { display: true, text: 'Hora do Dia' } }
        }
      },
      vehicleChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            stacked: false, // Lado a lado
            title: { display: true, text: 'Nº de Acidentes' }
          },
          x: {
            stacked: false, // Lado a lado
            title: { display: true, text: 'Tipo de Veículo' }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          }
        }
      }
    }
  },

  // Cria propriedades reativas
  computed: {
    /**
     * Propriedade central que aplica TODOS os filtros (Data e Chuva)
     * à nossa lista base 'listaAcidentes'.
     * Todos os gráficos vão usar este resultado.
     */
    acidentesFiltrados() {
      // 1. Espera os dados carregarem e os filtros serem definidos
      if (!this.listaAcidentes.length || !this.filtroDataInicio || !this.filtroDataFim) {
        return [];
      }

      // 2. Converte as strings dos filtros de data (YYYY-MM-DD) para Objetos Date
      const [yI, mI, dI] = this.filtroDataInicio.split('-').map(Number);
      const startDate = new Date(yI, mI - 1, dI);
      const [yF, mF, dF] = this.filtroDataFim.split('-').map(Number);
      const endDate = new Date(yF, mF - 1, dF);

      // 3. Aplica os filtros em cadeia
      let dadosFiltrados = this.listaAcidentes;

      // Filtro de Chuva
      if (this.filtroChuva !== 'Todos') {
        dadosFiltrados = dadosFiltrados.filter(ac => ac.Chuva === this.filtroChuva);
      }

      // Filtro de Data (usando o 'ac.dateObj' que criamos no 'mounted')
      dadosFiltrados = dadosFiltrados.filter(ac => {
        return ac.dateObj >= startDate && ac.dateObj <= endDate;
      });

      return dadosFiltrados;
    },

    timeChartDataComputado() {
      const dadosFiltrados = this.acidentesFiltrados;
      if (!dadosFiltrados) return null;

      // Lógica: Contar acidentes por hora
      const contagemPorHora = new Array(24).fill(0);
      for (const acidente of dadosFiltrados) {
        if (acidente.hora_sinistro !== null && acidente.hora_sinistro >= 0 && acidente.hora_sinistro <= 23) {
          contagemPorHora[acidente.hora_sinistro]++;
        }
      }

      return {
        labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
        datasets: [
          {
            label: `Nº de Acidentes (${this.filtroChuva})`,
            backgroundColor: '#007bff',
            data: contagemPorHora
          }
        ]
      }
    },

    vehicleDataComputado() {
      const dadosFiltrados = this.acidentesFiltrados;
      if (!dadosFiltrados) return null;

      // 1. Define as categorias (do JSON 'dados_acidentes.json')
      const gravidades = ['gravidade_leve', 'gravidade_grave', 'gravidade_fatal'];
      const veiculos = {
        'AUTOMOVEL': 'tp_veiculo_automovel',
        'MOTOCICLETA': 'tp_veiculo_motocicleta',
        'BICICLETA': 'tp_veiculo_bicicleta',
        'CAMINHAO': 'tp_veiculo_caminhao',
        'ONIBUS': 'tp_veiculo_onibus',
        'OUTROS': 'tp_veiculo_outros'
      };
      
      const labelsVeiculos = Object.keys(veiculos); // Eixo X

      // 2. Cria os datasets (um para 'LEVE', um para 'GRAVE', um para 'FATAL')
      const datasets = gravidades.map(grav => { // ex: grav = 'gravidade_leve'
        const cor = this.getCorGravidade(grav.split('_')[1].toUpperCase());
        
        return {
          label: grav.split('_')[1].toUpperCase(), // ex: 'LEVE'
          
          // 3. Lógica de Contagem de ACIDENTES
          data: labelsVeiculos.map(labelVeiculo => { // ex: labelVeiculo = 'BICICLETA'
            const colunaVeiculo = veiculos[labelVeiculo]; // ex: 'tp_veiculo_bicicleta'
            
            // Filtra os acidentes (já filtrados por data/chuva)
            // que satisfazem as DUAS condições:
            // 1. O veículo estava envolvido (ex: ac['tp_veiculo_bicicleta'] > 0)
            // 2. A gravidade ocorreu (ex: ac['gravidade_leve'] > 0)
            const contagem = dadosFiltrados.filter(ac => 
              ac[colunaVeiculo] > 0 && ac[grav] > 0
            ).length; // Retorna a CONTAGEM de acidentes
            
            return contagem;
          }),
          backgroundColor: cor,
        };
      });

      return {
        labels: labelsVeiculos,
        datasets: datasets
      }
    },
  },

  methods: {
    // Helper para formatar data (YYYY-MM-DD)
    formatDateForInput(date) {
      const y = date.getFullYear();
      const m = (date.getMonth() + 1).toString().padStart(2, '0');
      const d = date.getDate().toString().padStart(2, '0');
      return `${y}-${m}-${d}`;
    },
    // Helper para dar cores às barras
    getCorGravidade(gravidade) {
      switch (gravidade) {
        case 'LEVE': return '#ffc107'; // Amarelo
        case 'GRAVE': return '#fd7e14'; // Laranja
        case 'FATAL': return '#dc3545'; // Vermelho
        default: return '#007bff';
      }
    }
  },

  // Executar um trecho de código após o componente ter sido totalmente montado no DOM
  mounted() {
    // Busca o arquivo JSON que criamos (da pasta /public)
    fetch('/dados_graficos.json')
      .then(response => response.json())
      .then(data => {
        
        let minDate = new Date(2100, 0, 1);
        let maxDate = new Date(1900, 0, 1);

        // Pré-processa os dados UMA VEZ
        const processedData = data.map(acidente => {
          // O JSON vem com data 'YYYY-MM-DDTHH:MM:SSZ' (formato ISO)
          const dateObj = new Date(acidente.data_sinistro);
          
          if (dateObj < minDate) minDate = dateObj;
          if (dateObj > maxDate) maxDate = dateObj;

          // Cria 'acidente.dateObj' para ser usado na filtragem (muito mais rápido)
          acidente.dateObj = dateObj;
          return acidente;
        });
        
        this.listaAcidentes = processedData;

        // Define os valores padrão para os filtros de data
        this.minData = this.formatDateForInput(minDate);
        this.maxData = this.formatDateForInput(maxDate);
        this.filtroDataInicio = this.minData;
        this.filtroDataFim = this.maxData;

        console.log("DADOS CORRETOS (1 linha/acidente) CARREGADOS!");
      })
      .catch(error => {
        console.error("Erro ao carregar dados_acidentes.json:", error);
      });
  }
}
</script>

<style>
/* --- ESTILOS CSS COMPLETOS --- */
.graficos-container {
  padding: 20px;
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  max-width: 1200px;
  margin: 0 auto;
}
.grafico-secao {
  margin-bottom: 30px;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.grafico-secao h3 {
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 5px;
}
.chart-wrapper {
  position: relative;
  height: 400px;
  margin-top: 20px;
}

/* Container dos Filtros */
.filtros-container {
  display: flex;
  flex-wrap: wrap; /* Quebra linha em telas pequenas */
  gap: 20px; /* Espaço entre os filtros */
  margin-top: 15px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 5px;
  align-items: center;
}
.filtro {
  display: flex;
  align-items: center;
}
.filtro label {
  font-weight: bold;
  margin-right: 10px;
  font-size: 0.9em;
}
.filtro select, .filtro input {
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 0.9em;
}

/* Caixa de Análise */
.analise {
  margin-top: 20px;
  background-color: #f9f9f9;
  border-left: 4px solid #007bff;
  padding: 10px 15px;
}
.analise h4 {
  margin-top: 0;
  color: #0056b3;
}
.analise p {
  color: #555;
}

hr {
  border: 0;
  height: 1px;
  background-color: #ccc;
  margin: 40px 0;
}
</style>