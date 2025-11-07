<template>
  <div class="map-container">
    
    <div class="map-filters-overlay">
      
      <div class="filtro-grupo">
        <strong>Período de Análise</strong>
        <div class="filtro-item">
          <label for="map-data-inicio">De:</label>
          <input type="date" id="map-data-inicio" v-model="filtroDataInicio" :min="minData" :max="maxData">
        </div>
        <div class="filtro-item">
          <label for="map-data-fim">Até:</label>
          <input type="date" id="map-data-fim" v-model="filtroDataFim" :min="minData" :max="maxData">
        </div>
      </div>
      
      <div class="filtro-grupo">
        <strong>Tipo de Visualização</strong>
        <div class="filtro-item-radio">
          <input type="radio" id="view-cluster" value="cluster" v-model="viewMode">
          <label for="view-cluster">Agrupado (Cluster)</label>
        </div>
        <div class="filtro-item-radio">
          <input type="radio" id="view-heatmap" value="heatmap" v-model="viewMode">
          <label for="view-heatmap">Mapa de Calor</label>
        </div>
      </div>
      
      <div v-if="loading" class="filtro-loading">
        Carregando dados...
      </div>
    </div>

    <div id="map" style="height: 100vh; width: 100%;"></div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Supercluster from 'supercluster';
import { point } from '@turf/helpers';
import "leaflet.heat"; 

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

