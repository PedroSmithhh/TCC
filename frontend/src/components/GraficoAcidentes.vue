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

    <div v-if="loading" class="loading-aviso">
      Carregando dados...
    </div>

    <div v-if="!loading" class="graficos-grid">
      <div class="grafico-secao">
        <h3>Número de Acidentes por Tipo de Veículo Envolvido</h3>
        <div class="chart-wrapper">
          <canvas id="graficoAcidentesPorVeiculo"></canvas>
        </div>
      </div>

      <div class="grafico-secao">
        <h3>Acidentes por Hora do Dia</h3>
        <div class="chart-wrapper">
          <canvas id="graficoAcidentesPorHora"></canvas>
        </div>
      </div>

      <div class="grafico-secao">
        <h3>Vítimas por Faixa Etária e Gravidade</h3>
        <div class="chart-wrapper">
          <canvas id="graficoVitimasFaixaEtaria"></canvas>
        </div>
      </div>

      <div class="grafico-secao">
        <h3>Número de Acidentes por Tipo de de Via</h3>
        <div class="chart-wrapper">
          <canvas id="graficoAcidentesPorVia"></canvas>
        </div>
      </div>

      <div class="grafico-secao">
        <h3>Impacto da Chuva na Gravidade das Vítimas</h3>
        <div class="chart-wrapper">
          <canvas id="graficoImpactoChuva"></canvas>
        </div>
      </div>
      
    </div>

  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import axios from 'axios';

Chart.register(...registerables);