export default {
  name: 'MapaBauru',
  data() {
    return {
      map: null,
      allPontosAcidentes: [], 
      loading: true,
      
      // Filtros
      viewMode: 'cluster',
      filtroDataInicio: '',
      filtroDataFim: '',
      minData: '',
      maxData: '',

      // Camadas do Mapa
      markersLayer: L.layerGroup(), 
      heatmapLayer: null,
      
      // Índices
      clusterIndex: null,
    };
  },

  created() {
    this.clusterIndex = new Supercluster({
      radius: 60, 
      maxZoom: 16, 
      map: (props) => ({ ...props }),
      
      // Corrige o aviso do ESLint sobre variáveis não utilizadas
      reduce: (/* eslint-disable no-unused-vars */ accumulated, props /* eslint-enable no-unused-vars */) => {

      }
    });
  },


  computed: {
    filteredPontos() {
      if (!this.filtroDataInicio || !this.filtroDataFim) {
        return this.allPontosAcidentes;
      }
      
      const inicio = new Date(this.filtroDataInicio + "T00:00:00");
      const fim = new Date(this.filtroDataFim + "T23:59:59");
      
      return this.allPontosAcidentes.filter(ponto => {
         const dataPonto = new Date(ponto.data_sinistro);
         return dataPonto >= inicio && dataPonto <= fim;
      });
    }
  },


  watch: {
    filteredPontos(novosPontos) {
      if (this.map) {
        this.buildDataLayers(novosPontos);
      }
    },
    
    viewMode() {
      if (this.map) {
        this.displayActiveLayer();
      }
    }
  },

  mounted() {
    this.initMap();
    this.loadData();
  },

  methods: {
    initMap() {
      this.map = L.map('map').setView([-22.3145, -49.0586], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(this.map);
      
      this.markersLayer.addTo(this.map);

      // Evento de 'moveend' (zoom ou arrastar)
      this.map.on('moveend', () => {
        if (this.viewMode === 'cluster') {
          this.updateMarkers();
        }
      });
    },

    loadData() {
      this.loading = true;
      fetch('/coordenadas.json') 
        .then(res => res.json())
        .then(dados => {
          
          const pontosValidos = [];
          for (const d of dados) {
            const lat = parseFloat(d.latitude);
            const lon = parseFloat(d.longitude);
            const latValida = !isNaN(lat) && lat >= -90 && lat <= 90;
            const lonValida = !isNaN(lon) && lon >= -180 && lon <= 180;
            
            if (d.data_sinistro && latValida && lonValida) {
              pontosValidos.push({
                data_sinistro: d.data_sinistro,
                latitude: lat, 
                longitude: lon
              });
            } 
          }
          
          this.allPontosAcidentes = pontosValidos;
          console.log(`Dados brutos: ${dados.length}, Pontos válidos: ${this.allPontosAcidentes.length}`);
          
          this.setupFiltrosDatas();
          this.loading = false;
          
        }).catch(error => {
          console.error("Erro ao carregar coordenadas.json:", error);
          this.loading = false;
        });
    },

    setupFiltrosDatas() {
      if (this.allPontosAcidentes.length === 0) return;

      const sorted = [...this.allPontosAcidentes].sort((a, b) => new Date(a.data_sinistro) - new Date(b.data_sinistro));
      
      const min = sorted[0].data_sinistro.split('T')[0];
      const max = sorted[sorted.length - 1].data_sinistro.split('T')[0];

      this.minData = min;
      this.maxData = max;
      this.filtroDataInicio = min;
      this.filtroDataFim = max;
    },

    buildDataLayers(pontos) {
      if (!this.map || !pontos) return;

      // 1. Constrói o índice do Cluster
      const features = pontos.map(ponto => {
        return point([ponto.longitude, ponto.latitude], {
          data_sinistro: ponto.data_sinistro 
        });
      });
      this.clusterIndex.load(features);

      // 2. Constrói a camada do Heatmap
      const heatPoints = pontos.map(p => [p.latitude, p.longitude, 0.5]); 
      
      if (this.heatmapLayer && this.map.hasLayer(this.heatmapLayer)) {
        this.map.removeLayer(this.heatmapLayer);
      }
      
      // SOLUÇÃO OPACIDADE
      this.heatmapLayer = L.heatLayer(heatPoints, {
        radius: 20,
        blur: 15,
        maxZoom: 17,
        maxOpacity: 0.4, // 60% opaco
        minOpacity: 0.0, 
        gradient: { 0.4: 'blue', 0.65: 'lime', 0.9: 'red' } 
      });

      // 3. Exibe a camada correta (cluster ou heatmap)
      this.displayActiveLayer();
    },

    displayActiveLayer() {
      this.markersLayer.clearLayers();
      if (this.heatmapLayer && this.map.hasLayer(this.heatmapLayer)) {
        this.map.removeLayer(this.heatmapLayer);
      }

      if (this.viewMode === 'cluster') {
        this.updateMarkers();
      } else if (this.viewMode === 'heatmap') {
        this.map.addLayer(this.heatmapLayer);
      }
    },

    updateMarkers() {
      if (!this.clusterIndex || !this.map) return; 

      this.markersLayer.clearLayers();
      const bounds = this.map.getBounds();
      const zoom = this.map.getZoom();
      
      const clusters = this.clusterIndex.getClusters([
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth()
      ], zoom);

      for (const feature of clusters) {
        const [longitude, latitude] = feature.geometry.coordinates;
        const props = feature.properties;
        
        let marker;
        let count;
        const isCluster = props && props.cluster;

        if (isCluster) {
          // É um cluster (count >= 2)
          count = props.point_count;
        } else {
          // É um ponto individual (count = 1)
          count = 1;
        }

        // 1. Criar o ícone de cluster para TODOS (seja 1 ou 50)
        const icon = this.createClusterIcon(count);
        marker = L.marker([latitude, longitude], { icon: icon });

        // 2. Adicionar lógica de clique SOMENTE se for um cluster real (count > 1)
        if (isCluster) {
          marker.on('click', () => {
            const expansionZoom = this.clusterIndex.getClusterExpansionZoom(feature.id);
            this.map.setView([latitude, longitude], expansionZoom);
          });
        }
        // Se for count = 1, ele será apenas um ícone de círculo sem ação de clique.
        
        this.markersLayer.addLayer(marker);
      }
    },

    createClusterIcon(count) {
      let sizeClass = 'small';
      if (count >= 10) sizeClass = 'medium'; // Mudado de > 100
      if (count >= 100) sizeClass = 'large';  // Mudado de > 500
      
      const className = `marker-cluster marker-cluster-${sizeClass}`;
      
      return L.divIcon({
        html: `<div><span>${count}</span></div>`,
        className: className,
        iconSize: L.point(40, 40)
      });
    }
  }
}
</script>

<style>
.map-container {
  position: relative;
  width: 100%;
  height: 100vh;
}
#map {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 0;
}
.map-filters-overlay {
  position: absolute;
  top: 10px;
  left: 50px; /* Padrão do Leaflet para controles */
  z-index: 1000; /* Acima do mapa */
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid #ccc;
  border-radius: 8px;
  padding: 10px;
  font-family: Arial, sans-serif;
  box-shadow: 0 1px 5px rgba(0,0,0,0.4);
}
.filtro-grupo {
  margin-bottom: 10px;
}
.filtro-grupo strong {
  display: block;
  margin-bottom: 5px;
  font-size: 1.1em;
}
.filtro-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
.filtro-item label {
  margin-right: 10px;
}
.filtro-item input[type="date"] {
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.filtro-item-radio {
  margin-top: 5px;
}
.filtro-item-radio label {
  margin-left: 5px;
}
.filtro-loading {
  font-style: italic;
  color: #555;
}

.marker-cluster {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  font-weight: bold;
  font-family: "Helvetica Neue", Arial, Helvetica, sans-serif;
  color: #000;
  width: 40px;
  height: 40px;
  cursor: pointer; /* Indica que é clicável */
}
.marker-cluster div {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
}
.marker-cluster span {
  line-height: 1;
}

.marker-cluster-small {
  background-color: rgba(253, 231, 37, 0.7); /* Amarelo */
}
.marker-cluster-small div {
  background-color: rgba(253, 231, 37, 0.8);
}
.marker-cluster-medium {
  background-color: rgba(240, 89, 34, 0.7); /* Laranja */
}
.marker-cluster-medium div {
  background-color: rgba(240, 89, 34, 0.8);
}
.marker-cluster-large {
  background-color: rgba(189, 0, 38, 0.7); /* Vermelho */
}
.marker-cluster-large div {
  background-color: rgba(189, 0, 38, 0.8);
}
</style>