export default {
  name: 'GraficoAcidentes',
  data() {
    return {
      allAcidentes: [],
      allVitimas: [],
      filtroChuva: 'Todos',
      filtroDataInicio: '',
      filtroDataFim: '',
      minData: '2022-01-01',
      maxData: '2025-02-28',
      loading: true,
    };
  },

  created() {
    this.chartAcidentesPorVeiculo = null; // GRÁFICO 1
    this.chartAcidentesPorHora = null; // GRÁFICO 2
    this.chartVitimasFaixaEtaria = null; // GRÁFICO 3
    this.chartAcidentesPorVia = null; // GRÁFICO 4
    this.chartImpactoChuva = null; // GRÁFICO 5
  },

  // Funções que retornam um valor dependente de outros dados reativos
  computed: {
    filteredAcidentes() {
      return this.allAcidentes.filter(acidente => {
        const filtroChuvaOk = this.filtroChuva === 'Todos' || acidente.Chuva === this.filtroChuva;
        const filtroDataInicioOk = !this.filtroDataInicio || acidente.data_sinistro >= this.filtroDataInicio;
        const filtroDataFimOk = !this.filtroDataFim || acidente.data_sinistro <= this.filtroDataFim;
        return filtroChuvaOk && filtroDataInicioOk && filtroDataFimOk;
      });
    },

    filteredVitimas() {
      return this.allVitimas.filter(vitima => {
        const filtroChuvaOk = this.filtroChuva === 'Todos' || vitima.Chuva === this.filtroChuva;
        const filtroDataInicioOk = !this.filtroDataInicio || vitima.data_sinistro >= this.filtroDataInicio;
        const filtroDataFimOk = !this.filtroDataFim || vitima.data_sinistro <= this.filtroDataFim;
        return filtroChuvaOk && filtroDataInicioOk && filtroDataFimOk;
      });
    }
  },

  // Permite observar mudanças em propriedades reativas
  watch: {
    filtroChuva() {
      this.updateAllCharts();
    },
    filtroDataInicio() {
      this.updateAllCharts();
    },
    filtroDataFim() {
      this.updateAllCharts();
    }
  },

  // Executado imediatamente após o componente ter sido montado no DOM
  async mounted() {
    await this.loadData();
    if (!this.loading) {
      this.createChartInstances();
      this.setupFiltrosDatas();
    }
  },

  // Métodos do componente
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const [responseAcidentes, responseVitimas] = await Promise.all([
          axios.get('/dados_grafico_acidentes.json'),
          axios.get('/dados_grafico_vitimas.json')
        ]);
        this.allAcidentes = responseAcidentes.data;
        this.allVitimas = responseVitimas.data;
      } catch (error) {
        console.error("Erro ao carregar os dados JSON:", error);
        alert("Falha ao carregar dados. Verifique o console para mais detalhes.");
      } finally {
        this.loading = false;
      }
    },

    setupFiltrosDatas() {
      if (this.allAcidentes.length === 0) return;
      let min = this.allAcidentes[0].data_sinistro;
      let max = this.allAcidentes[0].data_sinistro;
      for (const acidente of this.allAcidentes) {
        if (acidente.data_sinistro < min) min = acidente.data_sinistro;
        if (acidente.data_sinistro > max) max = acidente.data_sinistro;
      }
      this.minData = min;
      this.maxData = max;
      this.filtroDataInicio = min;
      this.filtroDataFim = max;
    },

    createChartInstances() {
      // GRÁFICO 1 (Veículos)
      const ctx1 = document.getElementById('graficoAcidentesPorVeiculo').getContext('2d');
      this.chartAcidentesPorVeiculo = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels: [],
          datasets: []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Nº de Acidentes'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Tipo de Veículo'
              }
            }
          },
          plugins: { legend: { display: false } }
        }
      });

      // GRÁFICO 2 (Hora)
      const ctx2 = document.getElementById('graficoAcidentesPorHora').getContext('2d');
      this.chartAcidentesPorHora = new Chart(ctx2, {
        type: 'bar',
        data: { 
          labels: [], 
          datasets: [] 
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { 
              beginAtZero: true, 
              title: { 
                display: true, 
                text: 'Nº de Acidentes' 
              } 
            },
            x: { 
              title: { 
                display: true, 
                text: 'Hora do Dia' 
              } 
            }
          },
          plugins: { legend: { display: false } }
        }
      });

      // GRÁFICO 3 (Vítimas)
      const ctx3 = document.getElementById('graficoVitimasFaixaEtaria').getContext('2d');
      this.chartVitimasFaixaEtaria = new Chart(ctx3, {
        type: 'bar',
        data: { 
          labels: [], 
          datasets: [] 
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          scales: {
            x: { 
              beginAtZero: true, 
              stacked: true, 
              title: { 
                display: true, 
                text: 'Nº de Vítimas' 
              } 
            },
            y: { 
              stacked: true, 
              title: { 
                display: true, 
                text: 'Faixa Etária' 
              } 
            }
          },
          plugins: { legend: { position: 'top' } }
        }
      });

    // Gráfico 4 (Tipo de Via)
    const ctx4 = document.getElementById('graficoAcidentesPorVia').getContext('2d');
      this.chartAcidentesPorVia = new Chart(ctx4, {
        type: 'bar',
        data: {
          labels: [],
          datasets: []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Nº de Acidentes'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Tipo de Via'
              }
            }
          },
          plugins: { legend: { display: false } }
        }
      });

      // GRÁFICO 5 (Impacto da Chuva)
      const ctx5 = document.getElementById('graficoImpactoChuva').getContext('2d');
      this.chartImpactoChuva = new Chart(ctx5, {
        type: 'bar',
        data: {
          labels: [],
          datasets: []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          scales: {
            x: {
              beginAtZero: true,
              stacked: true,
              title: {
                display: true,
                text: 'Nº de Vítimas'
              }
            },
            y: {
              stacked: true,
              title: {
                display: true,
                text: 'Condição Climática'
              }
            }
          },
          plugins: { legend: { position: 'top' } }
        }
      });
    },

    updateAllCharts() {
      if (this.loading || !this.chartAcidentesPorHora) {
        return;
      }
      this.updateGraficoAcidentesPorVeiculo();
      this.updateGraficoAcidentesPorHora();
      this.updateGraficoVitimasFaixaEtaria();
      this.updateGraficoAcidentesPorVia();
      this.updateGraficoImpactoChuva();
    },

    updateGraficoAcidentesPorVeiculo() {
      if (!this.chartAcidentesPorVeiculo) return;

      const labels = ['Bicicleta', 'Caminhão', 'Motocicleta', 'Ônibus', 'Automóvel', 'Outros'];
      const keys = [
        'tp_veiculo_bicicleta',
        'tp_veiculo_caminhao',
        'tp_veiculo_motocicleta',
        'tp_veiculo_onibus',
        'tp_veiculo_automovel',
        'tp_veiculo_outros'
      ];

      const counts = {
        'tp_veiculo_bicicleta': 0,
        'tp_veiculo_caminhao': 0,
        'tp_veiculo_motocicleta': 0,
        'tp_veiculo_onibus': 0,
        'tp_veiculo_automovel': 0,
        'tp_veiculo_outros': 0
      };

      // Itera em cada acidente filtrado
      for (const acidente of this.filteredAcidentes) {
        // Para cada tipo de veículo, verifica se ele esteve envolvido
        for (const key of keys) {
          if (acidente[key] > 0) {
            counts[key]++; // Incrementa o contador de acidentes para aquele tipo
          }
        }
      }

      const data = keys.map(key => counts[key]);

      this.chartAcidentesPorVeiculo.data.labels = labels;
      this.chartAcidentesPorVeiculo.data.datasets = [{
        label: 'Número de Acidentes',
        data: data,
        backgroundColor: '#007bff'
      }];
      this.chartAcidentesPorVeiculo.update();
    },

    updateGraficoAcidentesPorHora() {
      if (!this.chartAcidentesPorHora) return;

      const countsPorHora = new Array(24).fill(0);
      for (const acidente of this.filteredAcidentes) {
        const hora = parseInt(acidente.hora_sinistro, 10);
        if (hora >= 0 && hora <= 23) {
          countsPorHora[hora]++;
        }
      }

      this.chartAcidentesPorHora.data.labels = Array.from({ length: 24 }, (_, i) => `${i}h`);
      this.chartAcidentesPorHora.data.datasets = [{
        label: 'Total de Acidentes por Hora',
        data: countsPorHora,
        backgroundColor: '#28a745'
      }];
      this.chartAcidentesPorHora.update();
    },

    updateGraficoVitimasFaixaEtaria() {
      if (!this.chartVitimasFaixaEtaria) return;

      const faixasEtariasOrdenadas = [...new Set(this.allVitimas.map(v => v.faixa_etaria_demografica))]
        .filter(Boolean)
        .filter(faixa => faixa !== 'NAO DISPONIVEL')
        .sort((a, b) => {
          const numA = parseInt(a.split(' ')[0], 10);
          const numB = parseInt(b.split(' ')[0], 10);
          if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
          if (a.startsWith('Mais de')) return 1;
          if (b.startsWith('Mais de')) return -1;
          return a.localeCompare(b);
        });

      const gravidades = ['FATAL', 'GRAVE', 'LEVE'];
      const colors = {
        'FATAL': '#dc3545',
        'GRAVE': '#ffc107',
        'LEVE': '#17a2b8',
      };

      const counts = this.filteredVitimas.reduce((acc, vitima) => {
        const faixa = vitima.faixa_etaria_demografica;
        const grav = vitima.gravidade_lesao;
        if (!acc[grav]) acc[grav] = {};
        acc[grav][faixa] = (acc[grav][faixa] || 0) + 1;
        return acc;
      }, {});

      const datasets = [];
      for (const gravidade of gravidades) {
        if (counts[gravidade]) {
          datasets.push({
            label: gravidade,
            data: faixasEtariasOrdenadas.map(faixa => counts[gravidade][faixa] || 0),
            backgroundColor: colors[gravidade]
          });
        }
      }

      this.chartVitimasFaixaEtaria.data.labels = faixasEtariasOrdenadas;
      this.chartVitimasFaixaEtaria.data.datasets = datasets;
      this.chartVitimasFaixaEtaria.update();
    },

    updateGraficoAcidentesPorVia() {
      if (!this.chartAcidentesPorVia) return;
      
      const counts = this.filteredAcidentes.reduce((acc, acidente) => {
        const tipoVia = acidente.tipo_via || 'NAO DISPONIVEL';
        acc[tipoVia] = (acc[tipoVia] || 0) + 1;
        return acc;
      }, {});

      if (counts['NAO DISPONIVEL']) {
        delete counts['NAO DISPONIVEL'];
      }

      const labels = Object.keys(counts);
      const data = Object.values(counts);

      this.chartAcidentesPorVia.data.labels = labels;
      this.chartAcidentesPorVia.data.datasets = [{
        label: 'Número de Acidentes',
        data: data,
        backgroundColor: '#007bff'
      }];
      this.chartAcidentesPorVia.update();
    },

    updateGraficoImpactoChuva() {
      if (!this.chartImpactoChuva) return;

      // Define a ordem correta das chuvas no eixo X
      const labelsChuva = ['Sem chuva', 'Chuva fraca', 'Chuva moderada', 'Chuva forte'];
      const gravidades = ['FATAL', 'GRAVE', 'LEVE'];
      const colors = {
        'FATAL': '#dc3545',
        'GRAVE': '#ffc107',
        'LEVE': '#17a2b8',
      };

      // Conta as vítimas
      const counts = this.filteredVitimas.reduce((acc, vitima) => {
        const chuva = vitima.Chuva;
        const grav = vitima.gravidade_lesao;

        if (gravidades.includes(grav)) {
          if (!acc[grav]) acc[grav] = {};
          acc[grav][chuva] = (acc[grav][chuva] || 0) + 1;
        }
        return acc;
      }, {});

      // Monta os datasets para o Chart.js
      const datasets = [];
      for (const gravidade of gravidades) {
        if (counts[gravidade]) {
          datasets.push({
            label: gravidade,
            // Mapeia os dados na ordem correta dos labels
            data: labelsChuva.map(chuva => counts[gravidade][chuva] || 0),
            backgroundColor: colors[gravidade]
          });
        }
      }

      this.chartImpactoChuva.data.labels = labelsChuva;
      this.chartImpactoChuva.data.datasets = datasets;
      this.chartImpactoChuva.update();
    }

  },
};

</script>

<style>
.graficos-container {
  padding: 20px;
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  max-width: 1200px;
  margin: 0 auto;
}

.graficos-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.grafico-secao {
  margin-bottom: 0;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.loading-aviso {
  text-align: center;
  font-size: 1.2em;
  padding: 40px;
  color: #555;
}

.filtros-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 15px;
  padding: 15px;
  background-color: #e9ecef;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filtro {
  display: flex;
  flex-direction: column;
}

.filtro label {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 0.9em;
  color: #343a40;
}

.filtro select,
.filtro input[type="date"] {
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1em;
}
</style>